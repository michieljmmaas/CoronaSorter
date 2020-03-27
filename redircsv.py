import pandas as pd


def rereadFiles(files):
    for file in files:
        file_string = file
        dataframe = pd.read_csv(file_string)
        dataframe.set_index("Category", inplace=True)
        # dataframe.drop(dataframe.columns[[0]], axis=1, inplace=True)
        # dataframe = dataframe[['Category', 'Aantal per 100.000 inwoners', 'Aantal']]
        # dataframe[0]['Category'] = 's-Gravenhage'
        dataframe.to_csv(file_string)
