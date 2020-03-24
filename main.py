import math
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from plotly.graph_objs import *
import plotly.graph_objects as go
import plotly.io as pio
import cufflinks as cf
import plotly.offline as py
import plotly.express as px


def getIndexPointOfOrder(total, index):
    percentage_string = str(index / total * 100)
    return percentage_string[0:4]


def getDFFromFile(filename):
    return pd.read_csv(filename, sep=";", index_col=0)


def getDifferenceFromYesterday(files):
    today_file = files[-1]
    todayDF = getDFFromFile(today_file)
    yesterday_file = files[-2]
    yesterdayDF = getDFFromFile(yesterday_file)
    return todayDF.subtract(yesterdayDF)


def printInfo(pretext, country_name, value, index, total):
    print(pretext + " " + country_name + ": " + str(value) + " - " + getIndexPointOfOrder(total, index) + "%")


def getTop10AndIndex(df, amount, index, county_name):
    df.sort_values(index, ascending=False, inplace=True)
    index_county = df.index.get_loc(county_name)
    value_county = df.at[county_name, index]
    largest = df.nlargest(amount, index)
    return largest, index_county, value_county


def getDifferenceFromYesterDay(files):
    today_file = files[-1]
    todayDF = getDFFromFile(today_file)
    yesterday_file = files[-2]
    yesterdayDF = getDFFromFile(yesterday_file)
    return todayDF - yesterdayDF


def getAllFilesInDirectory(dir_name):
    files = os.listdir(dir_name)
    results = map(lambda x: dir_name + x, files)
    return list(results)


def getChangeOverTime(county_name, files):
    df = pd.DataFrame()
    for file in files:
        dayDF = getDFFromFile(file)
        date_string = trimFileNameToDate(file)
        dayDF["day"] = date_string
        totalSum = dayDF["Aantal"].sum()
        county_row = dayDF.loc[county_name]
        county_row["sum"] = totalSum
        df = df.append(county_row)
    df.sort_values("day", ascending=True, inplace=True)
    df.reset_index()
    df.set_index("day")
    return df


def trimFileNameToDate(file_name):
    return file_name[6:11]


def normalizeOnKey(df, new_key, old_key):
    df[new_key] = df[old_key] / df[old_key].max()
    return df


def annotate(ax, length):
    for p in ax.patches:
        ax.annotate(str(round(p.get_height(), length)), xy=(p.get_x(), p.get_height()))


class CoronaGraph:
    def __init__(self):
        self.corona_scv_dir = "input/"
        self.files = getAllFilesInDirectory(self.corona_scv_dir)
        self.corona_scv_file = self.files[-1]
        self.StatsDf = getDFFromFile(self.corona_scv_file)
        self.DrawMatplot()

    def DrawMatplot(self):
        cf.go_offline()
        # chart_studio.tools.set_config_file(world_readable=False, sharing='private')

        sns.set_context('paper')
        pd.options.mode.chained_assignment = None
        TOTAL_INDEX = "Aantal"
        INDEXED_SUM = "indexed_sum"
        DENSITY_INDEX = "Aantal per 100.000 inwoners"
        ARNHEM = "Arnhem"
        DELFT = "Delft"
        COUNTY_NAME = DELFT
        count = len(self.StatsDf.index)
        top_10 = math.ceil(count / 10)

        # fig = plt.figure()

        # ax = fig.add_subplot(221)
        AantalDF, total_index_county, total_value_county = getTop10AndIndex(self.StatsDf, top_10, TOTAL_INDEX, COUNTY_NAME)
        ax = AantalDF.plot(title="Total", kind="bar", y=TOTAL_INDEX, color='red')
        annotate(ax, 0)

        # fig = go.Figure(go.Bar(AantalDF))
        # fig.update_layout(title_text='hello world')
        # pio.write_html(fig, file='hello_world.html', auto_open=True)

        # ax = fig.add_subplot(222)
        DensityDF, density_index_county, density_value_county = getTop10AndIndex(self.StatsDf, top_10, DENSITY_INDEX, COUNTY_NAME)
        ax = DensityDF.plot(title="Density", kind="bar", y=DENSITY_INDEX, color='green')
        annotate(ax, 0)

        DifferenceDf = getDifferenceFromYesterday(self.files)

        # ax = fig.add_subplot(223)
        DifferenceTotalDf, difference_total_index_county, differrence_total_county = getTop10AndIndex(DifferenceDf, top_10, TOTAL_INDEX, COUNTY_NAME)
        ax = DifferenceTotalDf.plot(title="Difference in total", kind="bar", y=TOTAL_INDEX, color='blue')
        annotate(ax, 0)
        # ax = fig.add_subplot(224)
        DifferenceDensityDf, difference_density_index_county, differrence_density_county = getTop10AndIndex(DifferenceDf, top_10, DENSITY_INDEX, COUNTY_NAME)
        ax = DifferenceDensityDf.plot(title="Difference in density", kind="bar", y=DENSITY_INDEX, color='yellow')
        px.bar(DifferenceDensityDf, title="Difference in density", x=DifferenceTotalDf.index, y=DENSITY_INDEX, height=400).show()
        annotate(ax, 0)

        print("Total gemeentes:" + str(count))
        printInfo("Total", COUNTY_NAME, total_value_county, total_index_county, count)
        printInfo("Density", COUNTY_NAME, density_value_county, density_index_county, count)
        printInfo("Difference Total", COUNTY_NAME, differrence_total_county, difference_total_index_county, count)
        printInfo("Difference Density", COUNTY_NAME, differrence_density_county, difference_density_index_county, count)

        TOTAL_CASES = self.StatsDf[TOTAL_INDEX].sum()
        print("Total Cases: " + str(TOTAL_CASES))
        # ax.axis('scaled')

        county_change_df = getChangeOverTime(COUNTY_NAME, self.files)
        county_change_index = DENSITY_INDEX
        ax = county_change_df.plot(title=COUNTY_NAME + " - " + county_change_index, kind="bar", x="day", y=county_change_index)
        annotate(ax, 0)

        county_change_df = normalizeOnKey(county_change_df, INDEXED_SUM, "sum")

        fig = px.bar(county_change_df, x="day", y=INDEXED_SUM, height=400)
        fig.update_traces(marker_color='red')
        fig.show()

        maxindex = DifferenceDf.loc[DifferenceDf[TOTAL_INDEX].idxmax()]
        print(maxindex)

        plt.tight_layout()  # plt.show()

        # TODO check maken op grootste verschil  # TODO get change of index


if __name__ == '__main__':
    run = CoronaGraph()
