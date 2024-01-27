import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import socket

UDP_IP = "localhost"
UDP_PORT = 5000
APP_IP = "localhost"
APP_PORT = 3000


class HttpHandler(BaseHTTPRequestHandler):
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # def __init__(self, udp_client: socket, *args, **kwargs):
    #     self.udp_client = udp_client
    #     super().__init__(*args, **kwargs)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        print(pr_url.path)
        if pr_url.path == "/":
            self.send_html_file("./index.html")
        elif pr_url.path == "/message":
            self.send_html_file("./message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("./error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)
        HttpHandler.udp_client.send("Testing message".encode())
        print(HttpHandler.udp_client.recv(1024).decode())
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def connect_udp_client(host, port) -> socket:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    udp_socket.connect()
    return udp_socket


def run_udp_server(ip, port):
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind((ip, port))
    while True:
        comm_socket, address = udp_server.accept()
        message = comm_socket.recv(1024).decode()
        print(message)
        comm_socket.send("Message stored succesfully")


def run():
    # udp_server_thread = threading.Thread(target=run_udp_server, args=(UDP_IP, UDP_PORT))
    # udp_server_thread.start()
    # run_udp_server(UDP_IP, UDP_PORT)
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind((UDP_IP, UDP_PORT))
    comm_socket, address = udp_server.accept()

    # udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # http_handler = HttpHandler(udp_client=udp_client)
    http_server_address = (APP_IP, APP_PORT)
    http_server = HTTPServer(http_server_address, HttpHandler)
    http_server_thread = threading.Thread(target=http_server.serve_forever())
    http_server_thread.start()
    http_server_thread.join()
    # udp_server_thread.join()

    # http_server_address = ("localhost", APP_PORT)
    # http_server = HTTPServer(http_server_address, HttpHandler)
    # try:
    #     http_server.serve_forever()
    # except KeyboardInterrupt:
    #     http_server.server_close()


if __name__ == "__main__":
    run()
