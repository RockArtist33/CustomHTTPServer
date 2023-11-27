import sys
import os
import socket
import datetime
import selectors
import types

sel = selectors.DefaultSelector()
HTTP_VERSION = 1.1

class HttpRequest:
    def __init__(self, request_entry: list):
        request_type_path_ver: list = request_entry[0].split(b" ")
        self.request_method = request_type_path_ver[0]
        self.request_target = request_type_path_ver[1]
        self.request_prot_ver = request_type_path_ver[2]
        self.request_host = request_entry[1]
        self.other_headers = request_entry[2:]
        

class HttpResponse:
    def __init__(self):
        self.HTTP_VERSION = HTTP_VERSION
        self.status = 0
        self.status_message = "null"
        self.server_name = "Custom"
        self.request_date = datetime.datetime.now()
        self.modified_date = os.path.getmtime("server.py")
        self.acc_ranges = "bytes"
        self.content_length = 0
        self.content_type = ""
        
def request_parser(data):
    data = data.split(b"\r\n")
    request = HttpRequest(data)
    return request

def get_file_on_path(response: HttpResponse, path):
    path = str(path)
    path = path[2:-1]
    if path == "/":
        path = "./index.html"
    else:
        path = "."+path
    try:
        if os.path.exists(path):
            print(os.path.splitext(path))
            response.content_length = os.path.getsize(path)
            if os.path.splitext(path)[1].strip(".") in ["html","css","js","txt","md"]:
                
                response.content_type = f"text/{os.path.splitext(path)[1].strip('.')}"
            elif os.path.splitext(path)[1].strip(".") in ["jpeg","png","webp","svg"]:
                response.content_type = f"image/{os.path.splitext(path)[1].strip('.')}"
            response.status, response.status_message = 200, "OK"

            f = open(path,"rb")
            return f
        else:
            response.status = 404
            response.status_message = "Not Found"
            return ""
    except FileNotFoundError:
        response.status = 404
        response.status_message = "Not Found"
        return ""
        
    
"""
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
                
        except KeyboardInterrupt:
            pass
"""

def accept_wrapper(sock: socket.socket):
    conn, addr = sock.accept()
    print(f"Connection Accepted from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key: selectors.SelectorKey, mask):
    sock: socket.socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            request = request_parser(recv_data)
            response = HttpResponse()
            f = get_file_on_path(response, request.request_target)
            try:
                response_bytes = bytes(f"HTTP/{response.HTTP_VERSION} {response.status} {response.status_message}\r\nDate: {response.request_date}\r\nServer: {response.server_name}\r\nLast-Modified: {response.modified_date}\r\nAccept-Ranges: {response.acc_ranges}\r\nContent-Type: {response.content_type}\r\n\r\n", "ISO-8859-1")+f.read()
            except:
                response_bytes = bytes(f"HTTP/{response.HTTP_VERSION} {response.status} {response.status_message}\r\nDate: {response.request_date}\r\nServer: {response.server_name}\r\nLast-Modified: {response.modified_date}\r\nAccept-Ranges: {response.acc_ranges}\r\nContent-Type: {response.content_type}\r\n\r\n", "ISO-8859-1")
            data.outb += response_bytes
            

        else:
            print(f"Closing Connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
            sel.unregister(sock)
            sock.close()

def main():
    #host, port = sys.argv[1].split(":")[0], int(sys.argv[1].split(":")[1])
    host,port = "10.106.1.91", 8080
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host,port))
    lsock.listen()
    print(f"[{datetime.datetime.now()}] HTTP Server started on {host}:{port}")
    print(f"[{datetime.datetime.now()}] Access Server on http://{host}:{port}")
    print(f"[{datetime.datetime.now()}] Press CONTROL-C to exit server")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key,mask)
    except KeyboardInterrupt:
        print("Server Closing")

if __name__ == "__main__":
    main()