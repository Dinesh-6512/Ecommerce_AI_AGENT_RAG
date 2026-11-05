import sys
from backend.rag.rag_flow import run_rag_flow

def main():
    if len(sys.argv) < 2:
        question = "How do I pair the wireless bluetooth headphones?"
    else:
        question = " ".join(sys.argv[1:])

    print(f"\nQuestion: {question}")
    result = run_rag_flow(question)
    print("\nAnswer:")
    print(result.get("answer"))

    sources = result.get("sources", [])
    if sources:
        print("\nSources:")
        for s in sources:
            print(f"- {s['manual']} (Section: {s['section']}) -> {s['download_link']}")
    else:
        print("\nSources: None")
    print()

if __name__ == "__main__":
    main()

