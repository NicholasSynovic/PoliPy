import unittest

import bs4
import requests

import congressAPI


class Test_CongressAPI(unittest.TestCase):
    def test_Init(self):
        c1 = congressAPI.CongressAPI()
        c2 = congressAPI.CongressAPI(test1="test1", test2=["test2", "test3"])
        self.assertEqual({}, c1.query)
        self.assertEqual(
            r"https://www.congress.gov/search?searchResultViewType=expanded&q={}",
            c1.url,
        )
        self.assertEqual("test1", c2.query["test1"])
        self.assertEqual(["test2", "test3"], c2.query["test2"])
        self.assertEqual(
            r'https://www.congress.gov/search?searchResultViewType=expanded&q={"test1": "test1", "test2": ["test2", "test3"]}',
            c2.url,
        )

    def test_SendRequest(self):
        c3 = congressAPI.CongressAPI().sendRequest()
        self.assertIs(list, type(c3))
        self.assertEqual(200, c3[1].status_code)


if __name__ == "__main__":
    unittest.main()
