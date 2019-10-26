import pandas as pd

def clean(data, name):
    indices = list(range(int(len(data) / 2)))
    columns = ["date", "away", "home", "away_score", "home_score", "away_ml", "home_ml", 
               "spread", "o/u"]
    output = pd.DataFrame(index = indices, columns = columns)
    output = output.fillna(0)

    i = 0
    j = 0
    while i < int(len(data) / 2):
        output.date[i] = data.Date[j]
        output.away[i] = data.Team[j]
        output.home[i] = data.Team[j + 1]
        output.away_score[i] = data.Final[j]
        output.home_score[i] = data.Final[j + 1]
        output.away_ml[i] = data.ML[j]
        output.home_ml[i] = data.ML[j + 1]
        if output.away_ml[i] < output.home_ml[i]:
            try:
                output.spread[i] = -1 * float(data.Close[j])
            except ValueError:
                output.spread[i] = data.Close[j]
            output["o/u"][i] = data.Close[j + 1]
        else:
            output.spread[i] = data.Close[j + 1]
            output["o/u"][i] = data.Close[j]
        i += 1
        j += 2
    
    output.to_csv(name + ".csv", index = False)
    
for year in range(2015, 2020):
    title = "ncaa football " + str(year) + ".xlsx"
    data = pd.read_excel(title)
    clean(data, "cfb games " + str(year))