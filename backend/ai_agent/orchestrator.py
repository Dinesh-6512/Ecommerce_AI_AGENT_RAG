import uuid
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from backend.ai_agent.llm import get_llm
from backend.ai_agent.state import AgentState
from backend.ai_agent.product_agent import product_agent_node
from backend.ai_agent.cart_agent import cart_agent_node
from backend.ai_agent.order_agent import order_agent_node
from backend.rag.rag_flow import run_rag_flow
from backend.ai_agent.langfuse_client import (
    get_langfuse_handler,
    update_trace_info,
    update_trace_manual_data,
    score_trace,
    flush_langfuse,
)

# Safe observe decorator from langfuse
try:
    from langfuse import observe
except Exception:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Handler for unclear questions
def unclear_node(state: AgentState) -> dict:
    return {
        "final_answer": "Could you please clarify your question? Let me know which product, cart item, order, or manual section you need help with.",
        "sources": [],
    }

# Handler for unrelated questions
def unrelated_node(state: AgentState) -> dict:
    return {
        "final_answer": "I'm sorry, but I can only assist with SimpleShop products, your cart, orders, and product manuals.",
        "sources": [],
    }

# Product Manuals Agent (Agentic RAG)
def product_manuals_node(state: AgentState) -> dict:
    question = state["question"]
    try:
        handler = get_langfuse_handler()
        config = {"callbacks": [handler]} if handler else None
        rag_result = run_rag_flow(question, config=config)

        # Update trace with search text, Chroma chunks, and tag with "manuals"
        search_query = rag_result.get("search_query", "")
        chunk_count = rag_result.get("chunk_count", 0)
        try:
            update_trace_manual_data(search_query=search_query, chunk_count=chunk_count, tags=["manuals"])
        except Exception:
            pass

        return {
            "final_answer": rag_result.get("answer", "not found in the manuals"),
            "sources": rag_result.get("sources", []),
        }
    except Exception:
        return {
            "final_answer": "The product manuals service is temporarily unavailable. Please try again shortly.",
            "sources": [],
        }

# Wrapped nodes ensuring sources field is always initialized
def wrapped_product_node(state: AgentState) -> dict:
    res = product_agent_node(state)
    res["sources"] = []
    return res

def wrapped_cart_node(state: AgentState) -> dict:
    res = cart_agent_node(state)
    res["sources"] = []
    return res

def wrapped_order_node(state: AgentState) -> dict:
    res = order_agent_node(state)
    res["sources"] = []
    return res

# Orchestrator routing node: NEVER reads the database
def orchestrator_node(state: AgentState) -> dict:
    question = state["question"]

    system_prompt = (
        "You are the Orchestrator for SimpleShop's AI assistant.\n"
        "Evaluate the user's question and choose the single best route:\n"
        "- 'manual': questions regarding product manuals, how to use, instructions, care/washing, troubleshooting, pairing, errors, or warranty coverage\n"
        "- 'product': general inquiries about store products, catalog, features, prices, or available stock\n"
        "- 'cart': inquiries about viewing the shopping cart or adding items to the cart\n"
        "- 'order': inquiries about past orders, order status, or ordering instructions\n"
        "- 'unclear': vague, incomplete, or ambiguous queries\n"
        "- 'unrelated': questions off-topic or unrelated to the store\n"
        "Respond with ONLY one word: manual, product, cart, order, unclear, or unrelated."
    )

    try:
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=question),
        ])
        route = response.content.strip().lower()
        if "manual" in route:
            selected_route = "manual"
        elif "product" in route:
            selected_route = "product"
        elif "cart" in route:
            selected_route = "cart"
        elif "order" in route:
            selected_route = "order"
        elif "unrelated" in route:
            selected_route = "unrelated"
        else:
            selected_route = "unclear"
    except Exception:
        selected_route = "unclear"

    return {"route": selected_route}

def route_condition(state: AgentState) -> str:
    route = state.get("route", "unclear")
    if route == "manual":
        return "manuals_agent"
    if route == "product":
        return "product_agent"
    if route == "cart":
        return "cart_agent"
    if route == "order":
        return "order_agent"
    if route == "unrelated":
        return "unrelated"
    return "unclear"

# Construct the LangGraph workflow
workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("manuals_agent", product_manuals_node)
workflow.add_node("product_agent", wrapped_product_node)
workflow.add_node("cart_agent", wrapped_cart_node)
workflow.add_node("order_agent", wrapped_order_node)
workflow.add_node("unclear", unclear_node)
workflow.add_node("unrelated", unrelated_node)

workflow.set_entry_point("orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    route_condition,
    {
        "manuals_agent": "manuals_agent",
        "product_agent": "product_agent",
        "cart_agent": "cart_agent",
        "order_agent": "order_agent",
        "unclear": "unclear",
        "unrelated": "unrelated",
    },
)

workflow.add_edge("manuals_agent", END)
workflow.add_edge("product_agent", END)
workflow.add_edge("cart_agent", END)
workflow.add_edge("order_agent", END)
workflow.add_edge("unclear", END)
workflow.add_edge("unrelated", END)

app_graph = workflow.compile()

def determine_score(route: str | None, answer: str) -> int:
    if route in ("unclear", "unrelated"):
        return 0

    lower_ans = answer.lower()
    negative_indicators = [
        "not found in the manuals",
        "couldn't find",
        "could not find",
        "no products available",
        "clarify your question",
        "only assist with simpleshop",
        "cannot place orders directly in chat",
        "order cancellation and modification are not supported",
        "temporarily unavailable",
        "unable to",
        "having trouble checking",
    ]
    if any(ind in lower_ans for ind in negative_indicators):
        return 0

    return 1

# Public runner function with Langfuse tracing
@observe(name="shop-assistant-agent")
def run_shop_assistant(user_id: int, role: str, question: str) -> dict:
    request_id = uuid.uuid4().hex[:8]

    # Strict agent input: user id, role, request id, question (nothing else)
    agent_input: AgentState = {
        "user_id": user_id,
        "role": role,
        "request_id": request_id,
        "question": question,
    }

    # Add user_id and role to trace
    try:
        update_trace_info(user_id=user_id, role=role, request_id=request_id)
    except Exception:
        pass

    handler = None
    try:
        handler = get_langfuse_handler()
    except Exception:
        pass

    config = {"callbacks": [handler]} if handler else {}

    try:
        result = app_graph.invoke(agent_input, config=config)
        answer = result.get("final_answer", "Sorry, I was unable to complete your request. Please try again.")
        sources = result.get("sources", [])
        route = result.get("route")

        # Tag manual questions with "manuals"
        if route == "manual":
            try:
                from langfuse import get_client
                get_client().update_current_trace(tags=["manuals"])
            except Exception:
                pass

        # Score the trace: 1 if answer found, 0 for no data, unclear, or refused questions
        try:
            score_val = determine_score(route, answer)
            score_trace(score_val)
        except Exception:
            pass

        return {"answer": answer, "sources": sources}
    except Exception:
        try:
            score_trace(0)
        except Exception:
            pass
        return {
            "answer": "The AI assistant is temporarily unavailable. Please try again shortly.",
            "sources": [],
        }
    finally:
        try:
            flush_langfuse()
        except Exception:
            pass
