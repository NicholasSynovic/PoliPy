from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def get_TotalNumberofPages(self) -> int:
        pass
