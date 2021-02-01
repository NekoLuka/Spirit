from Spirit.responseEncoder import responseEncoder
from Spirit.requestDecoder import requestDecoder
from Spirit.database import database, quarryBuilder
import time
import pickle
'''
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

'''

class session:
    __db = None

    def __init__(self, context: requestDecoder, response: responseEncoder, dbFile: str="sessions.db"):
        self.close = False
        if self.__db is None:
            self.__db = database(dbFile, autoCommit=True)

        self.__db.quarry(quarryBuilder.createTable(
            "sessions", [
                quarryBuilder.column("updateTime", quarryBuilder.types.INT),
                quarryBuilder.column("key", quarryBuilder.types.INT, unique=True)
            ]
        ))

        self.__context = context
        self.__response = response

        self.__key = self.__context.cookie["SpiritSession"]
        if not self.__key:
            self.__key = int(time.time()) + 69420
            self.__response.setCookie("SpiritSession", str(self.__key))

    def destroy(self):
        return self.__db.quarry(quarryBuilder.delete(
            "sessions", quarryBuilder.operators.comparison.equal("key", self.__key)
        ))

    def __getitem__(self, item):
        item = self.__db.quarry(f"SELECT {item} FROM sessions", fetch=True)[0][0]
        return pickle.loads(bytes.fromhex(item))

    def __setitem__(self, name, value):
        cols = [j[1] for j in [i for i in self.__db.quarry("pragma table_info('sessions')", fetch=True)]]
        if name not in cols:
            if not self.__db.quarry(quarryBuilder.addColumn(
                "sessions",
                quarryBuilder.column(name, quarryBuilder.types.STRING)
            )): raise Exception("Quarry failed")

        ctime = str(int(time.time()))
        cValue = bytes.hex(pickle.dumps(value))
        if not self.__db.quarry(f"INSERT INTO sessions (updateTime, key, {name}) VALUES ({ctime}, {str(self.__key)}, '{cValue}') "
                                f"ON CONFLICT(key) DO UPDATE SET "
                                f"updateTime={ctime}, {name}=excluded.{name} "
                                f"WHERE sessions.key == excluded.key"): raise Exception("Quarry failed")

    def __del__(self):
        if self.close:
            self.__db.cursor.close()
            self.__db = None

