from modules.notes import add_note, get_notes, delete_note

from modules.contacts import (
    add_contact,
    get_contacts,
    find_contact,
    update_contact,
    delete_contact
)

from modules.calling import (
    resolve_contact_for_call,
    make_call
)


def route_intent(parsed_intent: dict) -> dict:
    """
    Routes a parsed MATRIX intent to the appropriate module.
    """

    if not isinstance(parsed_intent, dict):
        return {
            "success": False,
            "message": "Invalid intent data."
        }

    intent = parsed_intent.get("intent")
    params = parsed_intent.get("params", {})

    if not isinstance(params, dict):
        params = {}

    # =========================================================
    # NOTE
    # =========================================================

    if intent == "note":
        action = params.get("action")

        # Add note
        if action == "add":
            content = params.get("content")

            if not content:
                return {
                    "success": False,
                    "message": "No note content was provided."
                }

            return add_note(content)

        # List notes
        elif action == "list":
            return get_notes()

        # Delete note
        elif action == "delete":
            note_id = params.get("id")

            if note_id is None:
                return {
                    "success": False,
                    "message": "No note ID was provided."
                }

            try:
                note_id = int(note_id)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "Note ID must be a number."
                }

            return delete_note(note_id)

        return {
            "success": False,
            "message": f"Unknown note action: {action}"
        }

    # =========================================================
    # CALL
    # =========================================================

    elif intent == "call":
        name = params.get("name")

        if not name:
            return {
                "success": False,
                "message": "I need a contact name to make a call."
            }

        # Step 1: Find the contact
        contact_result = resolve_contact_for_call(name)

        # Stop if contact could not be resolved
        if not contact_result.get("success"):
            return contact_result

        # Step 2: Get the phone number
        contact = contact_result.get("contact")

        if not contact:
            return {
                "success": False,
                "message": "The contact information could not be retrieved."
            }

        phone = contact.get("phone")

        if not phone:
            return {
                "success": False,
                "message": f"{contact.get('name', name)} does not have a phone number."
            }

        # Step 3: Actually make the call
        return make_call(phone)

    # =========================================================
    # ADD CONTACT
    # =========================================================

    elif intent == "add_contact":
        action = params.get("action")

        # Add contact
        if action == "add":
            name = params.get("name")
            phone = params.get("phone")
            email = params.get("email")

            if not name:
                return {
                    "success": False,
                    "message": "Contact name was not provided."
                }

            return add_contact(
                name=name,
                phone=phone,
                email=email
            )

        # List contacts
        elif action == "list":
            return get_contacts()

        # Find contact
        elif action == "find":
            name = params.get("name")

            if not name:
                return {
                    "success": False,
                    "message": "Contact name was not provided."
                }

            return find_contact(name)

        # Update contact
        elif action == "update":
            contact_id = params.get("id")

            if contact_id is None:
                return {
                    "success": False,
                    "message": "Contact ID was not provided."
                }

            try:
                contact_id = int(contact_id)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "Contact ID must be a number."
                }

            return update_contact(
                contact_id=contact_id,
                name=params.get("name"),
                phone=params.get("phone"),
                email=params.get("email")
            )

        # Delete contact
        elif action == "delete":
            contact_id = params.get("id")

            if contact_id is None:
                return {
                    "success": False,
                    "message": "Contact ID was not provided."
                }

            try:
                contact_id = int(contact_id)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "Contact ID must be a number."
                }

            return delete_contact(contact_id)

        return {
            "success": False,
            "message": f"Unknown contact action: {action}"
        }

    # =========================================================
    # EMAIL
    # =========================================================

    elif intent == "email":
        return {
            "success": False,
            "message": "Email module is not implemented yet."
        }

    # =========================================================
    # UNKNOWN
    # =========================================================

    elif intent == "unknown":
        return {
            "success": False,
            "message": "I don't understand that command yet."
        }

    # =========================================================
    # INVALID / UNSUPPORTED INTENT
    # =========================================================

    return {
        "success": False,
        "message": f"Unknown intent: {intent}"
    }