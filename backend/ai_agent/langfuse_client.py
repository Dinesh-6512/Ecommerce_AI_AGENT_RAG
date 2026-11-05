import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env first
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def check_langfuse_connection():
    try:
        from langfuse import get_client
        client = get_client()
        if client.auth_check():
            print("Langfuse connected: yes")
        else:
            print("Langfuse connected: no - check the keys and LANGFUSE_HOST")
    except Exception:
        print("Langfuse connected: no - check the keys and LANGFUSE_HOST")

def get_langfuse_handler():
    try:
        from langfuse.langchain import CallbackHandler
        return CallbackHandler()
    except Exception:
        return None

def update_trace_info(user_id: int, role: str, request_id: str, tags: list[str] | None = None):
    try:
        from langfuse import get_client
        client = get_client()
        kwargs = {
            "user_id": str(user_id),
            "metadata": {"role": role, "request_id": request_id},
        }
        if tags:
            kwargs["tags"] = tags
        client.update_current_trace(**kwargs)
    except Exception:
        pass

def update_trace_manual_data(search_query: str, chunk_count: int, tags: list[str] | None = None):
    try:
        from langfuse import get_client
        client = get_client()
        kwargs = {
            "metadata": {
                "search_text": search_query,
                "chroma_chunks_found": chunk_count,
            }
        }
        if tags:
            kwargs["tags"] = tags
        client.update_current_trace(**kwargs)
    except Exception:
        pass

def score_trace(answer_found: int):
    try:
        from langfuse import get_client
        client = get_client()
        client.score_current_trace(name="answer_found", value=answer_found)
    except Exception:
        pass

def flush_langfuse():
    try:
        from langfuse import get_client
        client = get_client()
        client.flush()
    except Exception:
        pass
