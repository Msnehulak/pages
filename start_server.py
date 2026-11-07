import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

directory = "output/"
os.chdir(directory)

handler = SimpleHTTPRequestHandler
httpd = HTTPServer(("", 8000), handler)
print(f"Serving {directory} on http://127.0.0.1:8000/")
httpd.serve_forever()
