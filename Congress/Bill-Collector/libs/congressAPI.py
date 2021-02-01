from json import dumps

import requests
from bs4 import BeautifulSoup


class CongressAPI:
    def __init__(self, **kwargs) -> None:
        self.query = kwargs
        self.url = (
            "https://www.congress.gov/search?searchResultViewType=expanded&q={}".format(
                dumps(self.query)
            )
        )

    def sendRequest(self) -> list:
        req = requests.get(self.url)
        soup = BeautifulSoup(markup=req.content, features="lxml")
        return [soup, req]
