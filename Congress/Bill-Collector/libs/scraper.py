from bs4 import BeautifulSoup
import re


class Scraper:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def check_SearchHasResults(self) -> bool:
        if self.soup.find(name="h2", attrs={"class": "no-results-error"}) is None:
            return True
        return False

    def get_TotalNumberofPages(self) -> tuple:
        def _getData(string: str) -> int:
            data = 0
            try:
                data = int(
                    re.findall("(?<=of )(\d+[,]\d+)", string)[0].replace(",", "")
                )
            except IndexError:
                data = int(re.findall("(?<=of )(\d+)", string)[0])
            return data

        response = self.soup.find_all(name="span", attrs={"class": "results-number"})
        items = _getData(string=response[0].text)
        pages = _getData(string=response[1].text)
        return (items, pages)
