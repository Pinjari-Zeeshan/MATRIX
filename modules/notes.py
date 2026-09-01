import json
from datetime import datetime
from pathlib import Path


# MATRIX project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Notes storage file
NOTES_FILE = BASE_DIR / "data" / "notes.json"


def _load_notes() -> list:
    """
    Load notes from notes.json.
    """

    if not NOTES_FILE.exists():
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def _save_notes(notes: list) -> None:
    """
    Save notes to notes.json.
    """

    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


def add_note(content: str) -> dict:
    """
    Add a new note.
    """

    if not isinstance(content, str) or not content.strip():
        return {
            "success": False,
            "message": "Note content cannot be empty."
        }

    notes = _load_notes()

    if notes:
        new_id = max(note.get("id", 0) for note in notes) + 1
    else:
        new_id = 1

    note = {
        "id": new_id,
        "content": content.strip(),
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    notes.append(note)

    _save_notes(notes)

    return {
        "success": True,
        "message": "Note saved successfully.",
        "note": note
    }


def get_notes() -> dict:
    """
    Return all saved notes.
    """

    notes = _load_notes()

    return {
        "success": True,
        "message": f"Found {len(notes)} note(s).",
        "notes": notes
    }


def delete_note(note_id: int) -> dict:
    """
    Delete a note using its ID.
    """

    notes = _load_notes()

    original_count = len(notes)

    notes = [
        note
        for note in notes
        if note.get("id") != note_id
    ]

    if len(notes) == original_count:
        return {
            "success": False,
            "message": f"Note {note_id} was not found."
        }

    _save_notes(notes)

    return {
        "success": True,
        "message": f"Note {note_id} deleted successfully."
    }