from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from types import SimpleNamespace
import project as model

# This function validates the input muscle groups data, ensuring the required fields are present, unique, and within valid ranges
def validate_input(muscle_groups):
    valid_muscle_types = ["Chest", "Shoulders", "Triceps", "Biceps", "Back", "Legs"]
    muscle_types_count = {muscle_type: 0 for muscle_type in valid_muscle_types}

    for group in muscle_groups:
        # Check if all required fields are present
        if not all(hasattr(group, key) for key in ["muscleType", "reps", "weight"]):
            return False

        muscle_type = group.muscleType
        reps = group.reps
        weight = group.weight

        # Check if the muscle type is valid and not duplicated
        if muscle_type not in valid_muscle_types or muscle_types_count[muscle_type] > 0:
            return False
        muscle_types_count[muscle_type] += 1

        # Check if the reps and weight are valid integers
        try:
            reps = int(reps)
            weight = int(weight)
        except ValueError:
            return False

        # Check if the reps and weight are within the valid range
        if reps < 1 or reps > 61 or weight < 0 or weight > 501:
            return False

    return True

# This function builds a JSON-formatted message with the list of exercises to be sent as a response
def messageBuilder(exercises):
    message = []

    for exercise in exercises:
        muscleType = exercise[3]
        exerciseDescription = exercise[0]
        reps = exercise[1]
        weight = exercise[2]

        exercise_info = {
            "muscleType": muscleType,
            "exerciseDescription": exerciseDescription,
            "reps": str(reps),
            "weight": str(weight),
        }
        message.append(exercise_info)

    return json.dumps(message)

# This class defines a custom HTTP request handler for the server
class handler(BaseHTTPRequestHandler):

    # This function sends CORS headers to the client
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    # This function handles OPTIONS requests by sending the CORS headers and an OK response
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # This function handles POST requests by validating the input, running the model, and sending the exercise recommendations as a JSON response
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode("utf-8")  # Request body as json string

        args = json.loads(post_body, object_hook=lambda d: SimpleNamespace(**d))  # Convert body into object with addressable fields.

        # Validate input
        if not validate_input(args.muscleGroups):
            error_message = json.dumps({"error": "Invalid input"})
            self.wfile.write(bytes(error_message, "utf8"))
            return

        # Response
        message = model.run_model(args)
        self.wfile.write(bytes(messageBuilder(message), "utf8"))

# The main function runs the HTTP server with the custom request handler
if __name__ == "__main__":
    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()


