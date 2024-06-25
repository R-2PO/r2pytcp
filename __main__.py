from r2pytcp import *

if __name__ == "__main__":
    server = TCPServer(("0.0.0.0", 3500), HTTPHandler, allow_reuse_port=True)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
