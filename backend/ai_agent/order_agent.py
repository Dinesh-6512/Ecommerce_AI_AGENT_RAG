from backend.database import SessionLocal
from backend.models import Order
from backend.ai_agent.state import AgentState

def order_agent_node(state: AgentState) -> dict:
    user_id = state["user_id"]
    question = state["question"].lower()

    # If the user asks to place an order
    if any(phrase in question for phrase in ["place order", "place an order", "buy now", "checkout", "order now", "complete order"]):
        return {
            "final_answer": "I cannot place orders directly in chat. Please review your cart and proceed to the Checkout page to enter your delivery details and place your order."
        }

    # If the user asks to cancel or modify
    if any(phrase in question for phrase in ["cancel", "cancel order", "delete order", "change order"]):
        return {
            "final_answer": "Order cancellation and modification are not supported. Once an order is placed, it is processed for fulfillment."
        }

    db = SessionLocal()
    try:
        orders = (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

        if not orders:
            return {"final_answer": "You have not placed any orders yet."}

        lines = ["Here are your recent orders:"]
        for o in orders:
            order_date = (
                o.created_at.strftime("%b %d, %Y")
                if o.created_at
                else "Recent"
            )
            items_str = ", ".join(f"{item.product_name} x {item.quantity}" for item in o.items)
            lines.append(
                f"- Order #{o.id} ({order_date}): Status: {o.status} | Total: ${o.total:.2f} | Items: {items_str}"
            )

        return {"final_answer": "\n".join(lines)}
    except Exception:
        return {"final_answer": "Unable to retrieve your order history right now. Please try again shortly."}
    finally:
        db.close()
