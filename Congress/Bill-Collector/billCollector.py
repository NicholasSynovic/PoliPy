from libs import congressAPI, databaseConnector, scraper


class BillCollector:
    def __init__(self, **kwargs) -> None:
        self.c = congressAPI.CongressAPI(kwargs)
        self.d = databaseConnector.DatabaseConnector(
            databaseFileName=kwargs["congress"]
        )
        self.s = None

    def createScraper(self) -> None:
        soup = self.c.sendRequest()[0]
        self.s = scraper.Scraper(soup=soup)
