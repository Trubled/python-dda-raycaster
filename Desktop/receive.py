import http.server
import socketserver
import urllib.parse

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)

        if 'text' in data and 'filename' in data:
            text_content = data['text'][0]
            filename = data['filename'][0].strip()
            
            # Fallback if filename is left blank
            if not filename:
                filename = "output.txt"

            print("\n--- RECEIVED FROM PHONE ---")
            print(f"Target file: {filename}")
            print(text_content)
            print("---------------------------")

            # Save automatically to the dynamic filename!
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text_content)
            print(f"Successfully saved to {filename}!\n")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"File received and saved successfully to {filename}!".encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Missing text or filename field.")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <html><body>
        <h2>Send any file to laptop:</h2>
        <form method="POST">
            Filename (e.g., notes.txt, script.py):<br>
            <input type="text" name="filename" value="script.py" style="width: 300px;"><br><br>
            Content:<br>
            <textarea name="text" rows="15" cols="50"></textarea><br><br>
            <input type="submit" value="Send to Laptop">
        </form>
        </body></html>
        """
        self.wfile.write(html.encode('utf-8'))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving file receiver on port {PORT}...")
    httpd.serve_forever()