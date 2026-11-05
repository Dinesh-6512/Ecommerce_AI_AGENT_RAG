# UI/UX Specification

A clean, minimalist user interface with standard top navigation (links to Products, Cart, My Orders, Chat / Shop Assistant, Login/Register or Logout, and Add Product for Admin).

---

## 1. Account Screens

### Register
- **What the user sees:** Form with Email and Password fields, "Register" button, and a link to the Login page.
- **What the user can do:** Enter credentials and submit the form to create an account.
- **Where the user goes next:** On success, redirected to the Login screen.

### Login
- **What the user sees:** Form with Email and Password fields, "Login" button, and a link to Register.
- **What the user can do:** Enter credentials and log in.
- **Where the user goes next:** On success, saves token (and admin flag) and redirects to Home / Product list.

---

## 2. User Screens

### Home / Product List
- **What the user sees:** Grid of product cards displaying title, description, price, and an "Add to Cart" button on each card.
- **What the user can do:** Browse items and click "Add to Cart" to add an item to their cart.
- **Where the user goes next:** Stays on the page with visual feedback ("Added to cart"), or clicks the top nav to visit Cart or My Orders.

### Cart
- **What the user sees:** Table/list of cart items showing item title, price, quantity, calculated subtotal per item, overall total, and a "Proceed to Checkout" button.
- **What the user can do:** Review selected items and order total.
- **Where the user goes next:** Clicks "Proceed to Checkout" to go to the Checkout screen.

### Checkout
- **What the user sees:** Delivery details form (Full Name, Phone, Address, City, Postal Code), an order summary with total amount, and a "Place Order" button.
- **What the user can do:** Fill in required delivery fields and click "Place Order".
- **Where the user goes next:** On submit, displays a brief success confirmation message and automatically navigates to My Orders.

### My Orders
- **What the user sees:** Chronological list of placed orders. Each order card shows order date, status (e.g., Pending), total price, delivery information, and line items with quantities and prices.
- **What the user can do:** Review past orders and order details.
- **Where the user goes next:** Can use navigation to return to Product List or Cart.

---

## 3. Admin Screens

### Add Product (Admin Only)
- **What the user sees:** Product creation form with Title, Description, and Price fields, plus a "Create Product" button.
- **What the user can do:** Enter product details and submit.
- **Where the user goes next:** On success, shows a success notice and redirects to Home / Product list where the new item is visible.

---

## 4. Shop Assistant (Chat Page)

### Layout & Elements
- **Navigation:** Accessible via a "Chat" link in the top menu bar.
- **Chat Container:** Centered conversation panel styled consistently with existing cards, displaying alternating user and assistant message bubbles.
- **Input Area:** Bottom sticky message box with a text input (`Ask a question about products, your cart, or orders...`) and a "Send" button.
- **Loading State:** Displays an inline indicator (`Shop Assistant is thinking...`) while waiting for the AI response.

### Response Behaviors
- **No Data Found:** `I couldn't find any products or records matching your request in the store.`
- **Unclear Question:** `Could you please clarify your question? Please mention the specific product, cart item, or order you are asking about.`
- **Refused Question (Off-topic / Out-of-bounds):** `I can only assist with SimpleShop products, your cart, and your order history. To place an order, please visit the Checkout page.`
- **Error State:** `Sorry, I was unable to complete your request. Please try again in a moment.`

---

## 5. Product Manuals in Chat (Module 3)

### Seamless Experience (No Mode Switching)
- Users interact within the exact same chat interface. No toggle or separate page is needed: the assistant automatically identifies questions about manuals (usage, troubleshooting, warranty).

### Manual Answer Presentation
- **Answer Text:** Direct, grounded answers extracted strictly from official documentation.
- **Source Citation Badge:** Every manual answer card displays a dedicated sources footer:
  - **Manual Name:** e.g., `Classic White T-Shirt Manual`
  - **Section:** e.g., `How to Use` or `Troubleshooting`
  - **Download Link:** A clean, clickable `Download Manual (PDF)` link pointing directly to `/manuals/<file_name>.pdf`.

### Download Manuals Shelf
- A compact, collapsible or dedicated sub-bar on the chat page listing available PDF manuals so users can download any manual directly at any time.

### RAG Response States
- **No Information Found:** `This information was not found in the product manuals.`
- **Unclear Question:** `Could you please clarify which product manual or section (How to Use, Troubleshooting, Warranty) you are inquiring about?`
- **Error State:** `Sorry, I was unable to search the product manuals at this time. Please try again shortly.`
