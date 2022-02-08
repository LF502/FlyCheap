import pandas
import pandasgui
import pathlib

if __name__ == "__main__":
    file = pathlib.Path("time-rate.xlsx")
    data = pandas.read_excel(file, index_col=0).iloc[0:4, :]
    data = pandas.DataFrame(data.values.T, index=data.columns, columns=data.index)
    pandasgui.show(data)
    