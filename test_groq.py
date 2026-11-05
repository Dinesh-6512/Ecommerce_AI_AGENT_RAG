from backend.ai_agent.llm import get_llm

def main():
    llm = get_llm()
    response = llm.invoke("Say hello in one line")
    print("Groq Response:", response.content)

if __name__ == "__main__":
    main()

