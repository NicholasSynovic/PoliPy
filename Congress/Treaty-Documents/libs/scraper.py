import re
from math import ceil

from bs4 import BeautifulSoup, Tag


class Scraper:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def check_SearchHasResults(self) -> bool:
        if self.soup.find(name="h2", attrs={"class": "no-results-error"}) is None:
            return True
        return False

    def get_TotalNumberofItemsandPages(self) -> tuple:
        response = self.soup.find_all(name="span", attrs={"class": "results-number"})
        items = 0
        try:
            items = int(
                re.findall("(?<=of )(\d+[,]\d+)", response[0].text)[0].replace(",", "")
            )
        except IndexError:
            items = int(re.findall("(?<=of )(\d+)", response[0].text)[0])
        return (items, ceil(items / 250))

    def get_DataPoints(self, startingPK: int = 0) -> list:
        # (Primary Key, Type, Data)
        dataPoints = []
        response = self.soup.find_all(name="li", attrs={"class": "expanded"})
        pointer = 0
        for dataPoint in response:
            try:
                dataPoint = response[pointer]
                primaryKey = startingPK + pointer + 1
                dataType = dataPoint.find(
                    name="span", attrs={"class": "visualIndicator"}
                ).text.capitalize()
                dataPoints.append((primaryKey, dataType, dataPoint))
                pointer += 1
            except IndexError as e:
                break
        return dataPoints

    def scrape_TreatyDocumentFrontMatterDataPoints(
        self, primaryKey: int, treaty: Tag
    ) -> tuple:
        # (ID, Title, URL, Short_Title, Text_URL, Date_Recieved, Topic, Latest_Action_Date, Latest_Action_Text, Latest_Action_URL)

        items = treaty.find_all(name="span", attrs={"class": "result-item"})

        titleData = treaty.find(
            name="span", attrs={"class": "result-heading"}
        ).text.strip()

        urlData = "https://www.congress.gov" + (
            treaty.find(name="span", attrs={"class": "result-heading"})
            .find(name="a")
            .get("href")
        )

        shortTitleData = treaty.find(
            name="span", attrs={"class": "result-title"}
        ).text.strip()

        if len(items) == 4:
            textURLData = "https://www.congress.gov" + items[0].find(name="a").get(
                "href"
            )
            dateRecievedData = items[1].text.split(":")[1].strip()
            topicData = items[2].text.split(":")[1].strip()
            latestAction = items[3].text.split(":")
            latestActionDateData = latestAction[1].split(" - ")[0].strip()
            latestActionTextData = latestAction[1].split(" - ")[1].strip()
            latestActionURLData = "https://www.congress.gov" + items[3].find(
                name="a"
            ).get("href")
        else:
            textURLData = "N/A"
            dateRecievedData = items[0].text.split(":")[1].strip()
            topicData = items[1].text.split(":")[1].strip().split(" - ")[0]
            latestAction = items[2].text.split(":")
            latestActionDateData = latestAction[1].split(" - ")[0].strip()
            latestActionTextData = latestAction[1].split(" - ")[1].strip()
            latestActionURLData = "https://www.congress.gov" + items[2].find(
                name="a"
            ).get("href")

        return (
            primaryKey,
            titleData,
            urlData,
            shortTitleData,
            textURLData,
            dateRecievedData,
            topicData,
            latestActionDateData,
            latestActionTextData,
            latestActionURLData,
        )
