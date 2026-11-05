import json
from langchain_core.messages import SystemMessage, HumanMessage
from backend.database import SessionLocal
from backend.models import Cart, CartItem, Product
from backend.ai_agent.llm import get_llm
from backend.ai_agent.state import AgentState

def cart_agent_node(state: AgentState) -> dict:
    user_id = state["user_id"]
    question = state["question"]

    db = SessionLocal()
    try:
        # Determine intent: view or add
        classifier_prompt = (
            "You are an intent classifier for a shopping cart assistant.\n"
            "Given the user question, identify if the user wants to 'add' an item to their cart, 'view' their cart, "
            "'remove' an item, or 'checkout'.\n"
            "Return ONLY a valid JSON object with:\n"
            '{"action": "add"|"view"|"remove"|"checkout", "product_query": "string or empty", "quantity": integer (default 1)}\n'
            "Example: 'Add 2 water bottles' -> {\"action\": \"add\", \"product_query\": \"water bottle\", \"quantity\": 2}\n"
            "Example: 'What is in my cart?' -> {\"action\": \"view\", \"product_query\": \"\", \"quantity\": 0}\n"
            "Output JSON only, no markdown, no explanation."
        )

        llm = get_llm()
        decision_msg = llm.invoke([
            SystemMessage(content=classifier_prompt),
            HumanMessage(content=question),
        ])

        try:
            cleaned = decision_msg.content.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)
        except Exception:
            parsed = {"action": "view"}

        action = parsed.get("action", "view")

        if action == "checkout":
            return {"final_answer": "I cannot place orders in chat. Please go to the Checkout page to complete your purchase."}

        if action == "remove":
            return {"final_answer": "Modifying or removing items directly in chat is not supported. Please visit your Cart page."}

        if action == "add":
            query = parsed.get("product_query", "").strip().lower()
            quantity = parsed.get("quantity", 1)
            if not isinstance(quantity, int) or quantity <= 0:
                quantity = 1

            # Match product from catalog
            all_products = db.query(Product).all()
            matched_product = None
            for p in all_products:
                if query and (query in p.name.lower() or p.name.lower() in query):
                    matched_product = p
                    break

            if not matched_product:
                return {"final_answer": f"I couldn't find any product matching '{query}' in our shop."}

            # Get user's cart
            cart = db.query(Cart).filter(Cart.user_id == user_id).first()
            if not cart:
                cart = Cart(user_id=user_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)

            # Check existing item in cart
            cart_item = db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id == matched_product.id,
            ).first()

            current_qty = cart_item.quantity if cart_item else 0
            new_qty = current_qty + quantity

            # max_stock_rule: a cart quantity can never be above the stock
            if new_qty > matched_product.stock:
                return {
                    "final_answer": (
                        f"Cannot add {quantity} item(s) of '{matched_product.name}'. "
                        f"You have {current_qty} in your cart, and only {matched_product.stock} are available in stock."
                    )
                }

            if cart_item:
                cart_item.quantity = new_qty
            else:
                cart_item = CartItem(cart_id=cart.id, product_id=matched_product.id, quantity=quantity)
                db.add(cart_item)

            db.commit()

            # Calculate total
            total = sum(item.quantity * item.product.price for item in cart.items)
            return {
                "final_answer": (
                    f"Added {quantity} x '{matched_product.name}' to your cart. "
                    f"You now have {new_qty} of this item in your cart. Current cart total: ${total:.2f}."
                )
            }

        # Default action: view cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart or not cart.items:
            return {"final_answer": "Your shopping cart is currently empty."}

        lines = []
        total = 0.0
        for item in cart.items:
            subtotal = item.quantity * item.product.price
            total += subtotal
            lines.append(f"- {item.product.name}: {item.quantity} x ${item.product.price:.2f} = ${subtotal:.2f}")

        summary = "\n".join(lines)
        return {"final_answer": f"Here is what is currently in your cart:\n{summary}\nTotal: ${total:.2f}"}

    except Exception:
        return {"final_answer": "Unable to access your cart right now. Please try again shortly."}
    finally:
        db.close()
