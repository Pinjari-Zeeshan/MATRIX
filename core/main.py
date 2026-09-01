import json

from core.llm_brain import parse_intent
from core.intent_router import route_intent


def main():
    print("===================================")
    print("        MATRIX AI ASSISTANT")
    print("===================================")
    print("Type a command or 'exit' to quit.")
    print()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("MATRIX: Shutting down.")
            break

        if not user_input:
            continue

        try:
            # Step 1: Send user command to the LLM
            parsed_intent = parse_intent(user_input)

            print("\n[Intent]")
            print(
                json.dumps(
                    parsed_intent,
                    indent=2,
                    ensure_ascii=False
                )
            )

            # Step 2: Send parsed intent to router
            result = route_intent(parsed_intent)

            print("\n[MATRIX]")
            print(result["message"])

            if result.get("notes"):
                for note in result["notes"]:
                    print(f"[{note['id']}] {note['content']}")

            if result.get("contacts"):
                for contact in result["contacts"]:
                    print(
                        f"[{contact['id']}] "
                        f"{contact['name']} | "
                        f"Phone: {contact['phone'] or 'N/A'} | "
                        f"Email: {contact['email'] or 'N/A'}"
                    )

            print()

        except Exception as e:
            print(f"\nMATRIX Error: {e}\n")


if __name__ == "__main__":
    main()