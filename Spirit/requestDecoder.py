import socket
from Spirit.consts import urlDecodeHexTable

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
                for i in get.split("&"):
                    if i == '':
                        continue
                    key, value = self.__parseUrl(i.split("=", 1))
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
                    self.cookie[name] = value
        except:
            pass

        try:
            contentType = self.header["content-type"]
            contentLength = int(self.header["content-length"])
            if "application/x-www-form-urlencoded" in contentType:
                postData = link.recv(contentLength).decode("utf-8")
                for i in postData.split("&"):
                    if i == '':
                        continue
                    name, value = self.__parseUrl(i.split("=", 1))
                    self.post[name] = value

            elif "multipart/form-data" in contentType:
                formData = link.recv(contentLength)
                formDataList = formData.split(
                    self.header["content-type"].split(";")[1].strip().split("=")[1].encode()
                )
                for i in formDataList:
                    if i == b"--" or i == b"":
                        continue

                    header, value = i.split(b"\r\n\r\n")
                    headerList = header.split(b"\r\n")
                    while b"" in headerList:
                        headerList.remove(b"")
                    headerDict = {value.split(b":", 1)[0].strip().decode("utf-8"): value.split(b":", 1)[1].strip().decode("utf-8") for value in headerList}

                    fieldName = headerDict.get("content-disposition").split(";")[1].strip().split("=")[1].strip("\"")
                    try:
                        fileName = headerDict.get("content-disposition").split(";")[2].strip().split("=")[1].strip("\"")
                        fileContentType = headerDict.get("content-type")
                        self.file[fieldName] = {"name": fileName, "mimeType": fileContentType, "data": value[:-4]}
                    except:
                        self.post[fieldName] = value[:-4].decode("utf-8")

        except:
            pass

        self.get = self.__data(self.get)
        self.post = self.__data(self.post)
        self.header = self.__data(self.header)
        self.cookie = self.__data(self.cookie)
        self.file = self.__file(self.file)


    def __parseUrl(self, urlList: list) -> list:
        returnList = []
        for i in urlList:
            length = len(i)
            count = 0
            parsedString = ""
            while count < length:
                if i[count] == "%":
                    try:
                        decodedCharacter = urlDecodeHexTable[i[count:count+3]]
                        count += 2
                        parsedString += decodedCharacter
                    except:
                        parsedString += "%"
                elif i[count] == "+":
                    parsedString += " "
                else:
                    parsedString += i[count]
                count += 1
            returnList.append(parsedString)
        return returnList

