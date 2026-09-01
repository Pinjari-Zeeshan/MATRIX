import subprocess
import tempfile
from pathlib import Path


POWERSHELL_SCRIPT = r'''
Add-Type -AssemblyName System.Speech

$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine("en-US")

$recognizer.SetInputToDefaultAudioDevice()

$recognizer.LoadGrammar(
    (New-Object System.Speech.Recognition.DictationGrammar)
)

$result = $recognizer.Recognize(
    [TimeSpan]::FromSeconds(8)
)

if ($null -ne $result) {
    Write-Output $result.Text
}
'''


def listen_once(timeout: int = 8) -> str:
    """
    Listen through the Windows default microphone and
    return the recognized speech as text.
    """

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ps1",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(POWERSHELL_SCRIPT)
            script_path = Path(file.name)

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path)
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )

        script_path.unlink(missing_ok=True)

        if result.returncode != 0:
            return f"[STT ERROR] {result.stderr.strip()}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "[STT ERROR] Listening timed out."

    except Exception as exc:
        return f"[STT ERROR] {exc}"


if __name__ == "__main__":
    print("MATRIX Windows Speech Test")
    print("---------------------------")
    print("Speak after the program starts.")
    print("Listening for up to 8 seconds...")
    print()

    text = listen_once()

    print("Recognized:")
    print(text)