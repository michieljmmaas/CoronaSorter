import math
import os
import pandas as pd
import matplotlib.pyplot as plt
import cufflinks as cf
import plotly.express as px
from plotly.subplots import make_subplots
import datetime


def getIndexPointOfOrder(total, index):
    percentage_string = str(index / total * 100)
    return percentage_string[0:4]


def getDFFromFile(filename):
    return pd.read_csv(filename, sep=";", index_col=0)


def getDifferenceFromNumerOfDaysBack(files, number_of_days_back):
    previous_index = 0
    if number_of_days_back != -1:
        previous_index = -(1 + number_of_days_back)
    today_file = files[-1]
    todayDF = getDFFromFile(today_file)
    previous_file = files[previous_index]
    yesterdayDF = getDFFromFile(previous_file)
    return todayDF.subtract(yesterdayDF), trimFileNameToDate(previous_file)


def printInfo(pretext, country_name, value, index, total):
    print(pretext + " " + country_name + ": " + str(value) + " - " + getIndexPointOfOrder(total, index) + "%")


def getTop10AndIndex(df, amount, index, county_name):
    df.sort_values(index, ascending=False, inplace=True)
    index_county = df.index.get_loc(county_name)
    value_county = df.at[county_name, index]
    largest = df.nlargest(amount, index)
    return largest, index_county, value_county


def getAllFilesInDirectory(dir_name):
    files = os.listdir(dir_name)
    results = map(lambda x: dir_name + x, files)
    return list(results)


def getChangeOverTime(county_name, files):
    df = pd.DataFrame()
    for file in files:
        dayDF = getDFFromFile(file)
        dayDF["day"] = trimFileNameToDate(file)
        totalSum = dayDF["Aantal"].sum()
        county_row = dayDF.loc[county_name]
        county_row["sum"] = totalSum
        df = df.append(county_row)
    df.sort_values("day", ascending=True, inplace=True)
    df.reset_index()
    df.set_index("day")
    return df


def trimFileNameToDate(file_name):
    date_string = file_name[6:11]
    month = int(date_string[0:2])
    day = int(date_string[3:5])
    return datetime.datetime(2020, month, day)


def normalizeOnKey(df, new_key, old_key):
    df[new_key] = df[old_key] / df[old_key].max()
    return df


def annotate(ax, length):
    for p in ax.patches:
        ax.annotate(str(round(p.get_height(), length)), xy=(p.get_x(), p.get_height()))


def getStringOfDate(date):
    datestring = date.strftime("%m/%d")
    difference = datetime.datetime.now() - date
    return datestring + " - " + str(difference.days + 1) + " days"


class CoronaGraph:
    def __init__(self):
        self.corona_scv_dir = "input/"
        self.files = getAllFilesInDirectory(self.corona_scv_dir)
        self.corona_scv_file = self.files[-1]
        self.StatsDf = getDFFromFile(self.corona_scv_file)
        self.DrawMatplot()

    def DrawMatplot(self):
        cf.go_offline()

        pd.options.mode.chained_assignment = None
        TOTAL_INDEX = "Aantal"
        INDEXED_SUM = "indexed_sum"
        DENSITY_INDEX = "Aantal per 100.000 inwoners"
        ARNHEM = "Arnhem"
        DELFT = "Delft"
        COUNTY_NAME = DELFT
        count = len(self.StatsDf.index)
        top_10 = math.ceil(count / 2)
        # top_10 = count
        DIFFEREMCE_SINCE = 1
        NORMALIZED = False
        CHANGE_INDEX = "sum"

        AantalDF, total_index_county, total_value_county = getTop10AndIndex(self.StatsDf, top_10, TOTAL_INDEX, COUNTY_NAME)
        total_fig = px.bar(AantalDF, x=AantalDF.index, y=TOTAL_INDEX)
        total_fig = total_fig.update_traces(marker_color='red')
        total_trace = total_fig['data'][0]

        DensityDF, density_index_county, density_value_county = getTop10AndIndex(self.StatsDf, top_10, DENSITY_INDEX, COUNTY_NAME)
        denisty_fig = px.bar(DensityDF, x=DensityDF.index, y=DENSITY_INDEX)
        denisty_fig = denisty_fig.update_traces(marker_color='blue')
        denisty_trace = denisty_fig['data'][0]

        DifferenceDf, earliest_date = getDifferenceFromNumerOfDaysBack(self.files, DIFFEREMCE_SINCE)

        DifferenceTotalDf, difference_total_index_county, differrence_total_county = getTop10AndIndex(DifferenceDf, top_10, TOTAL_INDEX, COUNTY_NAME)
        total_change_fig = px.bar(DifferenceTotalDf, x=DifferenceTotalDf.index, y=TOTAL_INDEX)
        total_change_fig = total_change_fig.update_traces(marker_color='green')
        total_change_trace = total_change_fig['data'][0]

        DifferenceDensityDf, difference_density_index_county, differrence_density_county = getTop10AndIndex(DifferenceDf, top_10, DENSITY_INDEX, COUNTY_NAME)
        density_change_fig = px.bar(DifferenceDensityDf, x=DifferenceDensityDf.index, y=DENSITY_INDEX)
        density_change_fig = density_change_fig.update_traces(marker_color='yellow')
        density_change_trace = density_change_fig['data'][0]

        printInfo("Total", COUNTY_NAME, total_value_county, total_index_county, count)
        printInfo("Density", COUNTY_NAME, density_value_county, density_index_county, count)
        printInfo("Difference Total", COUNTY_NAME, differrence_total_county, difference_total_index_county, count)
        printInfo("Difference Density", COUNTY_NAME, differrence_density_county, difference_density_index_county, count)

        TOTAL_CASES = self.StatsDf[TOTAL_INDEX].sum()
        print("Total Cases: " + str(TOTAL_CASES))

        county_change_df = getChangeOverTime(COUNTY_NAME, self.files)
        county_change_index = TOTAL_INDEX
        county_change_fig = px.bar(county_change_df, x="day", y=county_change_index)
        county_change_fig = county_change_fig.update_traces(marker_color='purple')
        county_change_trace = county_change_fig['data'][0]

        total_change_indexed_df = county_change_df
        if NORMALIZED:
            CHANGE_INDEX = INDEXED_SUM
            total_change_indexed_df = normalizeOnKey(county_change_df, INDEXED_SUM, "sum")

        total_change_indexed_fig = px.bar(total_change_indexed_df, x="day", y=CHANGE_INDEX)
        total_change_indexed_fig = total_change_indexed_fig.update_traces(marker_color='orange')
        total_change_indexed_trace = total_change_indexed_fig['data'][0]

        date_string = getStringOfDate(earliest_date)

        fig = make_subplots(rows=3, cols=2,
                            subplot_titles=("Total", "Density", "Total Change since: " + date_string, "Density Change since: " + date_string, "Total Cases in " + COUNTY_NAME, "Total Cases Indexed"))
        fig.add_trace(total_trace, row=1, col=1)
        fig.add_trace(denisty_trace, row=1, col=2)
        fig.add_trace(total_change_trace, row=2, col=1)
        fig.add_trace(density_change_trace, row=2, col=2)
        fig.add_trace(county_change_trace, row=3, col=1)
        fig.add_trace(total_change_indexed_trace, row=3, col=2)

        fig.update_layout(title_text="Total Cases: " + str(TOTAL_CASES))
        fig.show()
        plt.tight_layout()

        # TODO check maken op grootste verschil  # TODO get change of index


if __name__ == '__main__':
    run = CoronaGraph()
