import re
from math import ceil, cos

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
    def scrape_LegislationFrontMatterDataPoints(
        self, primaryKey: int, legislation: Tag
    ) -> tuple:
        # TODO: Simplify method
        def _getItems(items: ResultSet, content: str) -> list:
            sponsorData = None
            sponsorURLData = None
            dateIntroducedData = None
            cosponsorData = None
            cosponsorURLData = None
            committeesData = None
            latestActionChamberData = None
            latestActionChamberDateData = None
            latestActionChamberDescriptionData = None
            latestActionURLData = None
            trackerData = None

            sponsorContent = items[0]

            sponsorData = (
                sponsorContent.text.split(":")[1]
                .split("(")[0]
                .strip()
                .split(" [")[0]
                .strip()
            )

            sponsorLinks = sponsorContent.find_all(name="a")

            if content == "Bill" or content == "Law":
                sponsorURLData = "https://www.congress.gov" + sponsorLinks[0].get(
                    "href"
                )
                cosponsorData = sponsorLinks[1].text.strip()
                cosponsorURLData = "https://www.congress.gov" + sponsorLinks[1].get(
                    "href"
                )
                dateIntroducedData = re.findall(
                    "\(([^)]+)\)", sponsorContent.text.strip()
                )[0].split(" ")[-1]
                committeesData = items[1].text.strip().split(" - ")[-1]

                latestActionText = items[2].text.strip()
                latestActionChamberData = (
                    latestActionText.split(":")[1].split(" - ")[0].strip()
                )
                latestActionChamberDateData = (
                    latestActionText.split(" - ")[1].split(" ")[0].strip()
                )
                latestActionChamberDescriptionData = (
                    latestActionText.split(latestActionChamberDateData)[-1]
                    .strip()
                    .split("(")[0]
                    .strip()
                )
                latestActionURLData = "https://www.congress.gov" + items[2].find(
                    name="a"
                ).get("href")

                trackerData = (
                    items[3]
                    .find(name="p", attrs={"class": "hide_fromsighted"})
                    .text.strip()
                )

            return [
                sponsorData,
                sponsorURLData,
                dateIntroducedData,
                cosponsorData,
                cosponsorURLData,
                committeesData,
                latestActionChamberData,
                latestActionChamberDateData,
                latestActionChamberDescriptionData,
                latestActionURLData,
                trackerData,
            ]

        items = legislation.find_all(name="span", attrs={"class": "result-item"})

        typeData = (
            legislation.find(name="span", attrs={"class": "visualIndicator"})
            .text.strip()
            .title()
        )

        titleData = (
            legislation.find(name="span", attrs={"class": "result-heading"})
            .text.strip()
            .split(" — ")[0]
        )

        urlData = "https://www.congress.gov" + (
            legislation.find(name="span", attrs={"class": "result-heading"})
            .find(name="a")
            .get("href")
        )

        try:
            descriptionData = legislation.find(
                name="span", attrs={"class": "result-title"}
            ).text.strip()
        except Exception:
            descriptionData = None

        data = _getItems(items=items, content=typeData)

        return (
            primaryKey,
            typeData,
            titleData,
            urlData,
            descriptionData,
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
            data[7],
            data[8],
            data[9],
            data[10],
        )
