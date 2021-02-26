from json import dumps

from libs import congressAPI, databaseConnector, scraper
from libs.cmdLineInterface import arguementHandling
from libs.cmdLineOutput import errorMessage, neutralMessage, positiveMessage
from progress.spinner import MoonSpinner


class MemberCollector:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.congressAPI = congressAPI.CongressAPI(dumps(kwargs))
        self.databaseConnector = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.scraper = None

    def buildDatabase(self) -> None:
        print(neutralMessage(message="Attempting to create table Treaty_Documents"))
        frontmatterSQL = "CREATE TABLE Treaty_Documents (ID INTEGER, Title TEXT, URL TEXT, Short_Title TEXT, Text_URL TEXT, PDF_URL TEXT, Date_Recieved TEXT, Topic TEXT, Latest_Action_Date TEXT, Latest_Action_Text TEXT, Latest_Action_URL TEXT, PRIMARY KEY(ID))"
        if self.databaseConnector.executeSQL(sql=frontmatterSQL):
            print(positiveMessage(message="Created table Treaty_Documents"))

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
            pkCalculation = (currentPage - 1) * 250
            onPageData = self.scraper.get_DataPoints(startingPK=pkCalculation)

            frontmatterSQL = "INSERT OR IGNORE INTO Treaty_Documents (ID, Title, URL, Short_Title, Text_URL, PDF_URL, Date_Recieved, Topic, Latest_Action_Date, Latest_Action_Text, Latest_Action_URL) VALUES (?,?,?,?,?,?,?,?,?,?,?)"

            with MoonSpinner(
                neutralMessage("Inserting data into Treaty_Documents\t")
            ) as spinner:

                # TODO: FIX ME

                for treaty in onPageData:
                    treatyDataPoint = (
                        self.scraper.scrape_TreatyDocumentFrontMatterDataPoints(
                            primaryKey=treaty[0],
                            treaty=treaty[2],
                        )
                    )
                    self.executeSQL(sql=frontmatterSQL, options=treatyDataPoint)
                    spinner.next()
            print(positiveMessage(message="Stored data into Treaty_Documents"))
            currentPage = self.congressAPI.get_CurrentPage() + 1
            if currentPage > count[1]:
                break

            self.congressAPI.incrementPage()
            self.createScraper()


if __name__ == "__main__":

    cmdLineArgs = arguementHandling()

    print(
        "\nPoliPy: {} Congress Treaty Documents Scraper".format(
            str(cmdLineArgs.session[0])
        )
    )

    mc = MemberCollector(
        congress=cmdLineArgs.session[0],
        source="treaties",
    )

    mc.startScraper()
