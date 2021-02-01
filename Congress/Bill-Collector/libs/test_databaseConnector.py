import unittest
import os
from sqlite3 import Connection

import databaseConnector


class Test_CongressAPI(unittest.TestCase):
    def test_Init_1(self):
        d1 = databaseConnector.DatabaseConnector(databaseFileName="test2.db")
        self.assertTrue("test2.db", d1.file)
        self.assertIs(Connection, type(d1.databaseConnection))
        d1.databaseConnection.close()
        os.remove("test2.db")

    def test_Init_2(self):
        d2 = databaseConnector.DatabaseConnector(databaseFileName="test1.db")
        self.assertTrue("test1.db", d2.file)
        self.assertIs(Connection, type(d2.databaseConnection))
        d2.databaseConnection.close()

    def test_ExecuteSQL(self):
        d3 = databaseConnector.DatabaseConnector(databaseFileName="test1.db")
        self.assertTrue(
            d3.executeSQL(
                sql="CREATE TABLE Test (ID INTEGER, Test TEXT, PRIMARY KEY(ID))"
            )
        )
        self.assertTrue(
            d3.executeSQL(
                sql="INSERT OR IGNORE INTO Test (ID, Test) VALUES (?,?)",
                options=(0, "Hello World"),
            )
        )

        d3.databaseConnection.close()
        os.remove("test1.db")


if __name__ == "__main__":
    temp = open("test1.db", "w")
    temp.close()
    unittest.main()
