from r2pytcp import *
import time

class Handler (HTTPHandler):
    def __init__ (self, client_socket):
        super().__init__(client_socket)
        print (client_socket.getsockname()[0], "|", self.path)
        self.headers["Content-Type"] = "text/plain"
        self.headers["Content-Length"] = "13"
        self.send_response(200)
        self.send_headers()
        self.write(b"Hello, world!")
        self.close()

if __name__ == "__main__":
    server = ThreadTCPServer(("0.0.0.0", 3500), Handler, allow_reuse_port=True)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
