import pandas as pd
from sportsreference.ncaaf.teams import Teams
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

#import team stats
stats2015 = Teams("2015").dataframes
stats2016 = Teams("2016").dataframes
stats2017 = Teams("2017").dataframes
stats2018 = Teams("2018").dataframes
stats2019 = Teams("2019").dataframes

#drop Idaho from 2015-2017 stats
stats2015 = stats2015.drop("IDAHO")
stats2016 = stats2016.drop("IDAHO")
stats2017 = stats2017.drop("IDAHO")

#add in 2015-2016 stats for Coastal Carolina
cc2017 = stats2017.loc["COASTAL-CAROLINA"]
stats2015 = stats2015.append(cc2017)
stats2016 = stats2016.append(cc2017)

#add in 2015-2017 stats for Liberty
liberty2018 = stats2018.loc["LIBERTY"]
stats2015 = stats2015.append(liberty2018)
stats2016 = stats2016.append(liberty2018)
stats2017 = stats2017.append(liberty2018)

#add in 2015-2016 stats for UAB
uab2017 = stats2017.loc["ALABAMA-BIRMINGHAM"]
stats2015 = stats2015.append(uab2017)
stats2016 = stats2016.append(uab2017)

#import past game data
games2016 = pd.read_csv("cfb games 2016.csv")
games2017 = pd.read_csv("cfb games 2017.csv")
games2018 = pd.read_csv("cfb games 2018.csv")
games2019 = pd.read_csv("cfb games 2019.csv")

#subset
games2018 = games2018.iloc[134:735]
games2019 = games2019.iloc[139:]
current_games = pd.read_csv("current games.csv")

#create test stats
features = ["first_downs", "opponents_first_downs", "fumbles_lost", 
            "opponents_fumbles_lost", "interceptions", "opponents_interceptions", 
            "pass_attempts", "opponents_pass_attempts",  "pass_completions", 
            "opponents_pass_completions", "pass_touchdowns", "opponents_pass_touchdowns", 
            "pass_yards", "opponents_pass_yards", "penalties", "opponents_penalties", 
            "points_against_per_game", "points_per_game", "rush_attempts",
            "opponents_rush_attempts", "rush_touchdowns", "opponents_rush_touchdowns", 
            "rush_yards", "opponents_rush_yards", "yards", "opponents_yards", "turnovers", 
            "opponents_turnovers", "yards_from_penalties", 
            "opponents_yards_from_penalties"]

diff_features = ["d_" + feature for feature in features]
level_features = ["l_" + feature for feature in features]

diff_d = {feature:"d_" + feature for feature in features}
level_d = {feature:"l_" + feature for feature in features}

#create weighted stats
for feature in diff_features:
    current_games.insert(current_games.shape[1], feature, 0)
for feature in level_features:
    current_games.insert(current_games.shape[1], feature, 0)
weights = [n ** 2 for n in range(1, 6)]
years = [stats2015[features], stats2016[features], stats2017[features], 
         stats2018[features], stats2019[features]]

weighted_stats = pd.DataFrame(index = years[0].index, columns = features)
weighted_stats = weighted_stats.fillna(0)
for i in range(len(years)):
    weight = years[i].multiply(weights[i])
    weighted_stats = weighted_stats.add(weight)
weighted_stats = weighted_stats.div(sum(weights))

for i in range(current_games.shape[0]):
    away_team = current_games.at[i, "away"]
    home_team = current_games.at[i, "home"]
    
    diff_stats = weighted_stats.loc[home_team] - weighted_stats.loc[away_team]
    diff_stats.rename(index = diff_d, inplace = True)
    current_games.loc[i, diff_features] = diff_stats
    
    level_stats = weighted_stats.loc[home_team]
    level_stats.rename(index = level_d, inplace = True)
    current_games.loc[i, level_features] = level_stats

#specify test and train
train = games2018
test = current_games

x_train = train[diff_features + level_features]
x_test = test[diff_features + level_features]

y_train = train["spread"]

#predict spreads
pca = PCA(n_components = 0.8, svd_solver = "full")
x_pca_train = pca.fit_transform(x_train)
x_pca_test = pca.transform(x_test)
    
pca_reg = LinearRegression()
pca_reg.fit(x_pca_train, y_train)
predictions = pd.Series(pca_reg.predict(x_pca_test), name = "predicted_spread")

#determine bet amount
def wager(budget, difference, odds = -110):
    def convert_odds(odds):
        if odds > 0:
            decimal_odds = odds + 1
        else:
            decimal_odds = 100 / -odds + 1
        return round(decimal_odds, 3)
    decimal_odds = convert_odds(odds)
    proportion = abs(difference) / decimal_odds
    bet = budget * min(proportion / 100, 0.05)
    return round(bet, 2)

#create prediction df
core = ["away", "home", "spread", "away_odds", "home_odds"]
predicted_spreads = current_games[core].join(predictions)

#generate bets
budget = 100
threshold = 4.5
cutoff = 18
picks = []
bets = []
differences = predicted_spreads.predicted_spread - predicted_spreads.spread
for i in range(predicted_spreads.shape[0]):
    if abs(predicted_spreads.at[i, "spread"]) < cutoff:
        if differences[i] < -threshold:
            picks.append(predicted_spreads.at[i, "away"])
            odds = predicted_spreads.at[i, "away_odds"]
            bet = wager(budget, differences[i], odds)
            bets.append(bet)
        elif differences[i] > threshold:
            picks.append(predicted_spreads.at[i, "home"])
            odds = predicted_spreads.at[i, "home_odds"]
            bet = wager(budget, differences[i], odds)
            bets.append(bet)
        else:
            picks.append("no pick")
            bets.append(0)
    else:
        picks.append("no pick")
        bets.append(0)
        
picks = pd.Series(picks, name = "picks")
bets = pd.Series(bets, name = "bets")
predicted_spreads = predicted_spreads.join([picks, bets])

#print bets
for i in range(predicted_spreads.shape[0]):
    series = predicted_spreads.loc[i]
    if series["picks"] != "no pick":
        pick = series["picks"]
        amount = series["bets"]
        print(amount, "on", pick)
