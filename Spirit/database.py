import sqlite3, datetime

class database:
    def __init__(self, dbName: str, autoCommit: bool=False):
        self.__autoCommit = autoCommit
        self.__conn = sqlite3.connect(dbName)
        self.__conn.row_factory = sqlite3.Row
        self.__conn.isolation_level = None if autoCommit else "DEFERRED"
        self.__cursor = self.__conn.cursor()
        
    def createTable(self, name: str, **kwargs) -> bool:
        self.__conn.execute(f"CREATE TABLE IF NOT EXISTS {name} (" + ", ".join([f"{name} {value}" for name, value in kwargs.items()]) + ")")

    def insert(self, name: str, **kwargs) -> bool:
        self.__conn.execute(f"INSERT INTO {name} (" + 
                            ", ".join([name for name in kwargs.keys()]) + 
                            ") VALUES (" + 
                            ", ".join(["?" for i in range(len(kwargs))]) + 
                            ")", [i for i in kwargs.values()])

    def commit(self):
        self.__conn.commit()

    def rollBack(self):
        self.__conn.rollback()

    

    