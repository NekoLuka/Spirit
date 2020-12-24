import time

class logger:
    DISABLED = -1
    INFO = 0
    CRITICAL = 1
    ERROR = 2
    WARNING = 3
    DEBUG = 4

    __reportLevel = 2
    __logLevel = 1

    __fileName = "Spirit.log"
    __fileObject = None

    @classmethod
    def setLogLevel(cls, level: int=1):
        cls.__logLevel = level

    @classmethod
    def setReportLevel(cls, level: int=2):
        cls.__reportLevel = level

    @classmethod
    def setLogFile(cls, path: str="Spirit.log"):
        cls.__fileName = path

    @classmethod
    def info(cls, message: str):
        data = time.ctime() + " - INFO: " + message + "\n"
        if cls.INFO <= cls.__reportLevel:
            print(data)
        if cls.INFO <= cls.__logLevel and cls.__fileObject:
            cls.__fileObject.write(data)

    @classmethod
    def critical(cls, message: str):
        data = time.ctime() + " - CRITICAL: " + message + "\n"
        if cls.CRITICAL <= cls.__reportLevel:
            print(data)
        if cls.CRITICAL <= cls.__logLevel and cls.__fileObject:
            cls.__fileObject.write(data)

    @classmethod
    def error(cls, message: str):
        data = time.ctime() + " - ERROR: " + message + "\n"
        if cls.ERROR <= cls.__reportLevel:
            print(data)
        if cls.ERROR <= cls.__logLevel and cls.__fileObject:
            cls.__fileObject.write(data)

    @classmethod
    def warning(cls, message: str):
        data = time.ctime() + " - WARNING: " + message + "\n"
        if cls.WARNING <= cls.__reportLevel:
            print(data)
        if cls.WARNING <= cls.__logLevel and cls.__fileObject:
            cls.__fileObject.write(data)

    @classmethod
    def debug(cls, message: str):
        data = time.ctime() + " - DEBUG: " + message + "\n"
        if cls.DEBUG <= cls.__reportLevel:
            print(data)
        if cls.DEBUG <= cls.__logLevel and cls.__fileObject:
            cls.__fileObject.write(data)

    @classmethod
    def run(cls):
        cls.__fileObject = open(cls.__fileName, "a")

