import sqlite3, datetime

class dataBase:
    sqliteVersion = sqlite3.version

    def __init__(dbName: str, autoCommit: bool=False):
        self.__autoCommit = autoCommit
        self.__conn = sqlite3.connect(dbName)
        
    def createTable(name: str, **kwargs):
        self.__conn.execute(f"CREATE TABLE IF NOT EXISTS {name} (" + ", ".join([f"{name} {value}" for name, value in kwargs.items()]) + ")")
        if self.__autoCommit:
            self.commit()

    def insert(name: str, **kwargs):
        self.__conn.execute(f"INSERT INTO {name} (" + 
                            ", ".join([name for name in kwargs.keys()]) + 
                            ") VALUES (" + 
                            ", ".join(["?" for i in len(kwargs)]) + 
                            ")", [i for i in kwargs.values()])
        if self.__autoCommit:
            self.commit()

    def commit():
        self.__conn.commit()

    

    