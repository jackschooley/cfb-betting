import pandas as pd
import matplotlib.pyplot as plt
from sportsreference.ncaaf.teams import Teams
from sklearn import linear_model

#collect team stats for each season
stats2014 = Teams("2014").dataframes
stats2015 = Teams("2015").dataframes
stats2016 = Teams("2016").dataframes
stats2017 = Teams("2017").dataframes
stats2018 = Teams("2018").dataframes
stats2019 = Teams("2019").dataframes

#collect betting data
odds2015 = pd.read_csv("cfb games 2015.csv")
odds2016 = pd.read_csv("cfb games 2016.csv")
odds2017 = pd.read_csv("cfb games 2017.csv")
odds2018 = pd.read_csv("cfb games 2018.csv")
odds2019 = pd.read_csv("cfb games 2019.csv")

#drop Idaho from 2014, 2015, 2016, 2017 stats
stats2014 = stats2014.drop("IDAHO")
stats2015 = stats2015.drop("IDAHO")
stats2016 = stats2016.drop("IDAHO")
stats2017 = stats2017.drop("IDAHO")

#add in 2014 stats for Charlotte
c2015 = stats2015.loc["CHARLOTTE"]
stats2014 = stats2014.append(c2015)

#add in 2014, 2015, 2016 stats for Coastal Carolina
cc2017 = stats2017.loc["COASTAL-CAROLINA"]
stats2014 = stats2014.append(cc2017)
stats2015 = stats2015.append(cc2017)
stats2016 = stats2016.append(cc2017)

#add in 2015, 2016 stats for UAB
uab2017 = stats2017.loc["ALABAMA-BIRMINGHAM"]
stats2015 = stats2015.append(uab2017)
stats2016 = stats2016.append(uab2017)

#add in 2014, 2015, 2016, 2017 stats for Liberty
liberty2018 = stats2018.loc["LIBERTY"]
stats2014 = stats2014.append(liberty2018)
stats2015 = stats2015.append(liberty2018)
stats2016 = stats2016.append(liberty2018)
stats2017 = stats2017.append(liberty2018)

#create input data frame
features = ["first_downs", "opponents_first_downs", "first_downs_from_penalties", 
        "opponents_first_downs_from_penalties", "fumbles_lost", "opponents_fumbles_lost",
        "interceptions", "opponents_interceptions", "pass_attempts",
        "opponents_pass_attempts", "pass_completion_percentage",
        "opponents_pass_completion_percentage", "pass_completions", 
        "opponents_pass_completions", "pass_first_downs", "opponents_pass_first_downs",
        "pass_touchdowns", "opponents_pass_touchdowns", "pass_yards", 
        "opponents_pass_yards", "penalties", "opponents_penalties", "plays", 
        "opponents_plays", "points_against_per_game", "points_per_game", "rush_attempts",
        "opponents_rush_attempts", "rush_first_downs", "opponents_rush_first_downs", 
        "rush_touchdowns", "opponents_rush_touchdowns", "rush_yards", 
        "opponents_rush_yards", "rush_yards_per_attempt", 
        "opponents_rush_yards_per_attempt", "turnovers", "opponents_turnovers", "yards",
        "opponents_yards", "yards_from_penalties", "opponents_yards_from_penalties",
        "yards_per_play", "opponents_yards_per_play"]

def weighted_average(years, weights):
    weighted_stats = pd.DataFrame(index = stats2017.index, columns = features)
    weighted_stats = weighted_stats.fillna(0)
    for i in range(4):
        weight = years[i].multiply(weights[i])
        weighted_stats = weighted_stats.add(weight)
    weighted_stats = weighted_stats.div(sum(weights))
    return weighted_stats

def create_game_stats(years, game_data, weights):
    weighted_stats = weighted_average(years, weights)
    for feature in features:
        game_data.insert(game_data.shape[1], feature, 0)
    for i in range(game_data.shape[0]):
        away_team = game_data.at[i, "away"]
        home_team = game_data.at[i, "home"]
        away_stats = weighted_stats.loc[away_team]
        home_stats = weighted_stats.loc[home_team]
        game_stats = home_stats.sub(away_stats)
        game_data.at[i, features] = game_stats

weights = [n ** 2 for n in range(1, 5)]
y2017 = [stats2014[features], stats2015[features], stats2016[features], stats2017[features]]
y2018 = [stats2015[features], stats2016[features], stats2017[features], stats2018[features]]
create_game_stats(y2017, odds2017, weights)
create_game_stats(y2018, odds2018, weights)

#run lasso after cross-validating
x_lasso_train = odds2017[features]
y_train = odds2017.home_score.sub(odds2017.away_score)
lasso_cv = linear_model.LassoCV(cv = 10)
lasso_cv.fit(x_lasso_train, y_train)

lasso = linear_model.Lasso(lasso_cv.alpha_)
lasso.fit(x_lasso_train, y_train)
selected_vars = []
for i in range(len(lasso.coef_)):
    if lasso.coef_[i]:
        selected_vars.append(features[i])

#run spread model 
x_train = x_lasso_train[selected_vars]
reg = linear_model.LinearRegression()
reg.fit(x_train, y_train)

x_test = odds2018[selected_vars]
predicted_margins = reg.predict(x_test)
true_margins = odds2018.home_score.sub(odds2017.away_score)

#test
games = []
probs = []
thresholds = [x * 0.5 for x in range(22)]
for threshold in thresholds:
    picks = []
    ats_winners = []
    for i in range(odds2018.shape[0]):
        try:
            spread = float(odds2018.loc[i, "spread"])
        except ValueError:
            spread = 0
        if predicted_margins[i] > spread + threshold:
            picks.append(odds2018.loc[i, "home"])
        elif predicted_margins[i] < spread - threshold:
            picks.append(odds2018.loc[i, "away"])
        else:
            picks.append("no pick")
        if true_margins[i] > spread:
            ats_winners.append(odds2018.loc[i, "home"])
        else:
            ats_winners.append(odds2018.loc[i, "away"])
        
    wins = 0
    losses = 0
    for i in range(len(picks)):
        if picks[i] == ats_winners[i]:
            wins += 1
        elif picks[i] != "no pick":
            losses += 1
    game = wins + losses
    prob = wins / game
    games.append(game)
    probs.append(prob)

plt.plot(games, probs)