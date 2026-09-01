import os

from modules.contacts import find_contact

from modules.android_bridge import make_phone_call


def resolve_contact_for_call(name: str) -> dict:
    """
    Find the contact MATRIX wants to call.

    This does not make the call.
    """

    if not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "message": "I need a contact name to make a call."
        }

    result = find_contact(name.strip())

    if not result.get("success"):
        return {
            "success": False,
            "message": f"I couldn't find a contact named '{name}'."
        }

    contacts = result.get("contacts", [])

    if not contacts:
        return {
            "success": False,
            "message": f"I couldn't find a contact named '{name}'."
        }

    if len(contacts) > 1:
        names = ", ".join(
            contact["name"]
            for contact in contacts
        )

        return {
            "success": False,
            "message": (
                f"I found multiple contacts matching '{name}': "
                f"{names}. Please specify the exact contact name."
            ),
            "contacts": contacts
        }

    contact = contacts[0]

    if not contact.get("phone"):
        return {
            "success": False,
            "message": (
                f"{contact['name']} does not have a phone number "
                "saved in your contacts."
            ),
            "contact": contact
        }

    return {
        "success": True,
        "message": f"Found {contact['name']}.",
        "contact": contact
    }


def make_call(phone: str) -> dict:
    """
    Start a cellular call through the Android bridge.
    """

    return make_phone_call(phone)