# Architecture & System Design

## 1. System Flow
```
ReactJS Website (Frontend)  --->  FastAPI Server (Backend)  --->  Neon PostgreSQL (Cloud DB)
                                           │
                                           ▼
                               Chroma DB (Product Manuals Vector DB)
```
- **Frontend:** Renders UI, stores auth token and `is_admin` in browser localStorage, and calls backend endpoints with `Authorization: Bearer <token>`. Directly serves static PDF manuals from `frontend/public/manuals/`.
- **Backend:** Checks authentication via JWT tokens, handles business logic (products, cart, orders, chat assistant), executes database operations on Neon, and queries Chroma DB for manual document retrieval.
- **Database:** Neon PostgreSQL manages persistent relational data across 6 tables; Chroma DB stores embedded manual chunks for local semantic vector search.

---

## 2. Database Tables (6 Tables)
1. **users:** `id`, `name`, `email`, `hashed_password`, `is_admin`, `created_at`
2. **products:** `id`, `name`, `description`, `price`, `stock`, `created_at`
3. **cart:** `id`, `user_id`, `created_at`
4. **cart_items:** `id`, `cart_id`, `product_id`, `quantity`
5. **orders:** `id`, `user_id`, `total_amount`, `status`, `full_name`, `phone`, `address`, `city`, `postal_code`, `created_at`
6. **order_items:** `id`, `order_id`, `product_id`, `quantity`, `price`

---

## 3. Core Business Operations
- **Authentication:** Password hashing via bcrypt, stateless JWT token validation. Admin status verified for protected endpoints.
- **Place Order (Atomic Transaction):** Reads user's active cart, verifies and reduces product stock, saves order header with delivery details, saves line items to `order_items`, and empties the cart—all in a single database transaction.

---

## 4. Shop Assistant (AI Multi-Agent Architecture)

### Request Journey
```
Chat Page (ReactJS)
       │
       ▼
POST /api/chat (FastAPI)
       │
       ▼
Orchestrator Agent (LangGraph + Groq LLM)
       │
       ├───────────────────┼───────────────────┬─────────────────────┐
       ▼                   ▼                   ▼                     ▼
Product Search Agent   Cart Agent         Order Agent        Product Manuals Agent
(Read-only catalog)    (User's cart only) (User's orders)    (RAG semantic search)
       │                   │                   │                     │
       └───────────────────┼───────────────────┘                     ▼
                           ▼                                    Chroma DB
                 Neon PostgreSQL Database                       (Manual Chunks)
                           │                                         │
                           └─────────────────┬───────────────────────┘
                                             ▼
                          Answer Returned (+ Sources if Manual)
```

### Agent Data Access Boundaries
- **Orchestrator:** Coordinates routing using Groq LLM (`temperature = 0`). Receives strictly `{ "user_id", "role", "request_id", "question" }`. Never reads databases directly.
- **Product Search Agent:** Read-only access to the `products` table (name, description, price, stock).
- **Cart Agent:** Read/write access restricted strictly to the calling user's own `cart` and `cart_items`. Additions strictly observe `max_stock_rule`.
- **Order Agent:** Read-only access restricted strictly to the calling user's own `orders` and `order_items`. Never places orders (directs users to Checkout).
- **Product Manuals Agent:** Performs Agentic RAG semantic search over Chroma DB (`collection_name = product_manuals`, top_k=4, max_searches=2) to ground usage, troubleshooting, and warranty responses.

---

## 5. Product Manuals RAG Architecture (Module 3)

### 1. Ingestion Pipeline (Preparation)
```
PDF Manuals (5 synthetic PDFs) 
       │
       ▼
Section Extractor (Headings: How to Use, Troubleshooting, Warranty)
       │
       ▼
Chunker (Chunk by headings, size: 500 chars, overlap: 50 chars)
Format: "Product: <name> | Section: <section>\n<text>"
       │
       ▼
Embedding Model (all-MiniLM-L6-v2) ---> Stored in Chroma DB (backend/rag/chroma_db)
```

### 2. Query Pipeline (Answering)
- **Question Evaluation:** Orchestrator routes manual-related queries to the Product Manuals Agent.
- **Search & Verification:** Generates search query &rarr; searches Chroma DB (`top_k=4`) &rarr; checks if retrieved chunks sufficiently answer the query (retries search once if insufficient, `max_searches=2`).
- **Grounded Response:** Synthesizes answer strictly from verified manual chunks with citation metadata (`manual_name`, `section`, `download_link`). If not found, answers: `"not found in the manuals"`.

### 3. Static Manual Downloads
- All 5 PDF files are statically served from `frontend/public/manuals/`.
- Download links point to `/manuals/<file_name>.pdf` as direct static assets requiring no backend API.

---

## 6. API List
- `GET /health`
- `POST /api/register` - name, email, password
- `POST /api/login` - email, password; returns access_token and is_admin
- `GET /api/products`
- `POST /api/products` (admin only) - name, description, price, stock
- `POST /api/cart` - product_id, quantity
- `GET /api/cart` - items and total
- `POST /api/orders` - full_name, phone, address, city, postal_code
- `GET /api/orders` - the user's own orders, newest first
- `POST /api/chat` (logged-in users only) - question; returns answer and optional sources (`manual_name`, `section`, `download_link`)
- `Errors:` `{"detail": "short message"}`
*(Note: There are no admin order APIs)*
