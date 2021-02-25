from json import dumps
from os import error

import requests
from bs4 import BeautifulSoup

from libs.cmdLineOutput import errorMessage, neutralMessage, positiveMessage


class CongressAPI:
    def __init__(self, query: str, page: int = 1) -> None:
        self.page = page
        self.query = query
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&pageSize=250&page={}&q={}".format(
            self.page, self.query
        )

    def sendRequest(self) -> list:
        print(neutralMessage(message="Sending GET request to {}".format(self.url)))
        try:
            req = requests.get(self.url)
        except Exception as e:
            print(
                errorMessage(
                    message="Failed to get {}: ".format(self.url) + e.__str__()
                )
            )

        soup = BeautifulSoup(markup=req.content, features="lxml")
        return [soup, req]

    def incrementPage(self) -> int:
        self.page += 1
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&pageSize=250&page={}&q={}".format(
            self.page, self.query
        )
        return self.page

    def get_CurrentPage(self) -> int:
        return self.page
