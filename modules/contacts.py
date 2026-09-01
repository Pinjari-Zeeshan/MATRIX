import re
import sqlite3
from datetime import datetime
from pathlib import Path


# MATRIX project root
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database
DB_FILE = BASE_DIR / "data" / "contacts.db"


def get_connection():
    """
    Create and return a connection to the contacts database.
    """

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the contacts table if it doesn't already exist.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:
        connection.close()


def normalize_phone(phone: str | None) -> str | None:
    """
    Normalize a phone number for consistent storage/comparison.

    Keeps digits only.

    Example:
        +91 98765 43210 -> 919876543210
        98765-43210     -> 9876543210
    """

    if phone is None:
        return None

    phone = str(phone).strip()

    if not phone:
        return None

    # Keep digits only
    digits = re.sub(r"\D", "", phone)

    return digits if digits else None


def get_contact_by_id(contact_id: int) -> dict | None:
    """
    Get one contact by its database ID.
    """

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, created_at
            FROM contacts
            WHERE id = ?
        """, (contact_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def add_contact(
    name: str,
    phone: str | None = None,
    email: str | None = None
) -> dict:
    """
    Add a new contact after checking for duplicates.
    """

    if not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "message": "Contact name cannot be empty."
        }

    name = name.strip()
    phone = normalize_phone(phone)

    if email:
        email = str(email).strip().lower()
    else:
        email = None

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check duplicate by phone number
        if phone:
            cursor.execute("""
                SELECT id, name, phone, email
                FROM contacts
                WHERE phone = ?
                LIMIT 1
            """, (phone,))

            existing = cursor.fetchone()

            if existing:
                return {
                    "success": False,
                    "message": "A contact with this phone number already exists.",
                    "contact": dict(existing)
                }

        # Check duplicate by name
        cursor.execute("""
            SELECT id, name, phone, email
            FROM contacts
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1
        """, (name,))

        existing = cursor.fetchone()

        if existing:
            return {
                "success": False,
                "message": f"A contact named '{name}' already exists.",
                "contact": dict(existing)
            }

        # Insert new contact
        cursor.execute("""
            INSERT INTO contacts (
                name,
                phone,
                email,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()

        contact_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Contact added successfully.",
            "contact": {
                "id": contact_id,
                "name": name,
                "phone": phone,
                "email": email
            }
        }

    finally:
        connection.close()


def get_contacts() -> dict:
    """
    Return all contacts.
    """

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, created_at
            FROM contacts
            ORDER BY name COLLATE NOCASE
        """)

        rows = cursor.fetchall()

        contacts = [dict(row) for row in rows]

        return {
            "success": True,
            "message": f"Found {len(contacts)} contact(s).",
            "contacts": contacts
        }

    finally:
        connection.close()


def find_contact(name: str) -> dict:
    """
    Find contacts using a partial name match.
    """

    if not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "message": "Contact name cannot be empty.",
            "contacts": []
        }

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        search_name = name.strip()

        cursor.execute("""
            SELECT id, name, phone, email, created_at
            FROM contacts
            WHERE name LIKE ?
            ORDER BY name COLLATE NOCASE
        """, (f"%{search_name}%",))

        rows = cursor.fetchall()

        contacts = [dict(row) for row in rows]

        if not contacts:
            return {
                "success": False,
                "message": f"No contact found matching '{name}'.",
                "contacts": []
            }

        return {
            "success": True,
            "message": f"Found {len(contacts)} matching contact(s).",
            "contacts": contacts
        }

    finally:
        connection.close()


def update_contact(
    contact_id: int,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None
) -> dict:
    """
    Update one or more fields of an existing contact.
    """

    existing = get_contact_by_id(contact_id)

    if existing is None:
        return {
            "success": False,
            "message": f"Contact {contact_id} was not found."
        }

    if name is None:
        name = existing["name"]

    if phone is None:
        phone = existing["phone"]
    else:
        phone = normalize_phone(phone)

    if email is None:
        email = existing["email"]
    else:
        email = email.strip().lower() if email.strip() else None

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Don't allow the new phone number to belong to another contact
        if phone:
            cursor.execute("""
                SELECT id
                FROM contacts
                WHERE phone = ?
                AND id != ?
                LIMIT 1
            """, (phone, contact_id))

            duplicate_phone = cursor.fetchone()

            if duplicate_phone:
                return {
                    "success": False,
                    "message": "That phone number already belongs to another contact."
                }

        cursor.execute("""
            UPDATE contacts
            SET name = ?,
                phone = ?,
                email = ?
            WHERE id = ?
        """, (
            name.strip(), # type: ignore
            phone,
            email,
            contact_id
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Contact updated successfully.",
            "contact": get_contact_by_id(contact_id)
        }

    finally:
        connection.close()


def delete_contact(contact_id: int) -> dict:
    """
    Delete a contact using its ID.
    """

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM contacts
            WHERE id = ?
        """, (contact_id,))

        connection.commit()

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": f"Contact {contact_id} was not found."
            }

        return {
            "success": True,
            "message": f"Contact {contact_id} deleted successfully."
        }

    finally:
        connection.close()


initialize_database()