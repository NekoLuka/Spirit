import sqlite3, datetime

class database:
    def __init__(self, dbName: str, autoCommit: bool=False):
        self.__autoCommit = autoCommit
        self.__conn = sqlite3.connect(dbName)
        
    def createTable(self, name: str, **kwargs):
        self.__conn.execute(f"CREATE TABLE IF NOT EXISTS {name} (" + ", ".join([f"{name} {value}" for name, value in kwargs.items()]) + ")")
        if self.__autoCommit:
            self.commit()

    def insert(self, name: str, **kwargs):
        self.__conn.execute(f"INSERT INTO {name} (" + 
                            ", ".join([name for name in kwargs.keys()]) + 
                            ") VALUES (" + 
                            ", ".join(["?" for i in range(len(kwargs))]) + 
                            ")", [i for i in kwargs.values()])
        if self.__autoCommit:
            self.commit()

    def commit(self):
        self.__conn.commit()

    def rollBack(self):
        self.__conn.rollback()

    

    