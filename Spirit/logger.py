import time

class logger:
    DISABLED = 0
    INFO = 1
    CRITICAL = 2
    ERROR = 4
    WARNING = 8
    DEBUG = 16

    __reportType = 15

    __fileName = "Spirit.log"
    __fileObject = None

    @classmethod
    def setReportTypes(cls, type: int=15):
        cls.__reportType = type

    @classmethod
    def setLogFile(cls, path: str="Spirit.log"):
        cls.__fileName = path

    @classmethod
    def info(cls, message: str):
        data = time.ctime() + " - INFO: " + message + "\n"
        if cls.__reportType & cls.INFO == cls.INFO:
            print(data, end="")
            if cls.__fileObject:
                cls.__fileObject.write(data)

    @classmethod
    def critical(cls, message: str):
        data = time.ctime() + " - CRITICAL: " + message + "\n"
        if cls.__reportType & cls.CRITICAL == cls.CRITICAL:
            print(data, end="")
            if cls.__fileObject:
                cls.__fileObject.write(data)

    @classmethod
    def error(cls, message: str):
        data = time.ctime() + " - ERROR: " + message + "\n"
        if cls.__reportType & cls.ERROR == cls.ERROR:
            print(data, end="")
            if cls.__fileObject:
                cls.__fileObject.write(data)

    @classmethod
    def warning(cls, message: str):
        data = time.ctime() + " - WARNING: " + message + "\n"
        if cls.__reportType & cls.WARNING == cls.WARNING:
            print(data, end="")
            if cls.__fileObject:
                cls.__fileObject.write(data)

    @classmethod
    def debug(cls, message: str):
        data = time.ctime() + " - DEBUG: " + message + "\n"
        if cls.__reportType & cls.DEBUG == cls.DEBUG:
            print(data, end="")
            if cls.__fileObject:
                cls.__fileObject.write(data)

    @classmethod
    def run(cls):
        cls.__fileObject = open(cls.__fileName, "a")

