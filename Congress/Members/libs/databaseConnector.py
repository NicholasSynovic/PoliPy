import sqlite3

from libs.cmdLineOutput import errorMessage, neutralMessage, positiveMessage


class DatabaseConnector:
    def __init__(self, databaseFileName: str) -> None:
        self.file = r"database/" + databaseFileName
        print(neutralMessage(message="Trying to find file: {}".format(self.file)))
        try:
            with open(self.file, "r") as database:
                print(
                    positiveMessage(
                        message="File {} already exists. Will append data to {}".format(
                            self.file, self.file
                        )
                    )
                )
                database.close()
        except FileNotFoundError:
            with open(self.file, "w") as database:
                print(positiveMessage(message="Creating file {}".format(self.file)))
                database.close()
        self.databaseConnection = sqlite3.connect(self.file)

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
        except Exception as e:
            print(
                errorMessage(
                    message="Exception raised with file {} when executing SQL: ".format(
                        self.file
                    )
                    + e.__str__()
                )
            )
            return False
            quit(1)
        connection.commit()
        return True
