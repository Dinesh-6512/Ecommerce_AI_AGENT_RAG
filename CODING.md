# Backend Code Overview

This document describes the backend structure and the responsibility of each file.

## File Structure & Responsibilities

- **`backend/.env`**
  Contains configuration and secret settings: `DATABASE_URL` (Neon PostgreSQL connection string), `SECRET_KEY` (JWT signature key), `CORS_ORIGINS` (allowed frontend client addresses), `GROQ_API_KEY` / `GROQ_MODEL` (Groq AI model configuration), and `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` (Langfuse observability configuration).

- **`backend/requirements.txt`**
  Lists required Python packages: FastAPI, Uvicorn, SQLAlchemy, Psycopg 3, Pydantic, Email-Validator, Python-Dotenv, Python-Multipart, PyJWT, Bcrypt, LangChain-Groq, LangGraph, LangChain-Core, Langfuse, ReportLab, ChromaDB, and PyPDF.

- **`backend/database.py`**
  Sets up the SQLAlchemy engine with PostgreSQL/Neon, sessionmaker, base declarative class, and the `get_db` session dependency.

- **`backend/models.py`**
  Defines the 6 SQLAlchemy database models: `User`, `Product`, `Cart`, `CartItem`, `Order`, and `OrderItem`.

- **`backend/schemas.py`**
  Defines Pydantic models for request validation and response formatting:
  - Auth: `UserRegister`, `UserLogin`, `TokenResponse`, `UserResponse`
  - Products: `ProductCreate`, `ProductResponse`
  - Cart: `CartItemAdd`, `CartItemResponse`, `CartResponse`
  - Orders: `OrderCreate`, `OrderItemResponse`, `OrderResponse`
  - Chat: `ChatRequest`, `ChatSource`, `ChatResponse` (with answer and sources)

- **`backend/auth.py`**
  Handles password hashing and verification using `bcrypt`, JWT token generation and decoding using `pyjwt`, and authentication dependencies (`get_current_user`, `get_current_admin`) supporting OpenAPI Bearer auth.

- **`backend/main.py`**
  Application entry point. Initializes FastAPI, configures CORS middleware, executes startup table creation, database seeding (initial admin and 5 sample products), Langfuse connection check, and defines all API routes:
  - System: `GET /health`
  - Auth: `POST /api/register`, `POST /api/login`, `GET /api/me`
  - Products: `GET /api/products`, `POST /api/products` (Admin only)
  - Cart: `POST /api/cart`, `GET /api/cart`
  - Orders: `POST /api/orders` (Atomic transaction: creates order, reduces stock, clears cart), `GET /api/orders`
  - Chat Assistant: `POST /api/chat` (Protected chat endpoint using LangGraph multi-agent system returning answers and manual sources)

- **`backend/ai_agent/llm.py`**
  Configures the Groq Chat model (`ChatGroq`) with `llm_temperature = 0`, reading credentials and model identifier from `backend/.env`.

- **`backend/ai_agent/state.py`**
  Defines the shared `AgentState` TypedDict ensuring all agent data is structured as dictionary state with strict inputs (`user_id`, `role`, `request_id`, `question`) and outputs (`final_answer`, `sources`).

- **`backend/ai_agent/orchestrator.py`**
  Coordinates question classification using Groq LLM across 5 destinations: Product Manuals (RAG), Product Search, Cart, Order, or fallback nodes. Traced via `@observe(name="shop-assistant-agent")` and scored with `answer_found` (1 or 0).

- **`backend/ai_agent/product_agent.py`**
  Queries the database in read-only mode to answer product availability, price, and stock inquiries.

- **`backend/ai_agent/cart_agent.py`**
  Displays the authenticated user's cart or adds products adhering strictly to the `max_stock_rule`.

- **`backend/ai_agent/order_agent.py`**
  Provides read-only access to the authenticated user's order history and guides users to the Checkout page to place orders.

- **`backend/ai_agent/langfuse_client.py`**
  Handles Langfuse v3 connection testing (`auth_check`), LangChain callback handler creation, trace updates (`user_id`, `role`), trace scoring (`answer_found`), and trace flushing with resilient error handling.

- **`backend/rag/create_manuals.py`**
  Script using ReportLab to generate 5 synthetic PDF product manuals in `frontend/public/manuals/` with required headings: How to Use, Troubleshooting, and Warranty.

- **`backend/rag/build_knowledge_base.py`**
  Script to ingest PDF manuals, clean text, partition into heading-based chunks with metadata, persist into Chroma DB (`backend/rag/chroma_db`), and verify with a sample query.

- **`backend/rag/rag_flow.py`**
  Agentic RAG pipeline executing relevance check, query reformulation, Chroma DB semantic search, usefulness evaluation with retry loop, and strictly grounded answer generation with source citation.
