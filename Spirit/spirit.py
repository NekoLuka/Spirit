import socket
import ssl
import threading
import re
import uuid
import base64
from Spirit.requestDecoder import requestDecoder
from Spirit.responseEncoder import responseEncoder
from Spirit.logger import logger
import Spirit.statusFunctions as status
from Spirit.consts import statusCode

# Main class with all logic to run a server
class spirit:
    def __init__(self, host: str="", port: int=80, SSL: bool=False, autoRedirectToSSL: bool=False, SSLRedirectPort: int=80):
        self.host = host
        self.port = port
        self.backlog = 10
        self.SSL = SSL
        self.autoRedirectToSSL = autoRedirectToSSL
        self.SSLRedirectPort = SSLRedirectPort
        self.certChain = ""
        self.certKey = ""
        self.localFileDirectory = ""

        self.__routes = []
        self.__functions = {}
        self.__statusFunctions = {
            "404": status.default404,
            "405": status.default405,
            "500": status.default500
        }

        self.__ipv = 4
        self.listFile = ""
        self.useBlackList = False
        self.blackList = []
        self.useWhiteList = False
        self.whiteList = []

        logger.info(f"Initializing Spirit on port {self.port} and host {self.host if not host == '' else '0.0.0.0'}")

    # Set the url to fire the function on
    def route(self, url: str, methods: list=["POST", "GET"]):
        targetID = uuid.uuid4().hex
        pattern = "^" + url + "$"
        vars = []

        while True:
            if varStart := pattern.find("<"):
                if varStart == -1:
                    break
                varEnd = pattern.find(">") + 1
                vars.append(pattern[varStart+1:varEnd-1])
                pattern = pattern.replace(pattern[varStart:varEnd], r"(\w+)")

        self.__routes.append({"pattern": pattern, "var": vars, "methods": methods, "target": targetID, "authorized": False})

        def wrapper(fn):
            self.__functions[targetID] = fn
            return fn
        return wrapper

    def authorizedRoute(self, credentials, realm: str, url: str, methods: list=["POST", "GET"]):
        targetID = uuid.uuid4().hex
        pattern = "^" + url + "$"
        vars = []

        while True:
            if varStart := pattern.find("<"):
                if varStart == -1:
                    break
                varEnd = pattern.find(">") + 1
                vars.append(pattern[varStart+1:varEnd-1])
                pattern = pattern.replace(pattern[varStart:varEnd], r"(\w+)")

        self.__routes.append({
            "pattern": pattern,
            "var": vars,
            "methods": methods,
            "target": targetID,
            "authorized": True,
            "function": callable(credentials),
            "credentials": credentials,
            "realm": realm
        })

        def wrapper(fn):
            self.__functions[targetID] = fn
            return fn
        return wrapper

    # Set the function to fire on a certain status
    def status(self, status: int):
        def wrapper(fn):
            self.__statusFunctions[str(status)] = fn
            return fn
        return wrapper

    # Main function for handling a connection
    def __run(self, link, ip):
        ipv = self.__ipv
        if self.__ipv == 6:
            if match := re.search(r"(\d+\.\d+\.\d+\.\d+$)", ip):
                ip = match.group(1)
                ipv = 4

        if self.useBlackList:
            if ip in self.blackList:
                link.close()
                return
        elif self.useWhiteList:
            if not ip in self.whiteList:
                link.close()
                return

        try:
            header = requestDecoder(link, ip, ipv)
            logger.info(f"{header.ip} requested '{header.url}'")
        except Exception as e:
            link.close()
            return

        for route in self.__routes:
            if match := re.search(route["pattern"], header.url):
                if header.method in route["methods"]:
                    if route["authorized"]:
                        if not header.header["Authorization"]:
                            response = responseEncoder(statusCode[401])
                            response.setHeader("WWW-Authenticate", f"Basic realm=\"{route['realm']}\"")
                            link.sendall(response.getData())
                            link.close()
                            return
                        protocol, authData = header.header["Authorization"].split(" ")
                        if not protocol.lower() == "basic":
                            link.sendall(responseEncoder(statusCode[409]).getData())
                            link.close()
                            return
                        user, password = base64.b64decode(authData.encode()).decode().split(":", 1)
                        if route["function"]:
                            if route["credentials"](user, password):
                                pass
                            else:
                                link.sendall(responseEncoder(statusCode[403]).getData())
                                link.close()
                                return
                        else:
                            if suser := route["credentials"].get(user):
                                if suser == password:
                                    pass
                            else:
                                link.sendall(responseEncoder(statusCode[403]).getData())
                                link.close()
                                return

                    varDict = {route["var"][i]: match.group(i + 1) for i in range(len(route["var"]))}

                    try:
                        val = self.__functions[route["target"]](header, **varDict)
                    except Exception as e:
                        # Handle errors in the user defined function with a internal server error
                        link.sendall(self.__statusFunctions["500"](header).getData())
                        logger.error(f"{e} on url '{header.url}' from {header.ip}")
                        link.close()
                        return

                    try:
                        if type(val) is responseEncoder:
                            link.sendall(val.getData())
                        elif type(val) is str:
                            response = responseEncoder()
                            response.setData(val)
                            link.sendall(response.getData())
                        elif type(val) is bytes:
                            link.sendall(val)
                        else:
                            if header.method == "POST":
                                link.sendall(responseEncoder(statusCode[201]).getData())
                            else:
                                link.sendall(responseEncoder(statusCode[204]).getData())
                        logger.info(f"Successfully handled request for '{header.url}' from {header.ip}")
                        link.close()
                        return
                    except Exception as e:
                        logger.critical(f"{e} on sending data, failed to send reply")
                        link.close()
                        return

                else:
                    link.sendall(self.__statusFunctions["405"](header).getData())
                    logger.info(f"{header.ip} used {header.method} on '{header.url}' which is not allowed")
                    link.close()
                    return

        # Handle looking for file here
        try:
            response = responseEncoder()
            response.setDataFromFile(self.localFileDirectory + header.url[1:], header.header["Accept"].split(",")[0])
            link.sendall(response.getData())
            logger.info(f"Successfully handled request for '{header.url}' from {header.ip}")
        except Exception as e:
            link.sendall(self.__statusFunctions["404"](header).getData())
            logger.info(f"{header.ip} requested '{header.url}', which is unknown")
        finally:
            link.close()
            return

    # Function to cal to start the server
    def run(self):
        if self.useWhiteList and self.useBlackList:
            raise Exception("You can't use a black- and whitelist at the same time")

        if not self.listFile == "":
            with open(self.listFile, "r") as file:
                if self.useWhiteList:
                    for i in file.read().split("\n"):
                        self.whiteList.append(i)
                elif self.useBlackList:
                    for i in file.read().split("\n"):
                        self.blackList.append(i)

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
            self.__ipv = 6
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
        if socket.has_dualstack_ipv6():
            sock = socket.create_server(
                (self.host, self.SSLRedirectPort),
                backlog=self.backlog,
                family=socket.AF_INET6,
                dualstack_ipv6=True
            )
            self.__ipv = 6
        else:
            sock = socket.create_server(
                (self.host, self.port),
                backlog=self.backlog
            )
        while True:
            link, ip = sock.accept()
            header = requestDecoder(link, ip[0])
            link.send(status.defaultRedirect(f"https://{header.header['host']}:{self.port}").getData())
            link.close()