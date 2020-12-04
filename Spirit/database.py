import sqlite3, datetime
from Spirit.password import *


class database:
    def __salt(self, text):
        return saltPassword(text)

    def __checkSalt(self, text, hash):
        return 1 if checkPassword(text, hash) else 0

    def __logging(self, statement: str):
        pass

    def __init__(self, dbName: str="", autoCommit: bool=False, inMemory: bool=False, logging: bool=False):
        self.__autoCommit = autoCommit
        self.__conn = sqlite3.connect(dbName if not inMemory else ":memory:")
        self.__conn.row_factory = sqlite3.Row
        if logging:
            self.__conn.set_trace_callback(self.__logging)
        self.__conn.create_function("salt", 1, self.__salt)
        self.__conn.create_function("desalt", 2, self.__checkSalt)
        self.__conn.isolation_level = None if autoCommit else "DEFERRED"
        self.cursor = self.__conn.cursor()

    def addSQLFunction(self, name: str, func: object, parameterCount: int) -> None:
        self.__conn.create_function(name, parameterCount, func)

    def quarry(self, quarry: str, values, fetch: bool=True):
        try:
            if fetch:
                return self.cursor.execute(quarry, values).fetchall()
            else:
                self.cursor.execute(quarry, values)
                return True
        except Exception as e:
            return False

    def massQuarry(self, quarry: str, values, fetch: bool=True):
        try:
            if fetch:
                return self.cursor.executemany(quarry, values).fetchall()
            else:
                self.cursor.executemany(quarry, values)
                return True
        except Exception as e:
            return False


class quarryBuilder:
    class types:
        INT = "INTEGER"
        STRING = "TEXT"
        FLOAT = "REAL"
        BIN = "BLOB"
        NULL = "NULL"

    class defaults:
        CURR_TIME = "CURRENT_TIME"
        CURR_DATE = "CURRENT_DATE"
        CURR_TIMESTAMP = "CURRENT_TIMESTAMP"

    SUBSTITUTE = "?"

    @staticmethod
    def createTable(name: str, temporary: bool, ifNotExists: bool, columns: [], rowid: bool=True) -> str:
        return f"CREATE{' TEMP' if temporary else ''} TABLE{' IF NOT EXISTS' if ifNotExists else ''} " \
               f"{name} ({', '.join(columns)}) {'WITHOUT ROWID' if not rowid else ''}"

    @staticmethod
    def dropTable(name):
        return f"DROP TABLE IF EXISTS {name}"

    @staticmethod
    def insert(name: str, columns: []) -> str:
        return f"INSERT INTO {name} ({', '.join(columns)}) VALUES ({', '.join(['?' for i in range(len(columns))])})"

    @staticmethod
    def select(name: str, columns: [], where: str="", order: str="", limit: int=0):
        return f"SELECT {', '.join(columns)} FROM {name} {f'WHERE {where}' if not where == '' else ''}" \
               f"{f' ORDER BY {order}' if not order == '' else ''}{f' LIMIT {limit}' if limit else ''}"

    @staticmethod
    def delete(name: str, where: str=""):
        return f"DELETE FROM {name} {f'WHERE {where}' if not where == '' else ''}"

    @staticmethod
    def column(name: str, type: str, unique: bool=False, primaryKey: bool=False, notNull: bool=False, default="") -> str:
        return f"{name} {type}{' PRIMARY KEY' if primaryKey else ''}{' UNIQUE' if unique else ''}" \
               f"{' NOT NULL' if notNull else ''}{f' DEFAULT {default}' if default != '' else ''}"

    @staticmethod
    def salt(value: str, columnName: str) -> str:
        return f"salt({value}) AS {columnName}"

    @staticmethod
    def desalt(text: str, hash: str, columnName: str):
        return f"desalt({text}, {hash}) AS {columnName}"

    class calender:
        @staticmethod
        def setTime(hour: int, minute: int, second: int) -> str:
            return f"{hour}:{minute}:{second}"

        @staticmethod
        def setDate(year: int, month: int, day: int) -> str:
            return f"{year}-{month}-{day}"

        @staticmethod
        def setTimeStamp(year: int, month: int, day: int, hour: int, minute: int, second: int) -> str:
            return f"{year}-{month}-{day} {hour}:{minute}:{second}"