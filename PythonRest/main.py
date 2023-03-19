from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from types import SimpleNamespace
import TestFile as Ts


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
        print(args.lName)
        if(args.questions):
            print("hello")
            Ts.printStuff()

        #repsonse
        message = "Hello, World! Here is a POST response"
        self.wfile.write(bytes(message, "utf8"))

if __name__ == "__main__":
    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()



