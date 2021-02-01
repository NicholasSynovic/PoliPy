import sqlite3
from sqlite3 import Connection, OperationalError


class DatabaseConnector:
    def __init__(self, databaseFileName: str) -> None:
        self.file = databaseFileName
        self.createDatabase()
        self.databaseConnection = sqlite3.connect(self.file)

    def createDatabase(self) -> bool:
        try:
            with open(self.file, "r") as database:
                database.close()
            return False
        except FileNotFoundError:
            with open(self.file, "w") as database:
                database.close()
            return True

    def executeSQL(
        self,
        sql: str,
        options: tuple = None,
    ) -> bool:
        connection = self.databaseConnection
        try:
            if options is None:
                connection.execute(sql)
            else:
                connection.execute(sql, options)
        except OperationalError:
            return False
        connection.commit()
        return True

    def closeDatabaseConnection(self, databaseConnection: Connection) -> bool:
        databaseConnection.close()
        return True
