from os import write
from libs import congressAPI, databaseConnector, scraper
from json import dumps
from tqdm import tqdm


class BillCollector:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.c = congressAPI.CongressAPI(dumps(kwargs))
        self.d = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.s = None

    def buildDatabase(self) -> None:
        sql = "CREATE TABLE FrontMatter (ID INTEGER, Chamber TEXT, Name TEXT, URL TEXT, State TEXT, District TEXT, Party TEXT, PRIMARY KEY(ID))"
        self.d.executeSQL(sql=sql)

    def createScraper(self) -> None:
        soup = self.c.sendRequest()[0]
        self.s = scraper.Scraper(soup=soup)

    def executeSQL(self, sql: str, options: tuple = None) -> None:
        self.d.executeSQL(sql=sql, options=options)


bc = BillCollector(congress=93, source="members", chamber="House")
bc.buildDatabase()
bc.createScraper()

if not bc.s.check_SearchHasResults():
    print("Invalid URL or search query.")
    quit()

c = bc.s.get_TotalNumberofPages()
if c[1] > 100:
    print("Search to broad, narrow search to continue.")
    quit()

onPageData = bc.s.get_DataPoints()

frontmatterSQL = "INSERT INTO FrontMatter (ID, Chamber, Name, URL, State, District, Party) VALUES (?,?,?,?,?,?,?)"
for member in tqdm(
    onPageData,
    desc="Storing Member Front Matter",
):
    memberDataPoint = bc.s.scrape_MemberDataPoints(
        primaryKey=member[0], member=member[2], chamber=bc.kwargs["chamber"]
    )
    bc.executeSQL(sql=frontmatterSQL, options=memberDataPoint)
