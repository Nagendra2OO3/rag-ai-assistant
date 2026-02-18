from rag_engine import ask_question


while True:
    q = input("Ask: ")

    if q.lower() == "exit":
        break

    ans = ask_question(q)

    print("\nAnswer:", ans)
