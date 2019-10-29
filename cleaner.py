import pandas as pd
from fix_names import d

def clean(data, name):
    indices = list(range(int(data.shape[0] / 2)))
    columns = ["date", "away", "home", "away_score", "home_score", "away_ml", "home_ml", 
               "spread", "o/u"]
    output = pd.DataFrame(index = indices, columns = columns)
    output = output.fillna(0)

    i = 0
    j = 0
    while i < int(data.shape[0] / 2):
        output.loc[i, "date"] = data.loc[j, "Date"]
        output.loc[i, "away"] = d.get(data.loc[j, "Team"])
        output.loc[i, "home"] = d.get(data.loc[j + 1, "Team"])
        output.loc[i, "away_score"] = data.loc[j, "Final"]
        output.loc[i, "home_score"] = data.loc[j + 1, "Final"]
        output.loc[i, "away_ml"] = data.loc[j, "ML"]
        output.loc[i, "home_ml"] = data.loc[j + 1, "ML"]
        if output.loc[i, "away_ml"] < output.loc[i, "home_ml"]:
            try:
                output.loc[i, "spread"] = -1 * float(data.loc[j, "Close"])
            except ValueError:
                output.loc[i, "spread"] = data.loc[j, "Close"]
            output.loc[i, "o/u"] = data.loc[j + 1, "Close"]
        else:
            output.loc[i, "spread"] = data.loc[j + 1, "Close"]
            output.loc[i, "o/u"] = data.loc[j, "Close"]
        i += 1
        j += 2
    
    output.to_csv(name + ".csv", index = False)
    
for year in range(2014, 2020):
    title = "ncaa football " + str(year) + ".xlsx"
    data = pd.read_excel(title)
    clean(data, "cfb odds " + str(year + 10))