#!/usr/bin/env python3
"""
Simple HTTP server to serve the web client for testing the bot
"""

import http.server
import socketserver
import os
import webbrowser
from threading import Timer

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open(f'http://localhost:{PORT}/web-client.html')

if __name__ == "__main__":
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Servidor web iniciado em http://localhost:{PORT}")
        print(f"📱 Bot page: http://localhost:{PORT}/web-client.html")
        print("🤖 Make sure the bot is running on http://localhost:3978")
        print("Press CTRL+C to stop the server")
        
        # Open browser after 1 second
        Timer(1.0, open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor web parado")
            httpd.shutdown()