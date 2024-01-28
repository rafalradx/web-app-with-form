import mimetypes
import pathlib
import urllib.parse
import threading
import socket
import pickle
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from time import time
from datetime import datetime

UDP_IP = "localhost"
UDP_PORT = 5000
APP_IP = "localhost"
APP_PORT = 3000
JSON_FILE = "./storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_address = (UDP_IP, UDP_PORT)

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
        data_parsed = urllib.parse.unquote_plus(data.decode())
        pickled_dict_bytes = self.prepare_message(data_parsed)
        responce = self.send_message_udp(pickled_dict_bytes)
        print(responce)
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

    def prepare_message(self, data_parsed: str):
        """formats data returned from POST (data_parsed)
        into dict with timestamp as a key
        return pickled bytes"""
        data_dict = {
            key: value
            for key, value in [el.split("=") for el in data_parsed.split("&")]
        }
        current_time = datetime.now()
        return_dict = {str(current_time): data_dict}
        return pickle.dumps(return_dict)

    def send_message_udp(self, message: bytes):
        HttpHandler.udp_client.sendto(message, HttpHandler.udp_server_address)
        response, address = HttpHandler.udp_client.recvfrom(1024)
        return (
            f"CLIENT: Response data: '{response.decode()}' from UDP server: {address}"
        )


def run_udp_server(ip, port):
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind((ip, port))
    try:
        while True:
            message, address = udp_server.recvfrom(1024)
            message_dict = pickle.loads(message)
            print(f"SERVER: Message received from UDP client {address}")
            try:
                responce = store_message_into_json(message_dict, JSON_FILE)
            except:
                responce = "Saving message failed"
            udp_server.sendto(responce.encode(), address)
    except KeyboardInterrupt:
        print(f"Destroy server")
        udp_server.close()


def run_http_server(address, handler: HttpHandler):
    http_server = HTTPServer(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


def store_message_into_json(data_dict, file) -> str:
    """Merges data_dict (dictionary) into JSON file with dictionary
    if file does not exist creates it
    if file exists but it's not in JSON format wipes it nad dumps data_dict
    if file already contains a dict in JSON, loads, updates dict
    and dumps it
    Function is not efficient as it needs to load the whole file (possibly large) contents
    every time when it stores new dict
    there no simple way to append json file
    returns a string with operation status"""
    if os.path.isfile(file):
        with open(file, "r+") as fh:
            try:
                json_loaded = json.load(fh)
                json_loaded.update(data_dict)
            except:
                # the only working way to wipe the file out
                # and dump dict in json
                fh.truncate(0)
                fh.seek(0, 0)
                fh.write(json.dumps(data_dict))
                return "Error reading JSON file, creating new"
        # I dont know why but the file needs to be reopen in w mode #
        # in order for json.dump to work properly
        with open(file, "w") as fh:
            json.dump(json_loaded, fh)
            return "Message registered in file"
    else:
        with open(file, "w") as fh:
            json.dump(data_dict, fh)
            return "File created. Message registered in file"


def run():
    udp_server_thread = threading.Thread(target=run_udp_server, args=(UDP_IP, UDP_PORT))
    http_server_thread = threading.Thread(
        target=run_http_server, args=((APP_IP, APP_PORT), HttpHandler)
    )
    try:
        udp_server_thread.start()
        http_server_thread.start()
    except KeyboardInterrupt:
        http_server_thread.join()
        udp_server_thread.join()


if __name__ == "__main__":
    run()
