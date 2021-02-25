from json import dumps

from libs import congressAPI, databaseConnector, scraper
from tqdm import tqdm


class MemberCollector:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.congressAPI = congressAPI.CongressAPI(dumps(kwargs))
        self.databaseConnector = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.scraper = None

    def buildDatabase(self) -> None:
        frontmatterSQL = "CREATE TABLE FrontMatter (ID INTEGER, Chamber TEXT, Name TEXT, URL TEXT, State TEXT, District TEXT, Party TEXT, PRIMARY KEY(ID))"
        self.databaseConnector.executeSQL(sql=frontmatterSQL)

    def createScraper(self) -> None:
        soup = self.congressAPI.sendRequest()[0]
        self.scraper = scraper.Scraper(soup=soup)

    def executeSQL(self, sql: str, options: tuple = None) -> None:
        self.databaseConnector.executeSQL(sql=sql, options=options)


mc = MemberCollector(congress=93, source="members", chamber="House")
currentPage = mc.congressAPI.get_CurrentPage()
mc.buildDatabase()
mc.createScraper()  # Initial Search/ Page 1

if not mc.scraper.check_SearchHasResults():
    print("Invalid URL or search query.")
    quit()

count = mc.scraper.get_TotalNumberofPages()
if count[1] > 100:
    print("Search to broad, narrow search to continue.")
    quit()

while True:
    pkCalculation = (currentPage - 1) * 250
    onPageData = mc.scraper.get_DataPoints(startingPK=pkCalculation)

    frontmatterSQL = "INSERT INTO FrontMatter (ID, Chamber, Name, URL, State, District, Party) VALUES (?,?,?,?,?,?,?)"

    for member in tqdm(
        onPageData, desc="Storing Member Front Matter (Page {})".format(currentPage)
    ):
        memberDataPoint = mc.scraper.scrape_MemberDataPoints(
            primaryKey=member[0],
            member=member[2],
            chamber=mc.kwargs["chamber"],
        )
        mc.executeSQL(sql=frontmatterSQL, options=memberDataPoint)

    currentPage = mc.congressAPI.incrementPage()
    if currentPage > count[1]:
        break

    mc.congressAPI.incrementPage()
    mc.createScraper()
