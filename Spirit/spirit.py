import socket
import ssl
import threading
from Spirit.requestDecoder import requestDecoder
from Spirit.responseEncoder import responseEncoder
from Spirit.logger import logger
from Spirit.redirect import redirect

# Main class with all logic to run a server
class spirit:
    def __init__(self, host: str="", port: int=80, SSL: bool=False, autoRedirectToSSL: bool=False, SSLRedirectPort: int=80):
        self.host = host
        self.port = port
        self.backlog = 10
        self.routes = {}
        self.SSL = SSL
        self.autoRedirectToSSL = autoRedirectToSSL
        self.SSLRedirectPort = SSLRedirectPort
        self.certChain = ""
        self.certKey = ""

        logger.info(f"Initializing Spirit on port {self.port} and host {self.host if not host == '' else '0.0.0.0'}")

        # Configuration variables
        self.localFileDirectory = ""
        self.custom404 = self.__custom404
        self.custom500 = self.__custom500

    # Set the url to fire the function on
    def route(self, url: str, methods: list=["POST", "GET"]):
        def wrapper(fn):
            self.routes[url] = {"function": fn, "methods": methods}
            return fn
        return wrapper

    # Main function for handling a connection
    def __run(self, link, ip):
        header = requestDecoder(link, ip)
        logger.info(f"{header.ip} requested '{header.url}'")
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
                    logger.info(f"Successfully handled request for '{header.url}' from {header.ip}")
                except Exception as e:
                    link.sendall(self.custom500(header).getData())
                    logger.error(f"{e} on url {header.url} from {header.ip}")

            else:
                response = responseEncoder("405 Method Not Allowed")
                response.setHeader("Allow", ",".join(route["methods"]))
                response.setData("405 method not allowed")
                link.sendall(response.getData())
                logger.info(f"{header.ip} used {header.method} which is not allowed")
        except Exception as e:
            try:
                data = responseEncoder()
                data.setDataFromFile(self.localFileDirectory + header.url[1:], header.header["Accept"].split(",")[0])
                link.sendall(data.getData())
                logger.info(f"Successfully handled request for '{header.url}' from {header.ip}")
            except Exception as e:
                link.sendall(self.custom404(header).getData())
                logger.info(f"{header.ip} requested '{header.url}', which is unknown")

        link.close()
        return

    # Function to cal to start the server
    def run(self):
        if self.SSL:
            sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            sslContext.load_cert_chain(certfile=self.certChain, keyfile=self.certKey)
        else:
            sslContext = None

        if self.autoRedirectToSSL:
            threading.Thread(target=self.__autoRedirect).start()

        if socket.has_dualstack_ipv6():
            sock = socket.create_server(
                (self.host, self.port),
                backlog=self.backlog,
                family=socket.AF_INET6,
                dualstack_ipv6=True
            )
        else:
            sock = socket.create_server(
                (self.host, self.port),
                backlog=self.backlog
            )

        while True:
            try:
                link, ip = sock.accept()
                threading.Thread(target=self.__run, args=(
                    sslContext.wrap_socket(link, server_side=True) if self.SSL else link,
                    ip[0]
                )).start()
            except:
                continue

    def __autoRedirect(self):
        sock = socket.create_server((self.host, self.SSLRedirectPort))
        while True:
            link, ip = sock.accept()
            header = requestDecoder(link, ip[0])
            link.send(redirect(f"https://{header.header['host']}:{self.port}").getData())
            link.close()


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