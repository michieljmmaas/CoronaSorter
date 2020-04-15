import pandas as pd


def rereadFiles(files):

    for file in files:
        file_string = file
        dataframe = pd.read_csv(file_string, index_col="Category", sep=';')
        # dataframe.set_index("Category", inplace=True)
        dataframe.drop(dataframe.columns[[3]], axis=1, inplace=True)
        dataframe.drop(dataframe.columns[[2]], axis=1, inplace=True)
        dataframe.columns = ['Aantal per 100.000 inwoners', 'Aantal']
        print(dataframe)
        # dataframe = dataframe[['Aantal per 100.000 inwoners', 'Aantal']]
        # dataframe[0]['Category'] = 's-Gravenhage'
        dataframe.to_csv("new-" + file_string)
