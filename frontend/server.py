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

    server = HTTPServer(('localhost', 3001), CORSRequestHandler)

    print("Health Chatbot GUI Server starting...")
    print("Server running at: http://localhost:3001")
    print("Opening browser in 2 seconds...")

    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
