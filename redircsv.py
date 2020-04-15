import pandas as pd


def rereadFiles(files):

    for file in files:
        file_string = file
        dataframe = pd.read_csv(file_string, index_col="Category", sep=';')
        edited_dataframe = refFile(dataframe)
        edited_dataframe.to_csv("new-" + file_string)


def refFile(dataframe):
    dataframe.drop(dataframe.columns[[3]], axis=1, inplace=True)
    dataframe.drop(dataframe.columns[[2]], axis=1, inplace=True)
    dataframe = dataframe[['Category', 'Zkh opname per 100.000', 'Zkh opname']]
    dataframe.columns = ['Category', 'Aantal per 100.000 inwoners', 'Aantal']
    return dataframe
