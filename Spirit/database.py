import sqlite3
from Spirit.password import *
from threading import Lock
from Spirit.logger import logger

class database:
    def __salt(self, text):
        return saltPassword(text)

    def __checkSalt(self, text, hash):
        return 1 if checkPassword(text, hash) else 0

    def __init__(self, dbName: str="", inMemory: bool=False, autoCommit: bool=False, timeOut: int=-1):
        self.__lock = Lock()
        self.__timeOut = timeOut
        self.__autoCommit = autoCommit

        self.__conn = sqlite3.connect(dbName if not inMemory else ":memory:", check_same_thread=False)
        self.__conn.create_function("salt", 1, self.__salt)
        self.__conn.create_function("desalt", 2, self.__checkSalt)
        self.__conn.isolation_level = None if autoCommit else "DEFERRED"
        self.cursor = self.__conn.cursor()

    def addSQLFunction(self, name: str, func: object, parameterCount: int) -> None:
        self.__conn.create_function(name, parameterCount, func)

    def quarry(self, quarry: str, values: list=[], fetch: bool=False):
        self.__lock.acquire(timeout=self.__timeOut)
        try:
            if fetch:
                data = self.cursor.execute(quarry, values).fetchall()
                if self.__autoCommit: self.__lock.release()
                return data
            else:
                self.cursor.execute(quarry, values)
                if self.__autoCommit: self.__lock.release()
                return True
        except Exception as e:
            logger.error(str(e))
            self.__conn.rollback()
            self.__lock.release()
            return False

    def commit(self):
        self.__conn.commit()
        self.__lock.release()

    def rollback(self):
        self.__conn.rollback()
        self.__lock.release()


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
    def cast(value1, value2):
        return f"{value1} AS {value2}"

    @staticmethod
    def createTable(name: str, columns: list, temporary: bool=False, ifNotExists: bool=True,  rowid: bool=True) -> str:
        return f"CREATE{' TEMP' if temporary else ''} TABLE{' IF NOT EXISTS' if ifNotExists else ''} " \
               f"{name} ({', '.join(columns)}) {'WITHOUT ROWID' if not rowid else ''}"

    @staticmethod
    def dropTable(name: str) -> str:
        return f"DROP TABLE IF EXISTS {name}"

    @staticmethod
    def addColumn(name: str, column: str) -> str:
        return f"ALTER TABLE {name} ADD COLUMN {column}"

    @staticmethod
    def renameTable(name: str, newName: str) -> str:
        return f"ALTER TABLE {name} RENAME TO {newName}"

    @staticmethod
    def insert(name: str, columns: list) -> str:
        return f"INSERT INTO {name} ({', '.join(columns)}) VALUES ({', '.join(['?' for i in range(len(columns))])})"

    @staticmethod
    def select(name: str, columns: list, condition: str="", order: str="", limit: int=0):
        return f"SELECT {', '.join(columns)} FROM {name} {f'WHERE {condition}' if not condition == '' else ''}" \
               f"{f' ORDER BY {order}' if not order == '' else ''}{f' LIMIT {limit}' if limit else ''}"

    @staticmethod
    def delete(name: str, condition: str=""):
        return f"DELETE FROM {name} {f'WHERE {condition}' if not condition == '' else ''}"

    @staticmethod
    def update(name: str, column: str, condition: str=""):
        return f"UPDATE {name} SET {column} = ? {f'WHERE {condition}' if not condition == '' else ''}"

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

    class operators:
        class arithmetic:
            @staticmethod
            def add(value1, value2):
                return f"{value1} + {value2}"

            @staticmethod
            def subtract(value1, value2):
                return f"{value1} - {value2}"

            @staticmethod
            def multiply(value1, value2):
                return f"{value1} * {value2}"

            @staticmethod
            def division(value1, value2):
                return f"{value1} / {value2}"

            @staticmethod
            def modulus(value1, value2):
                return f"{value1} % {value2}"

        class comparison:
            @staticmethod
            def equal(value1, value2):
                return f"{value1} == {value2}"

            @staticmethod
            def notEqual(value1, value2):
                return f"{value1} != {value2}"

            @staticmethod
            def greater(value1, value2):
                return f"{value1} > {value2}"

            @staticmethod
            def less(value1, value2):
                return f"{value1} < {value2}"

            @staticmethod
            def greaterOrEqual(value1, value2):
                return f"{value1} >= {value2}"

            @staticmethod
            def lessOrEqual(value1, value2):
                return f"{value1} <= {value2}"

            @staticmethod
            def notGreater(value1, value2):
                return f"{value1} !> {value2}"

            @staticmethod
            def notLess(value1, value2):
                return f"{value1} !< {value2}"