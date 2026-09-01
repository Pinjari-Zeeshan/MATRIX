import os
import subprocess

from dotenv import load_dotenv


load_dotenv()


ANDROID_USER = os.getenv("MATRIX_ANDROID_USER")
ANDROID_HOST = os.getenv("MATRIX_ANDROID_HOST")
ANDROID_PORT = os.getenv("MATRIX_ANDROID_PORT", "8022")


def run_android_command(command: str) -> dict:
    """
    Execute a command on the Android phone through SSH.
    """

    if not ANDROID_USER:
        return {
            "success": False,
            "message": "MATRIX_ANDROID_USER is not configured."
        }

    if not ANDROID_HOST:
        return {
            "success": False,
            "message": "MATRIX_ANDROID_HOST is not configured."
        }

    ssh_command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "-p",
        ANDROID_PORT,
        f"{ANDROID_USER}@{ANDROID_HOST}",
        command
    ]

    try:
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return {
                "success": False,
                "message": "Android command failed.",
                "error": result.stderr.strip()
            }

        return {
            "success": True,
            "message": "Android command executed successfully.",
            "output": result.stdout.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Connection to Android timed out."
        }

    except FileNotFoundError:
        return {
            "success": False,
            "message": "SSH was not found on this Windows computer."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Android bridge error: {exc}"
        }


def test_connection() -> dict:
    """
    Test the Windows → Android SSH connection.
    """

    return run_android_command("echo MATRIX_ANDROID_OK")


def make_phone_call(phone: str) -> dict:
    """
    Tell Android to initiate a cellular call.
    """

    if not phone:
        return {
            "success": False,
            "message": "No phone number was provided."
        }

    return run_android_command(
        f"termux-telephony-call {phone}"
    )