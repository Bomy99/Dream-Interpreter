#!/usr/bin/env python3
"""
Simple HTTP server for the Dream-Quote Matcher web interface.
Run this script and open dream_matcher.html in your browser.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
import json
import os
from dream_quote_matcher import DreamQuoteMatcher
from pathlib import Path

# Initialize matcher once
print("Initializing Dream-Quote Matcher...")
matcher = DreamQuoteMatcher()
print("Server ready!")

class DreamMatcherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the HTML file and images."""
        if self.path == '/' or self.path == '/dream_matcher.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_path = Path('dream_matcher.html')
            if html_path.exists():
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'<h1>dream_matcher.html not found</h1>')
        elif self.path == '/FREUD.PNG' or self.path == '/freud.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            
            image_path = Path('FREUD.PNG')
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            # Try to serve book and emoji images - decode path first to handle URL encoding
            decoded_path = unquote(self.path.lstrip('/'))
            if decoded_path.startswith('without background'):
                file_path = Path(decoded_path)
                
                if file_path.exists() and file_path.suffix.lower() == '.png':
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    # Debug: log what we're looking for
                    print(f"404: Looking for {file_path} (exists: {file_path.exists()})")
                    print(f"  Original path: {self.path}")
                    print(f"  Decoded path: {decoded_path}")
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
    
    def do_POST(self):
        """Handle dream matching requests."""
        if self.path == '/match':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                dream_text = data.get('dream', '')
                
                if not dream_text:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'No dream text provided'}).encode())
                    return
                
                # Match the dream
                result = matcher.match(dream_text)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def run_server(port=8000):
    """Run the HTTP server."""
    import os
    # Get port from environment variable (for cloud hosting) or use default
    port = int(os.environ.get('PORT', port))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, DreamMatcherHandler)
    print(f"\nDream-Quote Matcher Server")
    print(f"Server running at http://0.0.0.0:{port}/")
    print(f"Open http://localhost:{port}/dream_matcher.html in your browser")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
