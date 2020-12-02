# Class to encode a HTTP response
class responseEncoder:
    def __init__(self, status: str="200 OK", protocol: str="HTTP/1.0"):
        self.__stats = status
        self.__protocol = protocol
        self.__data = b""
        self.__dataSize = 0
        self.__mimeType = "text/plain"
        self.__headers = []
        self.__cookies = []

    # Set data to send from a string
    def setData(self, data: str, mimeType: str="text/plain") -> None:
        self.__data = str(data).encode("utf-8")
        self.__mimeType = mimeType
        self.__dataSize += len(self.__data)

    # Read a file, and set it as data
    def setDataFromFile(self, fileName: str, mimeType: str) -> None:
        self.__mimeType = mimeType
        with open(fileName, "rb") as file:
            self.__data = file.read()
            file.close()
        self.__dataSize += len(self.__data)

    # Set a single header
    def setHeader(self, headerName: str, headerValue: str) -> None:
        self.__headers.append(f"{headerName}: {headerValue}")

    # Set a list of correctly formatted headers at once
    def setHeaders(self, headers: list) -> None:
        for i in headers:
            self.__headers.append(i)

    # Set a single cookie
    def setCookie(self, cookieName: str, cookieValue: str, cookieArguments: list=[]) -> None:
        if len(cookieArguments) == 0:
            self.__cookies.append(f"{cookieName}={cookieValue}")
        else:
            cookie = f"{cookieName}={cookieValue}"
            for i in cookieArguments:
                cookie += f"; {i}"
            self.__cookies.append(cookie)

    # Set a list of correctly formatted cookies at once
    def setCookies(self, cookies: list) -> None:
        for i in cookies:
            self.__cookies.append(i)

    # Return the formatted request with the set parameters
    def getData(self) -> bytes:
        header = f"{self.__protocol} {self.__stats}\r\nServer: Spirit\r\nContent-Type: {self.__mimeType}\r\nContent-Length: {self.__dataSize}\r\n"

        for i in self.__headers:
            header += f"{i}\r\n"

        for i in self.__cookies:
            header += f"Set-Cookie: {i}\r\n"

        header += "\r\n"
        return header.encode("utf-8") + self.__data