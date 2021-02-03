from os import write
from libs import congressAPI, databaseConnector, scraper
from json import dumps
import csv


class BillCollector:
    def __init__(self, **kwargs) -> None:
        self.c = congressAPI.CongressAPI(dumps(kwargs))
        self.d = databaseConnector.DatabaseConnector(
            databaseFileName=str(kwargs["congress"]) + ".db"
        )
        self.s = None

    def buildDatabase(self) -> None:
        sql = "CREATE TABLE FrontMatter (ID INTEGER, DocumentType TEXT, ShortTitle TEXT, DocumentLink TEXT, LongTitle TEXT, SponsorName TEXT, SponsorLink TEXT, IntroducedDate INTEGER, PublicLegislation TEXT, PrivateLegislation TEXT, CosponsorAmount INTEGER, CosponsorLink TEXT, CommitteesChamber TEXT, LatestActionChamber INTEGER, LatestActionDate INTEGER, LatestActionLink TEXT, TrackerStage TEXT, PRIMARY KEY(ID))"
        self.d.executeSQL(sql=sql)

    def createScraper(self) -> None:
        soup = self.c.sendRequest()[0]
        self.s = scraper.Scraper(soup=soup)


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

with open("temp.csv", "w") as the_file:
    csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
    writer = csv.writer(the_file, dialect="custom")
    for memberIndex in range(len(onPageData)):
        print(memberIndex + 1)
        data = bc.s.scrape_MemberDataPoints(member=onPageData[memberIndex][2])
        writer.writerow(data)