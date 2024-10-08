import sys
import jal
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
        self.modified_date = 0
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
            response.content_length = os.path.getsize(path)
            if os.path.splitext(path)[1].strip(".") in ["html","css","js","txt","md"]:
                response.content_type = f"text/{os.path.splitext(path)[1].strip('.')}"
            elif os.path.splitext(path)[1].strip(".") in ["jpeg","png","webp","svg"]:
                response.content_type = f"image/{os.path.splitext(path)[1].strip('.')}"
            response.status, response.status_message = 200, "OK"

            f = open(path,"rb")
            response.modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            return f
        else:
            response.status = 404
            response.status_message = "Not Found"
            return ""
    except FileNotFoundError:
        response.status = 404
        response.status_message = "Not Found"
        return ""
        

def accept_wrapper(sock: socket.socket, logger: jal.Logger):
    conn, addr = sock.accept()
    logger.log(jal.NOTICE,f" Connection Accepted from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key: selectors.SelectorKey, mask, logger: jal.Logger):
    sock: socket.socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                request = request_parser(recv_data)
                
                response = HttpResponse()
                f = get_file_on_path(response, request.request_target)
                try:
                    response_bytes = bytes(f"HTTP/{response.HTTP_VERSION} {response.status} {response.status_message}\r\nDate: {response.request_date}\r\nServer: {response.server_name}\r\nLast-Modified: {response.modified_date}\r\nAccept-Ranges: {response.acc_ranges}\r\nContent-Type: {response.content_type}\r\nCustom-Header: 0\r\n\r\n", "ISO-8859-1")+f.read()
                except:
                    response_bytes = bytes(f"HTTP/{response.HTTP_VERSION} {response.status} {response.status_message}\r\nDate: {response.request_date}\r\nServer: {response.server_name}\r\nLast-Modified: {response.modified_date}\r\nAccept-Ranges: {response.acc_ranges}\r\nContent-Type: {response.content_type}\r\nCustom-Header: 0\r\n\r\n", "ISO-8859-1")
                for i in request.other_headers:
                    if "CensysInspect" in str(i):
                        response_bytes = bytes(f"HTTP/{response.HTTP_VERSION} {response.status} {response.status_message}\r\nDate: {response.request_date}\r\nServer: {response.server_name}\r\nLast-Modified: {response.modified_date}\r\nAccept-Ranges: {response.acc_ranges}\r\nContent-Type: {response.content_type}\r\nCustom-Header: 0\r\n\r\n Hello Censys :)", "ISO-8859-1")



                data.outb += response_bytes
                

            else:
                logger.log(jal.NOTICE,f" Closing Connection to {data.addr}")
                sel.unregister(sock)
                sock.close()
        except:
            logger.log(jal.NOTICE,f" Unexpected Error, Dropping Connection...")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
            sel.unregister(sock)
            sock.close()

def main():
    #host, port = sys.argv[1].split(":")[0], int(sys.argv[1].split(":")[1])
    logger = jal.Logger()
    logger.setup(type=jal.INFO, filenameDirectory = "./", filename = f"{str(datetime.date.today())}.log")


    host,port = "0.0.0.0", 8080
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host,port))
    lsock.listen()
    logger.log(jal.INFO,f"HTTP Server started on {host}:{port}")
    logger.log(jal.INFO,f"Access Server on http://{host}:{port}")
    logger.log(jal.INFO,f"Press CONTROL-C to exit server")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj, logger)
                else:
                    service_connection(key,mask, logger)
    except (KeyboardInterrupt or Exception) as e:
        e.with_traceback(None)
        print("\r", end="")
        logger.log(jal.INFO,f"Server Closing")
        lsock.detach()
        lsock.close()

if __name__ == "__main__":
    main()
