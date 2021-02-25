from json import dumps

import requests
from bs4 import BeautifulSoup


class CongressAPI:
    def __init__(self, query: str, page: int = 1) -> None:  # TODO: Fix test
        self.page = page
        self.query = query
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&pageSize=250&page={}&q={}".format(
            self.page, self.query
        )

    def sendRequest(self) -> list:
        req = requests.get(self.url)
        soup = BeautifulSoup(markup=req.content, features="lxml")
        return [soup, req]

    def incrementPage(self) -> int:  # TODO: Write test
        self.page += 1
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&pageSize=250&page={}&q={}".format(
            self.page, self.query
        )
        return self.page

    def get_CurrentPage(self) -> int:
        return self.page
