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

    def scrape_MemberDataPoints(
        self, primaryKey: int, member: Tag, chamber: str = "House"
    ) -> tuple:
        # (ID, Chamber, Name, URL, State, District, Party)
        def _get_Name(string: str) -> str:
            name = ""
            positions = [
                "Senator",
                "Representative",
                "Resident Commissioner",
                "Delegate de",
                "Delegate",
            ]
            positionsIndex = 0
            while True:
                try:
                    name = re.findall(
                        "(?<={} )(\D+)".format(positions[positionsIndex]), string
                    )[0]
                    return name
                except IndexError:
                    positionsIndex += 1

        header = member.find(name="span", attrs={"class": "result-heading"})
        items = member.find(name="div", attrs={"class": "member-profile"}).find_all(
            name="span", attrs={"class": "result-item"}
        )

        nameData = _get_Name(string=header.text)
        urlData = "https://www.congress.gov" + header.find(name="a").get("href")

        stateData = items[0].find(name="span").text

        if len(items) > 3:
            districtData = items[1].find(name="span").text
        else:
            districtData = "N/A"

        partyData = items[-2].find(name="span").text

        return (
            primaryKey,
            chamber,
            nameData,
            urlData,
            stateData,
            districtData,
            partyData,
        )
