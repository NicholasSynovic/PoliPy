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
        # Latest_Action_Chamber, Latest_Action_Date, Latest_Action_Description, Latest_Action_URL, Tracker

        # TODO: Simplify method
        def _getItems(items: ResultSet) -> list:
            sponsorContent = items[0]

            sponsorData = sponsorContent.text.split(":")[1].split("(")[0].strip()

            sponsorLinks = sponsorContent.find_all(name="a")

            try:
                sponsorURLData = "https://www.congress.gov" + sponsorLinks[0].get(
                    "href"
                )
            except Exception:
                sponsorURLData = None

            try:
                cosponsorData = sponsorLinks[1].text.strip()
                cosponsorURLData = "https://www.congress.gov" + sponsorLinks[1].get(
                    "href"
                )
            except Exception:
                cosponsorData = None
                cosponsorURLData = None

            try:
                dateIntroducedData = re.findall(
                    "\(([^)]+)\)", sponsorContent.text.strip()
                )[0].split(" ")[-1]
            except Exception:
                dateIntroducedData = None

            committeesData = items[1].text.strip().split(" - ")[-1]

            latestAction = items[2]

            latestActionText = latestAction.text.strip()
            latestActionChamberData = (
                latestActionText.split(":")[1].split(" - ")[0].strip()
            )
            try:
                latestActionChamberDateData = (
                    latestActionText.split(" - ")[1].split(" ")[0].strip()
                )
            except Exception:
                latestActionChamberDateData = latestActionText.split(" ")[0].strip()

            latestActionChamberDescriptionData = (
                latestActionText.split(latestActionChamberDateData)[-1]
                .strip()
                .split("(")[0]
                .strip()
            )
            try:
                latestActionURLData = "https://www.congress.gov" + latestAction.find(
                    name="a"
                ).get("href")
            except AttributeError:
                latestActionURLData = None

            try:
                trackerData = (
                    items[3]
                    .find(name="p", attrs={"class": "hide_fromsighted"})
                    .text.strip()
                )
            except Exception:
                trackerData = None

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

        titleData = legislation.find(
            name="span", attrs={"class": "result-heading"}
        ).text.strip()

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

        data = _getItems(items=items)

        return (
            primaryKey,
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
