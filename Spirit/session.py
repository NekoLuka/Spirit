from Spirit.responseEncoder import responseEncoder
from Spirit.requestDecoder import requestDecoder
from Spirit.logger import logger
import uuid
import json
import os
import time
import threading
import stat

# Class for managing sessions
class session:
    sessionFolder = "sessions/"
    __sessionFolderCreated = False
    autoCleanupAfter = 86400
    autoCleanupRunTimer = 300
    autoCleanupEnable = True

    @classmethod
    def cleanup(cls):
        logger.info("Started automatic session cleanup")
        while True:
            time.sleep(cls.autoCleanupRunTimer)
            if not cls.autoCleanupEnable:
                continue

            if not os.path.isdir(cls.sessionFolder):
                os.mkdir(cls.sessionFolder)
                continue

            for i in os.listdir(cls.sessionFolder):
                lastAccessTime = os.stat(cls.sessionFolder + i)[stat.ST_ATIME]
                if (int(time.time()) - lastAccessTime) >= cls.autoCleanupAfter:
                    os.remove(cls.sessionFolder + i)



    def __init__(self, context: requestDecoder, response: responseEncoder):
        self.__sessionVars = {}
        self.__sessionVarsBackup = {}

        try:
            self.spiritKey = context.cookie["spirit_key"]

            with open(self.sessionFolder + self.spiritKey, "r") as file:
                self.__sessionVarsBackup = json.load(file)
                file.seek(0)
                self.__sessionVars = json.load(file)
        except Exception as e:
            self.spiritKey = uuid.uuid4().hex
            response.setCookie("spirit_key", self.spiritKey)

        self.__unset = False
        self.__response = response

    def destroy(self):
        self.__response.setCookie("spirit_key", "", ["Expires=Thu, 01 Jan 1970 00:00:00 UTC"])
        os.remove(self.sessionFolder + self.spiritKey)
        self.__unset = True

    def __getitem__(self, item):
        return self.__sessionVars.get(item)

    def __setitem__(self, key, value):
        self.__sessionVars[key] = value

    def __del__(self):
        if self.__sessionVars != self.__sessionVarsBackup and not self.__unset:
            with open(self.sessionFolder + self.spiritKey, "w") as file:
                json.dump(self.__sessionVars, file)

threading.Thread(target=session.cleanup).start()