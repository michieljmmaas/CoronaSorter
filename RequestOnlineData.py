import requests
import pandas as pd
from io import StringIO
import json

from bs4 import BeautifulSoup


def GetDataFromOnline(files):
    SiteContents = RequestSiteData()
    date_on_page_as_file_string = GetDateFromPage(SiteContents)
    do_not_have_data = checkIfHaveDate(date_on_page_as_file_string, files)
    if do_not_have_data:
        csv_data = ParseRequestToCsvData(SiteContents)
        dataframe = ReadInDataframe(csv_data)
        dataframe.to_csv(date_on_page_as_file_string, index=False)


def checkIfHaveDate(date_on_page, files):
    return not date_on_page in files


def ReadInDataframe(csv_string):
    StringData = StringIO(csv_string)
    dataframe = pd.read_csv(StringData, sep=";")
    dataframe = dataframe.drop(["Gemnr", "BevAant"], axis=1)
    dataframe = dataframe.drop([0])
    dataframe = dataframe.sort_values(by=['Gemeente'])
    dataframe = dataframe.reset_index(drop=True)
    dataframe = dataframe.rename(columns={'Gemeente': 'Category'})
    dataframe = dataframe[['Category', 'Aantal per 100.000 inwoners', 'Aantal']]
    return dataframe


def GetDateFromPage(page_content):
    soup = BeautifulSoup(page_content, features="html.parser")
    div = soup.find('div', id='mapTitles')
    to_string = str(div)
    json_string = RemoveTagsFromHtml(to_string, "mapTitles")
    json_object = json.loads(json_string)
    full_date_string = json_object["nl"]["mapSubtitle"]
    return reformatDateString(full_date_string)


def reformatDateString(full_date_string):
    split_array = full_date_string.split(" ")
    date_string = split_array[-1]
    split_array = date_string.split("-")
    day = addZeroIfSingle(split_array[0])
    month = addZeroIfSingle(split_array[1])
    return "input/" + month + "-" + day + ".csv"


def addZeroIfSingle(string):
    if len(string) == 1:
        string = "0" + string
    return string


def RequestSiteData():
    URL = "https://www.rivm.nl/coronavirus-kaart-van-nederland-per-gemeente"
    r = requests.get(url=URL)
    return r.text


def RemoveTagsFromHtml(div_text, id):
    removed_upper_text = div_text.replace('<div id="' + id + '">', '')
    removed_lower_text = removed_upper_text.replace('</div>', '')
    return removed_lower_text.strip()


def CheckDate(html_text):
    return "date"


def ParseRequestToCsvData(html_text):
    soup = BeautifulSoup(html_text, features="html.parser")
    div = soup.find('div', id='csvData')
    to_string = str(div)
    to_string = to_string.replace('s-Gravenhage', '\'s-Gravenhage')
    return RemoveTagsFromHtml(to_string, "csvData")
