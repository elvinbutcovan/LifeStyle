from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from types import SimpleNamespace
import project as model



def messageBuilder(exercises):
    iter = 0
    message = "[{\n"
    for exercise in exercises:
        muscleType = exercise[3]
        exerciseDescription = exercise[0]
        reps = exercise[1]
        weight = exercise[2]
        message += "\"muscleType\": " + "\"" + muscleType + "\",\n"
        message += "\"exerciseDescription\": " + "\"" + exerciseDescription + "\",\n"
        message += "\"reps\": " + "\"" + str(reps) + "\",\n"
        message += "\"weight\": " + "\"" + str(weight) + "\",\n"
        message += "},\n"
        iter+=1
        if(iter != len(exercises)):
            message+="{"

    message += "]"
    return message

class handler(BaseHTTPRequestHandler):
    #only need this if model code isn't fast enough to return recommendation in post
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = "Hello, World! Here is a GET response Robert Test"
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode("utf-8") # Request body as json string
        print(post_body)

        args = json.loads(post_body, object_hook=lambda d: SimpleNamespace(**d)) # Convert body into object with addressable fields.
        print(args)

        #repsonse
        #message = model.do_model_stuff(model.supplyDataset())
        #print(messageBuilder(message))
        self.wfile.write(bytes("message", "utf8"))
        #self.wfile.write(bytes(messageBuilder(message), "utf8"))

if __name__ == "__main__":
    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()



