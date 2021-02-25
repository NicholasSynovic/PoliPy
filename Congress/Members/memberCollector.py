from json import dumps

from progress.spinner import MoonSpinner

from libs import congressAPI, databaseConnector, scraper
from libs.cmdLineInterface import arguementHandling
from libs.cmdLineOutput import errorMessage, neutralMessage, positiveMessage


class MemberCollector:
    def __init__(self, **kwargs) -> None:
        self.chamber = kwargs["chamber"]
        self.kwargs = kwargs
        self.congressAPI = congressAPI.CongressAPI(dumps(kwargs))
        self.databaseConnector = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.scraper = None

    def buildDatabase(self) -> None:
        tableName = self.chamber + "_Members"
        print(neutralMessage(message="Attempting to create table {}".format(tableName)))
        frontmatterSQL = "CREATE TABLE {} (ID INTEGER, Chamber TEXT, Name TEXT, URL TEXT, State TEXT, District TEXT, Party TEXT, PRIMARY KEY(ID))".format(
            tableName
        )
        if self.databaseConnector.executeSQL(sql=frontmatterSQL):
            print(positiveMessage(message="Created table {}".format(tableName)))

    def createScraper(self) -> None:
        soup = self.congressAPI.sendRequest()[0]
        self.scraper = scraper.Scraper(soup=soup)

    def executeSQL(self, sql: str, options: tuple = None) -> None:
        self.databaseConnector.executeSQL(sql=sql, options=options)

    def startScraper(self):
        currentPage = self.congressAPI.get_CurrentPage()
        self.buildDatabase()
        self.createScraper()  # Initial Search/ Page 1

        if not self.scraper.check_SearchHasResults():
            print(
                errorMessage(message="Invalid Congress Session or Chamber of Congress")
            )
            quit()

        count = self.scraper.get_TotalNumberofItemsandPages()

        if count[1] > 100:
            print(errorMessage(message="Search to broad, narrow search to continue"))
            quit()

        while True:
            tableName = self.chamber + "_Members"
            pkCalculation = (currentPage - 1) * 250
            onPageData = self.scraper.get_DataPoints(startingPK=pkCalculation)

            frontmatterSQL = "INSERT OR IGNORE INTO {} (ID, Chamber, Name, URL, State, District, Party) VALUES (?,?,?,?,?,?,?)".format(
                tableName
            )

            with MoonSpinner(
                neutralMessage("Inserting data into {}\t".format(tableName))
            ) as spinner:
                for member in onPageData:
                    memberDataPoint = self.scraper.scrape_MemberDataPoints(
                        primaryKey=member[0],
                        member=member[2],
                        chamber=self.kwargs["chamber"],
                    )
                    self.executeSQL(sql=frontmatterSQL, options=memberDataPoint)
                    spinner.next()
            print(positiveMessage(message="Stored data into {}".format(tableName)))
            currentPage = self.congressAPI.incrementPage()
            if currentPage > count[1]:
                break

            self.congressAPI.incrementPage()
            self.createScraper()


if __name__ == "__main__":

    cmdLineArgs = arguementHandling()

    print(
        "\nPoliPy: {} Congress {} Chamber Member Scraper".format(
            str(cmdLineArgs.session[0]), cmdLineArgs.chamber[0]
        )
    )

    mc = MemberCollector(
        congress=cmdLineArgs.session[0],
        source="members",
        chamber=cmdLineArgs.chamber[0],
    )

    mc.startScraper()
