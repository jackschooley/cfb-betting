import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

#import data
games2014 = pd.read_csv("cfb games 2014.csv")
games2015 = pd.read_csv("cfb games 2015.csv")
games2016 = pd.read_csv("cfb games 2016.csv")
games2017 = pd.read_csv("cfb games 2017.csv")
games2018 = pd.read_csv("cfb games 2018.csv")
games2019 = pd.read_csv("cfb games 2019.csv")

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

#run lasso after cross-validating
x_lasso_train = games2018[features]
y_train = games2018.home_score.sub(games2018.away_score)
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

x_test = games2019[selected_vars]
predicted_margins = reg.predict(x_test)
true_margins = games2019.home_score.sub(games2019.away_score)

#test
games = []
probs = []
thresholds = [x * 0.5 for x in range(22)]
for threshold in thresholds:
    picks = []
    ats_winners = []
    for i in range(games2019.shape[0]):
        try:
            spread = float(games2019.loc[i, "spread"])
        except ValueError:
            spread = 0
        if predicted_margins[i] > spread + threshold:
            picks.append(games2019.loc[i, "home"])
        elif predicted_margins[i] < spread - threshold:
            picks.append(games2019.loc[i, "away"])
        else:
            picks.append("no pick")
        if true_margins[i] > spread:
            ats_winners.append(games2019.loc[i, "home"])
        else:
            ats_winners.append(games2019.loc[i, "away"])
        
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