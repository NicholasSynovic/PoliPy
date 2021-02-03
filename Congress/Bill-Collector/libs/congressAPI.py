from json import dumps

import requests
from bs4 import BeautifulSoup


class CongressAPI:
    def __init__(self, **kwargs) -> None:  # TODO: Fix test
        self.page = 1
        self.query = kwargs
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&page={}&q={}".format(
            self.page, dumps(self.query)
        )

    def sendRequest(self) -> list:
        req = requests.get(self.url)
        soup = BeautifulSoup(markup=req.content, features="lxml")
        return [soup, req]

    def incrementPage(self) -> None:  # TODO: Write test
        self.page += 1
        self.url = "https://www.congress.gov/search?searchResultViewType=expanded&page={}&q={}".format(
            self.page, dumps(self.query)
        )
