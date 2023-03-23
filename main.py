from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from types import SimpleNamespace
import project as model

#def messageBuilder(exercises):
#    iter = 0
#    message = "[{\n"
#    for exercise in exercises:
#        muscleType = exercise[3]
#        exerciseDescription = exercise[0]
#        reps = exercise[1]
#        weight = exercise[2]
#        message += "\"muscleType\": " + "\"" + muscleType + "\",\n"
#        message += "\"exerciseDescription\": " + "\"" + exerciseDescription + "\",\n"
#        message += "\"reps\": " + "\"" + str(reps) + "\",\n"
#        message += "\"weight\": " + "\"" + str(weight) + "\",\n"
#        message += "},\n"
#        iter+=1
#        if(iter != len(exercises)):
#            message+="{"

#    message += "]"
#    return message

#class handler(BaseHTTPRequestHandler):

#    def do_POST(self):
#        self.send_response(200)
#        self.send_header('Content-type','application/json')
#        self.end_headers()
#        content_len = int(self.headers.get('Content-Length'))
#        post_body = self.rfile.read(content_len).decode("utf-8") # Request body as json string
#        #print(post_body)

#        args = json.loads(post_body, object_hook=lambda d: SimpleNamespace(**d)) # Convert body into object with addressable fields.

        #repsonse
#        message = model.run_model(args)
#        self.wfile.write(bytes(messageBuilder(message), "utf8"))

#if __name__ == "__main__":
#    with HTTPServer(('', 8000), handler) as server:
#        server.serve_forever()

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


class handler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode("utf-8") # Request body as json string

        args = json.loads(post_body, object_hook=lambda d: SimpleNamespace(**d)) # Convert body into object with addressable fields.

        #response
        message = model.run_model(args)
        self.wfile.write(bytes(messageBuilder(message), "utf8"))

if __name__ == "__main__":
    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()


