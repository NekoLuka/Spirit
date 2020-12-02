import socket
import threading
from Spirit.requestDecoder import requestDecoder
from Spirit.responseEncoder import responseEncoder

# Main class with all logic to run a server
class spirit:
    def __init__(self, host="", port=80):
        self.host = host
        self.port = port
        self.routes = {}

        # Configuration variables
        self.localFileDirectory = ""
        self.custom404 = self.__custom404
        self.custom500 = self.__custom500

    # Set the url to fire the function on
    def route(self, url, methods=["POST", "GET"]):
        def wrapper(fn):
            self.routes[url] = {"function": fn, "methods": methods}
            return fn
        return wrapper

    # Main function for handling a connection
    def __run(self, link):
        header = requestDecoder(link)
        try:
            route = self.routes[header.url]

            if header.method in route["methods"]:
                try:
                    val = route["function"](header)
                    if type(val) is str:
                        data = responseEncoder()
                        data.setData(val)
                        link.sendall(data.getData())
                    elif type(val) is responseEncoder:
                        link.sendall(val.getData())
                    elif type(val) is bytes:
                        link.sendall(val)
                    else:
                        link.sendall(responseEncoder().getData())
                except Exception as e:
                    print(e)
                    link.sendall(self.custom500(header).getData())
            else:
                response = responseEncoder("405 Method Not Allowed")
                response.setHeader("Allow", ",".join(route["methods"]))
                response.setData("405 method not allowed")
                link.sendall(response.getData())
        except Exception as e:
            print(e)
            try:
                data = responseEncoder()
                data.setDataFromFile(self.localFileDirectory + header.url[1:], header.header["Accept"].split(",")[0])
                link.sendall(data.getData())
            except Exception as e:
                print(e)
                link.sendall(self.custom404(header).getData())

        link.close()
        return

    # Function to cal to start the server
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(10)

        while True:
            try:
                link, ip = sock.accept()
                threading.Thread(target=self.__run, args=(link,)).start()
            except Exception as e:
                print(e)
                continue

    # Function to configure the server
    def configure(self, localFileLocation: str, custom404Function):
        self.localFileDirectory = localFileLocation
        self.custom404 = custom404Function

    def __custom404(self, context: requestDecoder) -> responseEncoder:
        data = responseEncoder("404 Not Found")
        data.setData('404 not found')
        return data

    def __custom500(self, context: requestDecoder) -> responseEncoder:
        response = responseEncoder("503 Internal Server Error")
        response.setData("503 internal server error")
        return response