import re
from math import ceil

from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet


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

    # TODO: Simplify method
    def scrape_TreatyDocumentFrontMatterDataPoints(
        self, primaryKey: int, treaty: Tag
    ) -> tuple:
        # (ID, Title, URL, Short_Title, Text_URL, PDF_URL, Date_Recieved, Topic, Latest_Action_Date, Latest_Action_Text, Latest_Action_URL)

        # TODO: Simplify method
        def _getItems(items: ResultSet) -> list:
            itemsLength = len(items)

            if itemsLength == 4:
                # Base case
                docLinks: Tag = items[0]
                textURLData: Tag = "https://www.congress.gov" + docLinks.find(
                    name="a", text="TXT"
                ).get("href")
                try:
                    pdfURLData: Tag = "https://www.congress.gov" + docLinks.find(
                        name="a", text="PDF"
                    ).get("href")
                except AttributeError:
                    pdfURLData = None

                dateRecievedData = items[1].text.split(":")[1].strip()
                topicData = items[2].text.split(":")[1].strip()

                latestAction = items[3].text.split(":")

                latestActionDateData = latestAction[1].split(" - ")[0].strip()
                latestActionTextData = latestAction[1].split(" - ")[1].strip()
                latestActionURLData = "https://www.congress.gov" + items[3].find(
                    name="a"
                ).get("href")

            elif itemsLength == 3:
                # If there is a treaty text
                topText: Tag = items[0]

                if topText.text.split(":")[0].strip() == "Text of Treaty Document":
                    dateRecievedData = items[1].text.split(":")[1].strip()
                    textLinks = topText.find_all(name="a")

                    textURLData = "https://www.congress.gov" + textLinks[0].get("href")
                    try:
                        pdfURLData = "https://www.congress.gov" + textLinks[1].get(
                            "href"
                        )
                    except IndexError:
                        pdfURLData = None

                    potentialTopic = items[2].text.split(":")
                    if potentialTopic[0].strip() == "Treaty Topic":
                        topicData = potentialTopic[1].strip()
                    else:
                        topicData = None

                else:
                    # If there is not a treaty text
                    dateRecievedData = topText.text.split(":")[1].strip()

                    textURLData = None
                    pdfURLData = None

                    potentialTopic = items[1].text.split(":")
                    if potentialTopic[0].strip() == "Treaty Topic":
                        topicData = potentialTopic[1].strip()
                    else:
                        topicData = None

                potentialActions = items[-1].text.split(":")
                if potentialActions[0] == "Latest Senate Action":
                    # If there are Latest Actions
                    latestActionDateData = potentialActions[1].split(" - ")[0].strip()
                    latestActionTextData = potentialActions[1].split(" - ")[1].strip()
                    latestActionURLData = "https://www.congress.gov" + items[-1].find(
                        name="a"
                    ).get("href")
                else:
                    latestActionDateData = None
                    latestActionTextData = None
                    latestActionURLData = None

            else:
                # items length == 2
                # No topic
                # Only date and actions
                textURLData = None
                pdfURLData = None
                dateRecievedData = items[0].text.split(":")[1].strip()
                topicData = None

                potentialActions = items[-1].text.split(":")

                latestActionDateData = potentialActions[1].split(" - ")[0].strip()
                latestActionTextData = potentialActions[1].split(" - ")[1].strip()
                latestActionURLData = "https://www.congress.gov" + items[-1].find(
                    name="a"
                ).get("href")

            if int(dateRecievedData.split("/")[-1]) < 1995:
                # If the date is before 1995, there is no treaty text
                textURLData = None
                pdfURLData = None

            return [
                textURLData,
                pdfURLData,
                dateRecievedData,
                topicData,
                latestActionDateData,
                latestActionTextData,
                latestActionURLData,
            ]

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

        data = _getItems(items=items)

        return (
            primaryKey,
            titleData,
            urlData,
            shortTitleData,
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
        )
