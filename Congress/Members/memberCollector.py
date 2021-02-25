from json import dumps

from tqdm import tqdm

from libs.cmdLineOutput import positiveMessage, neutralMessage, errorMessage
from libs import congressAPI, databaseConnector, scraper
from libs.cmdLineInterface import arguementHandling


class MemberCollector:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.congressAPI = congressAPI.CongressAPI(dumps(kwargs))
        self.databaseConnector = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.scraper = None

    def buildDatabase(self, chamber: str = "House") -> None:
        frontmatterSQL = "CREATE TABLE {} (ID INTEGER, Chamber TEXT, Name TEXT, URL TEXT, State TEXT, District TEXT, Party TEXT, PRIMARY KEY(ID))".format(
            chamber + "_Members"
        )
        self.databaseConnector.executeSQL(sql=frontmatterSQL)

    def createScraper(self) -> None:
        soup = self.congressAPI.sendRequest()[0]
        self.scraper = scraper.Scraper(soup=soup)

    def executeSQL(self, sql: str, options: tuple = None) -> None:
        self.databaseConnector.executeSQL(sql=sql, options=options)

    def startScraper(self):
        print(
            "\nPoliPy: {} Congress {} Chamber Member Scraper".format(
                str(self.kwargs["congress"]), self.kwargs["chamber"]
            )
        )

        currentPage = self.congressAPI.get_CurrentPage()
        self.buildDatabase()
        self.createScraper()  # Initial Search/ Page 1

        if not self.scraper.check_SearchHasResults():
            print("Invalid Congress Session or Chamber of Congress.")
            quit()

        count = self.scraper.get_TotalNumberofPages()
        if count[1] > 100:
            print("Search to broad, narrow search to continue.")
            quit()

        while True:
            pkCalculation = (currentPage - 1) * 250
            onPageData = self.scraper.get_DataPoints(startingPK=pkCalculation)

            frontmatterSQL = "INSERT INTO FrontMatter (ID, Chamber, Name, URL, State, District, Party) VALUES (?,?,?,?,?,?,?)"

            for member in tqdm(
                onPageData,
                desc="Storing Member Front Matter (Page {})".format(currentPage),
            ):
                memberDataPoint = self.scraper.scrape_MemberDataPoints(
                    primaryKey=member[0],
                    member=member[2],
                    chamber=self.kwargs["chamber"],
                )
                self.executeSQL(sql=frontmatterSQL, options=memberDataPoint)

            currentPage = self.congressAPI.incrementPage()
            if currentPage > count[1]:
                break

            self.congressAPI.incrementPage()
            self.createScraper()


if __name__ == "__main__":

    cmdLineArgs = arguementHandling()

    mc = MemberCollector(
        congress=cmdLineArgs.session[0],
        source="members",
        chamber=cmdLineArgs.chamber[0],
    )

    mc.startScraper()
