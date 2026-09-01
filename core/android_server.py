from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from core.llm_brain import parse_intent
from core.intent_router import route_intent


HOST = "0.0.0.0"
PORT = 8765


class MATRIXRequestHandler(BaseHTTPRequestHandler):

    def send_json(self, data: dict, status_code: int = 200):
        """
        Send a JSON response to the Android device.
        """

        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)

    def do_GET(self):
        """
        Handle GET requests.
        """

        if self.path == "/ping":

            self.send_json({
                "success": True,
                "message": "MATRIX Python is online"
            })

            print("Android ping received.")

        else:

            self.send_json({
                "success": False,
                "message": "Endpoint not found."
            }, 404)

    def do_POST(self):
        """
        Handle POST requests from Android.
        """

        if self.path not in ["/command", "/execute"]:

            self.send_json({
                "success": False,
                "message": "Endpoint not found."
            }, 404)

            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(
                body.decode("utf-8")
            )

            # =====================================================
            # EXISTING COMMAND MODE
            # =====================================================

            if self.path == "/command":

                command = data.get("command")

                print(f"Android command received: {command}")

                if command == "status":

                    self.send_json({
                        "success": True,
                        "message": "MATRIX Python is online",
                        "command": "status"
                    })

                    return

                elif command == "call":

                    phone = data.get("phone")

                    if not phone:

                        self.send_json({
                            "success": False,
                            "message": "No phone number was provided."
                        }, 400)

                        return

                    from modules.android_bridge import make_phone_call

                    result = make_phone_call(phone)

                    self.send_json(result)

                    return

                else:

                    self.send_json({
                        "success": False,
                        "message": f"Unknown command: {command}"
                    }, 400)

                    return

            # =====================================================
            # NATURAL LANGUAGE MATRIX MODE
            # =====================================================

            if self.path == "/execute":

                user_input = data.get("text")

                if not isinstance(user_input, str) or not user_input.strip():

                    self.send_json({
                        "success": False,
                        "message": "No command text was provided."
                    }, 400)

                    return

                print(f"Android MATRIX command: {user_input}")

                # Send natural language to Qwen
                parsed_intent = parse_intent(
                    user_input.strip()
                )

                print(
                    "Parsed intent:",
                    json.dumps(
                        parsed_intent,
                        ensure_ascii=False
                    )
                )

                # Route the intent
                result = route_intent(parsed_intent)

                self.send_json({
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "intent": parsed_intent,
                    "result": result
                })

                return

        except json.JSONDecodeError:

            self.send_json({
                "success": False,
                "message": "Invalid JSON."
            }, 400)

        except Exception as exc:

            self.send_json({
                "success": False,
                "message": f"Server error: {exc}"
            }, 500)
   
    def log_message(self, format, *args):
        """
        Keep default HTTP logs quiet.
        """
        return


def start_server():
    server = HTTPServer(
        (HOST, PORT),
        MATRIXRequestHandler
    )

    print("===================================")
    print("       MATRIX Android Server")
    print("===================================")
    print(f"Listening on port {PORT}")
    print("Waiting for Android...")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print("\nMATRIX Android Server stopped.")

    finally:

        server.server_close()


if __name__ == "__main__":
    start_server()