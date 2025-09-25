from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
from threading import Timer

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def open_browser():
    webbrowser.open('http://localhost:3001')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Use 0.0.0.0 to accept connections from outside the container
    server = HTTPServer(('0.0.0.0', 3001), CORSRequestHandler)

    print("Health Chatbot GUI Server starting...")
    print("Server running at: http://0.0.0.0:3001")
    print("Access from host at: http://localhost:3001")

    # Don't open browser when running in Docker container
    # Timer(2.0, open_browser).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
