import socket
from urllib.parse import unquote_plus
from email.parser import BytesParser

class requestDecoder:
    class __data:
        def __init__(self, data: dict):
            self.__varData = data

        def __getitem__(self, item: str):
            return self.__varData.get(item.lower())

    class __file:
        def __init__(self, files: dict):
            self.__files = {}
            for name, data in files.items():
                data["size"] = len(data["data"])
                self.__files[name] = data

        def size(self, fieldName: str) -> int:
            return self.__files.get(fieldName).get("size")

        def mimeType(self, fieldName: str) -> str:
            return self.__files.get(fieldName).get("mimeType")

        def fileName(self, fieldName: str) -> str:
            return self.__files.get(fieldName).get("name")

        def data(self, fieldName: str) -> bytes:
            return self.__files.get(fieldName).get("data")

    def __init__(self, link: socket.socket, ip: str="", ipv=4):
        header = b""
        lastByte = b""
        while True:
            tempData = link.recv(1)
            if not tempData:
                raise Exception("No data send")
            if tempData == b"\r":
                continue

            header += tempData
            if lastByte == b"\n" and tempData == b"\n":
                break
            lastByte = tempData

        headerList = header[:-2].decode("utf-8").split("\n")
        self.get = {}
        self.post = {}
        self.file = {}
        self.cookie = {}
        self.header = {}
        self.ip = ip
        self.ipv = ipv

        self.method, self.url, self.protocol = headerList[0].split(" ")

        if "?" in self.url:
            self.url, get = self.url.split("?")
            if not get == '':
                get = unquote_plus(get)
                for i in get.split("&"):
                    if i == '':
                        continue
                    key, value = i.split("=", 1)
                    self.get[key] = value

        headerList.pop(0)

        for i in headerList:
            if i == '':
                continue
            name, value = i.split(":", 1)
            self.header[name.lower()] = value.strip()

        try:
            cookieList = self.header["cookie"].replace(" ", "").split(";")
            if not cookieList[0] == '':
                for i in cookieList:
                    name, value = i.split("=")
                    self.cookie[name.lower()] = value
        except:
            pass

        try:
            contentType = str(self.header["content-type"])
            contentLength = int(self.header["content-length"])
            if "application/x-www-form-urlencoded" in contentType:
                postData = link.recv(contentLength).decode("utf-8")
                for i in postData.split("&"):
                    if i == '':
                        continue
                    name, value = i.split("=", 1)
                    self.post[name.lower()] = unquote_plus(value)

            elif "multipart/form-data" in contentType:
                formData = b""
                while len(formData) < contentLength:
                    formData += link.recv(512)
                boundary = contentType.split(";")[1].split("=")[1].strip().encode()
                formFields = formData.split(boundary)

                for i in formFields:
                    if i == b"--" or i == b"":
                        continue

                    headers, data = i.split(b"\r\n\r\n", 1)
                    headers = headers.decode("utf-8").split("\r\n")
                    headers = [i for i in headers if not i == ""]
                    headers = {name.strip().lower(): value.strip() for name, value in [i.split(":") for i in headers]}
                    fieldName, fileName = headers["content-disposition"].split(";")[1:]
                    fieldName = fieldName.split("=", 1)[1].replace('"', "").strip()
                    fileName = fileName.split("=", 1)[1].replace('"', "").strip()
                    mimeType = headers["content-type"]
                    self.file[fieldName] = {"name": fileName, "mimeType": mimeType, "data": data[:-2]}

        except:
            pass

        self.get = self.__data(self.get)
        self.post = self.__data(self.post)
        self.header = self.__data(self.header)
        self.cookie = self.__data(self.cookie)
        self.file = self.__file(self.file)
