# Business Requirements Document (BRD)

## 1. Goal & Target Users
The goal is to build a simple, beginner-friendly e-commerce application allowing customers to browse products and place orders, while giving administrators the ability to catalog new items.

**User Roles:**
- **User (Customer):** Browses products, manages a shopping cart, and places orders with delivery details.
- **Admin:** Manages inventory additions.

---

## 2. Features

### User Features
- **Register:** Create an account using email and password.
- **Login:** Authenticate and obtain an access token.
- **View Products:** Browse the catalog of available products (title, description, price).
- **Add to Cart:** Add selected products to a personal shopping cart.
- **View Cart:** Review items and quantities currently in the cart.
- **Checkout:** Provide delivery details (full name, phone, address, city, postal code).
- **Place Order:** Submit the order using cart contents and delivery details (cash on delivery / offline fulfillment).
- **View My Orders:** View historical orders and their delivery details.

### Admin Features
- **Add Product:** Create a new product entry (title, description, price).

---

## 3. Scope Boundaries (Not Included)
To keep the application simple and focused, the following features are explicitly out of scope:
- Online payment gateways / card processing.
- Product search and filtering.
- Dedicated product details pages.
- Product categories and tags.
- Editing or deleting products.
- Removing items or adjusting quantities from the cart.
- Order cancellation.
- Admin order management dashboard.

---

## 4. Main User Journey
1. **User Flow:**
   `Register` &rarr; `Login` &rarr; `View Products` &rarr; `Add to Cart` &rarr; `View Cart` &rarr; `Checkout` &rarr; `Place Order` &rarr; `View My Orders`
2. **Admin Flow:**
   `Login` &rarr; `Add Product` &rarr; Product immediately appears in `View Products`.

---

## 5. Success Rules
- Users can successfully register, log in, and persist their session token.
- Only authenticated admins can access and submit the Add Product form.
- Products added by an admin are immediately visible to all users.
- A user can add items to cart, enter complete delivery details, and place an order.
- Placed orders reliably clear the active cart and appear under "View My Orders".

---

## 6. Shop Assistant (Module 2)

### The 4 Agents & Responsibilities
1. **Orchestrator:** Reads the user question, picks the right specialized agent, and returns the final answer (never queries the database directly).
2. **Product Search Agent:** Queries product catalog data to answer questions about products, descriptions, prices, and stock.
3. **Cart Agent:** Manages the logged-in user's own cart to display items/totals or add an item (never above available stock).
4. **Order Agent:** Reads the logged-in user's own orders and status (never places or modifies orders; directs users to the Checkout page).

### Allowed Operations
- Answering questions about product details, prices, and current stock.
- Viewing the authenticated user's own cart.
- Adding a product to the authenticated user's cart (capped at available inventory).
- Viewing the authenticated user's own placed orders and current order status.

### Not Allowed Operations
- Placing orders directly via chat (must guide user to the Checkout page).
- Modifying quantities, editing, or deleting items from the cart.
- Cancelling or modifying existing orders.
- Accessing or revealing any other user's cart, orders, or private information.
- Inventing nonexistent data or answering unrelated off-topic queries (politely refuse).

### User Flow
`Open Shop Assistant Chat` &rarr; `Ask Question` &rarr; `Receive Grounded Answer From Real Shop Data`

### Success Rules
- Orchestrator accurately routes to the right specialist agent without database access.
- User data isolation is strictly preserved (user ID checked on every cart/order call).
- Cart additions via chat respect the `max_stock_rule` (quantity never exceeds stock).
- When information is missing, agent says so; when ambiguous, asks user for clarification; when off-topic, politely declines.
- System secrets, internal errors, or stack traces are never exposed to the user.

---

## 7. Product Manuals Questions (Module 3 - Agentic RAG)

### Unified Chat Interface
The existing Shop Assistant chat remains the single interface for all interactions. In addition to general shop operations (catalog, cart, orders), it seamlessly handles product manual inquiries using a dedicated **Product Manuals Agent**.

### Scope of Manual Questions
- **How to Use:** Setup instructions, operational procedures, and usage guidelines.
- **Troubleshooting:** Diagnosing common operational issues and remedies.
- **Warranty:** Terms of warranty coverage, duration, and claim procedures.

### Source of Answers & Downloads
- Answers are grounded strictly in synthetic PDF manuals stored in `frontend/public/manuals/`.
- Every manual answer cites its specific source: the manual filename, relevant section heading, and a direct download link (`/manuals/<filename>`).

### User Flow
`Ask manual question in Chat` &rarr; `Assistant retrieves matching sections from Chroma DB` &rarr; `Grounded answer is displayed alongside source citations and PDF download link`.

### Guardrails & Strict Rules
- **Anti-Hallucination:** Answers must be formulated solely from retrieved manual text. If the information is not present after the allowed searches, the assistant must state: "Not found in the manuals."
- **Prompt Injection Defense:** Any instruction embedded in user queries or manual texts attempting to override safety or operating boundaries must be ignored.
- **Preservation of Existing Features:** Core shop inquiries (product catalog, personal cart, order status) remain completely unaffected and continue to execute through their existing specialized agents.

### Success Rules
- Manual-related questions are accurately identified and routed to the Product Manuals Agent.
- Source metadata (manual name, section, download link) is returned whenever a manual answer is provided.
- If information is not in the manuals, the agent states that it is not found rather than speculating.
- Existing shop capabilities (catalog queries, cart operations, order history) function identically with zero regression.
