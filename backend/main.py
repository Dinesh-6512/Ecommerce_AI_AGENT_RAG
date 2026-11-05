import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db, SessionLocal
from backend.models import Product, User, Cart, CartItem, Order, OrderItem
from backend.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    ProductCreate,
    ProductResponse,
    CartItemAdd,
    CartItemResponse,
    CartResponse,
    OrderCreate,
    OrderResponse,
    ChatRequest,
    ChatResponse,
)
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin,
)
from backend.ai_agent.orchestrator import run_shop_assistant
from backend.ai_agent.langfuse_client import check_langfuse_connection

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in CORS_ORIGINS_RAW.split(",") if origin.strip()]

def seed_initial_data():
    db = SessionLocal()
    try:
        # Seed default admin user if no admin exists
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            admin = User(
                name="Admin User",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                is_admin=True,
            )
            db.add(admin)
            db.commit()

        # Seed sample products if empty (5 products)
        if db.query(Product).count() == 0:
            sample_products = [
                Product(
                    name="Classic White T-Shirt",
                    description="100% cotton premium basic t-shirt",
                    price=19.99,
                    stock=50,
                ),
                Product(
                    name="Wireless Bluetooth Headphones",
                    description="Noise-cancelling over-ear headphones with 20h battery life",
                    price=79.99,
                    stock=25,
                ),
                Product(
                    name="Stainless Steel Water Bottle",
                    description="Vacuum insulated 750ml reusable bottle",
                    price=14.50,
                    stock=40,
                ),
                Product(
                    name="Canvas Everyday Backpack",
                    description="Durable canvas backpack with dedicated 15-inch laptop sleeve",
                    price=45.00,
                    stock=15,
                ),
                Product(
                    name="Ceramic Coffee Mug",
                    description="Durable 350ml ceramic coffee mug with ergonomic handle",
                    price=12.00,
                    stock=30,
                ),
            ]
            db.add_all(sample_products)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    # Seed admin and products if empty
    seed_initial_data()
    # Check Langfuse connection at start
    check_langfuse_connection()
    yield

app = FastAPI(
    title="E-Commerce API",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def build_cart_response(cart: Cart) -> CartResponse:
    items = []
    total = 0.0
    for item in cart.items:
        subtotal = round(item.quantity * item.product.price, 2)
        total += subtotal
        items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )
    return CartResponse(items=items, total=round(total, 2))

# --- System & Auth Endpoints ---

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"detail": "User registered successfully", "id": new_user.id, "email": new_user.email}

@app.post("/api/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin}
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        is_admin=user.is_admin,
    )

@app.get("/api/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Product Endpoints ---

@app.get("/api/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.asc()).all()

@app.post("/api/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# --- Cart Endpoints ---

@app.post("/api/cart", response_model=CartResponse)
def add_to_cart(
    item_in: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if item_in.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1",
        )

    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_in.product_id,
    ).first()

    current_qty_in_cart = cart_item.quantity if cart_item else 0
    if current_qty_in_cart + item_in.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity exceeds available stock",
        )

    if cart_item:
        cart_item.quantity += item_in.quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=item_in.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart)
    return build_cart_response(cart)

@app.get("/api/cart", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return CartResponse(items=[], total=0.0)
    return build_cart_response(cart)

# --- Order Endpoints ---

@app.post("/api/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    try:
        for item in cart.items:
            if item.quantity > item.product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for '{item.product.name}'",
                )

        total_amount = sum(item.quantity * item.product.price for item in cart.items)

        order = Order(
            user_id=current_user.id,
            total=round(total_amount, 2),
            status="Pending",
            full_name=order_in.full_name,
            phone=order_in.phone,
            address=order_in.address,
            city=order_in.city,
            postal_code=order_in.postal_code,
        )
        db.add(order)
        db.flush()

        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            db.add(order_item)
            item.product.stock -= item.quantity
            db.delete(item)

        db.commit()
        db.refresh(order)
        return order
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order: {str(e)}",
        )

@app.get("/api/orders", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

# --- Shop Assistant Chat Endpoint ---

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    clean_question = request.question.strip()
    if not clean_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty",
        )

    role = "admin" if current_user.is_admin else "user"
    res = run_shop_assistant(user_id=current_user.id, role=role, question=clean_question)
    return ChatResponse(
        answer=res.get("answer", ""),
        sources=res.get("sources", []),
    )
