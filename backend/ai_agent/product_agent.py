from langchain_core.messages import SystemMessage, HumanMessage
from backend.database import SessionLocal
from backend.models import Product
from backend.ai_agent.llm import get_llm
from backend.ai_agent.state import AgentState

def product_agent_node(state: AgentState) -> dict:
    question = state["question"]
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            return {"final_answer": "There are currently no products available in the shop."}

        catalog_lines = [
            f"- ID: {p.id} | Name: {p.name} | Description: {p.description or 'N/A'} | Price: ${p.price:.2f} | Stock: {p.stock}"
            for p in products
        ]
        catalog_text = "\n".join(catalog_lines)

        system_prompt = (
            "You are the Product Search Assistant for SimpleShop.\n"
            "Answer user questions accurately regarding product availability, descriptions, pricing, and stock.\n"
            "STRICT RULES:\n"
            "- Rely ONLY on the product catalog provided below.\n"
            "- Never invent products, specs, prices, or stock numbers.\n"
            "- If no product in the catalog matches the user's request, reply exactly: "
            "'I couldn't find any products matching that in our shop.'\n\n"
            f"Product Catalog:\n{catalog_text}"
        )

        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=question),
        ])
        return {"final_answer": response.content.strip()}
    except Exception:
        return {"final_answer": "I'm having trouble checking the product catalog right now. Please try again shortly."}
    finally:
        db.close()
