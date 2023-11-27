import sys
import datetime
import socket

HOST = "127.0.0.1"
PORT = 8080
HTTP_VERSION = 1.1

class HttpRequest:
    def __init__(self, request_entry):
        request_type_path_ver: list = request_entry[0].split(b" ")
        self.request_method = request_type_path_ver[0]
        self.request_target = request_type_path_ver[1]
        self.request_prot_ver = request_type_path_ver[2]
        self.request_host = request_entry[1]


class HttpResonse:
    def __init__(self):
        self.HTTP_VERSION = bytes(HTTP_VERSION)
        


def get_file_on_path(path):
    path = path[1:len(path)]
    #print(path)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.split(b"\r\n")
                request = HttpRequest(data)

                get_file_on_path(request.request_target)
                with open("./index.html", "r") as f:
                    file_contents = f.read()
                    response = bytes(f"{request.request_prot_ver} 200 OK\r\nDate: {datetime.datetime.now()}\r\nServer: Custom\r\nLast-Modified: {datetime.datetime.now()}\r\nAccept-Ranges: bytes\r\nContent-Length: {len(file_contents)}\r\nContent-Type: text/html\r\n\r\n", "ISO-8859-1" )
                    response = response+bytes(f"{file_contents}\r\n", "ISO-8859-1")
                print(response)
                
                conn.sendall(response)
                
        except KeyboardInterrupt or Exception as e:
            e.with_traceback()