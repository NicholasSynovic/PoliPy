from bs4 import BeautifulSoup, Tag
import re
from tqdm import tqdm


class Scraper:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def check_SearchHasResults(self) -> bool:
        if self.soup.find(name="h2", attrs={"class": "no-results-error"}) is None:
            return True
        return False

    def get_TotalNumberofPages(self) -> tuple:
        def _get_Data(string: str) -> int:
            data = 0
            try:
                data = int(
                    re.findall("(?<=of )(\d+[,]\d+)", string)[0].replace(",", "")
                )
            except IndexError:
                data = int(re.findall("(?<=of )(\d+)", string)[0])
            return data

        response = self.soup.find_all(name="span", attrs={"class": "results-number"})
        items = _get_Data(string=response[0].text)
        pages = _get_Data(string=response[1].text)
        return (items, pages)

    def get_DataPoints(self) -> list:
        # (Primary Key, Type, Data)
        dataPoints = []
        response = self.soup.find_all(name="li", attrs={"class": "expanded"})
        index = 0
        for dataPoint in tqdm(response, desc="Finding Member Front Matter"):
            try:
                dataPoint = response[index]
                primaryKey = index + 1
                dataType = dataPoint.find(
                    name="span", attrs={"class": "visualIndicator"}
                ).text.capitalize()
                dataPoints.append((primaryKey, dataType, dataPoint))
                index += 1
            except IndexError:
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
