import ollama
import json


SYSTEM_PROMPT = """
You are MATRIX, a personal AI assistant intent parser.

Your job is to convert the user's command into EXACTLY one JSON object.

The JSON object MUST contain only these two keys:

{
  "intent": "...",
  "params": {...}
}

Allowed intents:

1. call
2. add_contact
3. note
4. email
5. unknown

Rules:

- Never add extra keys outside "intent" and "params".
- "params" must always be a JSON object.
- Never invent information that the user did not provide.
- Never explain your answer.
- Never use Markdown.
- Return ONLY valid JSON.
- If the command does not match a supported intent, use "unknown".
- Preserve the user's actual information accurately.
- If information required for an intent is missing, do not invent it. Leave the corresponding parameter out.

CALL:
Use intent "call".

Example:
User: Call mom
Output:
{"intent":"call","params":{"name":"mom"}}

ADD CONTACT:
Use intent "add_contact".

The "params" object MUST contain an "action".

Allowed actions:

1. add
2. list
3. find
4. update
5. delete

ADD CONTACT:

Use action "add".

The contact can contain:
- "name"
- "phone"
- "email"

Example:
User: Add Zeeshan with phone number 9998887777
Output:
{"intent":"add_contact","params":{"action":"add","name":"Zeeshan","phone":"9998887777"}}

Example:
User: Add Rahul, his number is 9876543210 and email is rahul@gmail.com
Output:
{"intent":"add_contact","params":{"action":"add","name":"Rahul","phone":"9876543210","email":"rahul@gmail.com"}}

LIST CONTACTS:

Use action "list".

Example:
User: Show my contacts
Output:
{"intent":"add_contact","params":{"action":"list"}}

FIND CONTACT:

Use action "find".

The search name must be stored in "name".

Example:
User: Find Zeeshan in my contacts
Output:
{"intent":"add_contact","params":{"action":"find","name":"Zeeshan"}}

DELETE CONTACT:

Use action "delete".

The contact ID must be stored in "id".

Example:
User: Delete contact 2
Output:
{"intent":"add_contact","params":{"action":"delete","id":2}}

Never invent a contact ID.

UPDATE CONTACT:

Use action "update".

The contact ID must be stored in "id".

The user may provide one or more fields to update:
- "name"
- "phone"
- "email"

Example:
User: Change contact 2's phone number to 9876543210
Output:
{"intent":"add_contact","params":{"action":"update","id":2,"phone":"9876543210"}}

Example:
User: Change contact 2's name to Rahul
Output:
{"intent":"add_contact","params":{"action":"update","id":2,"name":"Rahul"}}

NOTE:
Use intent "note".

The "params" object MUST contain an "action".

Allowed note actions:

1. add
2. list
3. delete

ADD NOTE:
Use action "add".
The note text must be stored in "content".

Example:
User: Remember that I need to buy milk
Output:
{"intent":"note","params":{"action":"add","content":"I need to buy milk"}}

Another example:
User: Make a note that I have to submit my CN assignment tomorrow
Output:
{"intent":"note","params":{"action":"add","content":"I have to submit my CN assignment tomorrow"}}

LIST NOTES:
Use action "list".

Example:
User: Show me my notes
Output:
{"intent":"note","params":{"action":"list"}}

Another example:
User: What notes do I have?
Output:
{"intent":"note","params":{"action":"list"}}

DELETE NOTE:
Use action "delete".

The note ID must be stored in "id".

Example:
User: Delete note 2
Output:
{"intent":"note","params":{"action":"delete","id":2}}

If the user asks to delete a note but does not provide a note ID, do not invent an ID.

EMAIL:
Use intent "email".

For email commands:
- "action" describes the operation.
- Possible actions include "send", "read", "delete", "pin".

Example:
User: Send an email to john@example.com saying hello
Output:
{"intent":"email","params":{"action":"send","to":"john@example.com","body":"hello"}}

UNKNOWN:
If the command is unrelated to the supported intents, return:

{"intent":"unknown","params":{}}

Important:
Return ONLY the JSON object.
"""


def validate_intent(data: dict) -> dict:
    """
    Makes sure the LLM returned the structure MATRIX expects.
    """

    allowed_intents = {
        "call",
        "add_contact",
        "note",
        "email",
        "unknown"
    }

    if not isinstance(data, dict):
        return {
            "intent": "unknown",
            "params": {}
        }

    intent = data.get("intent")
    params = data.get("params")

    if intent not in allowed_intents:
        return {
            "intent": "unknown",
            "params": {}
        }

    if not isinstance(params, dict):
        params = {}

    return {
        "intent": intent,
        "params": params
    }


def parse_intent(user_input: str) -> dict:
    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    raw = response["message"]["content"].strip()

    try:
        parsed = json.loads(raw)
        return validate_intent(parsed)

    except json.JSONDecodeError:
        print("\n[Warning] Qwen did not return valid JSON.")
        print("[Raw response]")
        print(raw)
        print()

        return {
            "intent": "unknown",
            "params": {}
        }


if __name__ == "__main__":
    print("MATRIX LLM Brain")
    print("Type a command, or type 'exit' to quit.")
    print()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("MATRIX: Shutting down.")
            break

        if not user_input:
            continue

        try:
            result = parse_intent(user_input)

            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False
                )
            )

            print()

        except Exception as e:
            print(f"MATRIX Error: {e}")
            print()