import http.server
import socketserver
import os
import json
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    PORT = 8080
    
    # Change to the directory containing the HTML file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"\nWeb server started at http://localhost:{PORT}")
        print(f"Access: http://localhost:{PORT}/voice-client.html")
        print("\nInstructions:")
        print("1. Make sure the bot is running on localhost:3978")
        print("2. Open the link above in your browser")
        print("3. Use the microphone for voice commands")
        print("4. Type messages or use voice to interact")
        print("\nAvailable features:")
        print("• Voice recognition (click the microphone)")
        print("• Voice synthesis (spoken responses)")
        print("• Real-time chat")
        print("• GPT-4o integration")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nWeb server stopped.")