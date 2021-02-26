from json import dumps

from libs import congressAPI, databaseConnector, scraper
from libs.cmdLineInterface import arguementHandling
from libs.cmdLineOutput import errorMessage, neutralMessage, positiveMessage
from progress.spinner import MoonSpinner


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
        tableName = self.chamber + "_Legislation"
        print(neutralMessage(message="Attempting to create table {}".format(tableName)))
        frontmatterSQL = "CREATE TABLE {} (ID INTEGER, Type TEXT, Title TEXT, URL TEXT, Description TEXT, Sponsor TEXT, Sponsor_URL TEXT, Date_Introduced TEXT, Cosponsor_Amount INTEGER, Cosponsor_URL TEXT, Committees TEXT, Latest_Action_Chamber TEXT, Latest_Action_Date TEXT, Latest_Action_Description TEXT, Latest_Action_URL TEXT, Tracker TEXT, PRIMARY KEY(ID))".format(
            tableName
        )
        if self.databaseConnector.executeSQL(sql=frontmatterSQL):
            print(positiveMessage(message="Created table {}").format(tableName))

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
            print(errorMessage(message="Invalid Congress Session"))
            quit()

        count = self.scraper.get_TotalNumberofItemsandPages()

        if count[1] > 100:
            print(errorMessage(message="Search to broad, narrow search to continue"))
            quit()

        while True:
            tableName = self.chamber + "_Legislation"
            pkCalculation = (currentPage - 1) * 250
            onPageData = self.scraper.get_DataPoints(startingPK=pkCalculation)

            frontmatterSQL = "INSERT OR IGNORE INTO {} (ID, Type, Title, URL, Description, Sponsor, Sponsor_URL, Date_Introduced, Cosponsor_Amount, Cosponsor_URL, Committees, Latest_Action_Chamber, Latest_Action_Date, Latest_Action_Description, Latest_Action_URL, Tracker) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)".format(
                tableName
            )

            with MoonSpinner(
                neutralMessage("Inserting data into {}\t".format(tableName))
            ) as spinner:

                # TODO: FIX ME

                for legislation in onPageData:
                    legislationDataPoint = (
                        self.scraper.scrape_LegislationFrontMatterDataPoints(
                            primaryKey=legislation[0],
                            legislation=legislation[2],
                        )
                    )
                    self.executeSQL(sql=frontmatterSQL, options=legislationDataPoint)
                    spinner.next()
            print(positiveMessage(message="Stored data into {}".format(tableName)))
            currentPage = self.congressAPI.get_CurrentPage() + 1
            if currentPage > count[1]:
                break

            self.congressAPI.incrementPage()
            self.createScraper()


if __name__ == "__main__":

    cmdLineArgs = arguementHandling()

    print(
        "\nPoliPy: {} Congress Legislation Scraper".format(str(cmdLineArgs.session[0]))
    )

    mc = MemberCollector(
        congress=cmdLineArgs.session[0],
        source="legislation",
        chamber=cmdLineArgs.chamber[0],
    )

    mc.startScraper()
