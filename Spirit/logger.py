import threading, time

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

    __logQue = []

    __shutdown = False

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
    def shutdown(cls):
        cls.__shutdown = True

    @classmethod
    def info(cls, message: str):
        data = time.ctime() + " - INFO: " + message + "\n"
        cls.__logQue.append((cls.INFO, data))
        if cls.INFO <= cls.__reportLevel:
            print(data)

    @classmethod
    def critical(cls, message: str):
        data = time.ctime() + " - CRITICAL: " + message + "\n"
        cls.__logQue.append((cls.CRITICAL, data))
        if cls.CRITICAL <= cls.__reportLevel:
            print(data)

    @classmethod
    def error(cls, message: str):
        data = time.ctime() + " - ERROR: " + message + "\n"
        cls.__logQue.append((cls.ERROR, data))
        if cls.ERROR <= cls.__reportLevel:
            print(data)

    @classmethod
    def warning(cls, message: str):
        data = time.ctime() + " - WARNING: " + message + "\n"
        cls.__logQue.append((cls.WARNING, data))
        if cls.WARNING <= cls.__reportLevel:
            print(data)

    @classmethod
    def debug(cls, message: str):
        data = time.ctime() + " - DEBUG: " + message + "\n"
        cls.__logQue.append((cls.DEBUG, data))
        if cls.DEBUG <= cls.__reportLevel:
            print(data)

    @classmethod
    def startLogger(cls):
        threading.Thread(target=cls.__logger).start()

    @classmethod
    def __logger(cls):
        with open(cls.__fileName, 'a') as file:
            while not cls.__shutdown:
                while len(cls.__logQue) > 0:
                    message = cls.__logQue[0]
                    if message[0] <= cls.__logLevel:
                        file.write(message[1])
                    cls.__logQue.pop(0)
                time.sleep(1)
            file.close()
