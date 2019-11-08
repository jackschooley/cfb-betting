import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR

#import data
games2016 = pd.read_csv("cfb games 2016.csv")
games2017 = pd.read_csv("cfb games 2017.csv")
games2018 = pd.read_csv("cfb games 2018.csv")
games2019 = pd.read_csv("cfb games 2019.csv")

base_features = ["first_downs", "opponents_first_downs", "fumbles_lost", 
            "opponents_fumbles_lost", "interceptions", "opponents_interceptions", 
            "pass_attempts", "opponents_pass_attempts",  "pass_completions", 
            "opponents_pass_completions", "pass_touchdowns", "opponents_pass_touchdowns", 
            "pass_yards", "opponents_pass_yards", "penalties", "opponents_penalties", 
            "points_against_per_game", "points_per_game", "rush_attempts",
            "opponents_rush_attempts", "rush_touchdowns", "opponents_rush_touchdowns", 
            "rush_yards", "opponents_rush_yards", "yards", "opponents_yards", "turnovers", 
            "opponents_turnovers", "yards_from_penalties", 
            "opponents_yards_from_penalties"]

diff_features = ["d_" + feature for feature in base_features]
level_features = ["l_" + feature for feature in base_features]
features = diff_features + level_features

#subset for "competitive" data (doesn't include weeks 0-3 or bowl games)
games2016 = games2016.iloc[134:682] #134-682
games2017 = games2017.iloc[118:682] #118-682
games2018 = games2018.iloc[134:735] #134-735
games2019 = games2019.iloc[139:] #139-

#specify test and train
train = games2018
train = train.reset_index()
test = games2019[134:]
test = test.reset_index()

x_train = train[features]
x_test = test[features]

y_train = train["spread"]
true_margins = test.home_score - test.away_score

#create dictionary to store predicted margins
predictions = {}

#principal component analysis
pca = PCA(n_components = 0.8, svd_solver = "full")
x_pca_train = pca.fit_transform(x_train)
x_pca_test = pca.transform(x_test)

pca_reg = linear_model.LinearRegression()
pca_reg.fit(x_pca_train, y_train)
predictions["linear"] = pca_reg.predict(x_pca_test)

#random forest
rf = RandomForestRegressor(100)
rf.fit(x_pca_train, y_train)
predictions["rf"] = rf.predict(x_pca_test)

#support vector machine
svm = LinearSVR(epsilon = 0.5, max_iter = 10000000)
svm.fit(x_pca_train, y_train)
predictions["svm"] = svm.predict(x_pca_test)

#test
thresholds = [x * 0.5 for x in range(22)] #stop at 10.5 points
for method in predictions:
    predicted_margins = predictions[method]
    games = []
    probs = []
    final_balances = []
    total_bets = []
    for threshold in thresholds:
        picks = []
        ats_winners = []
        for i in range(test.shape[0]):
            spread = float(test.loc[i, "spread"])
            if abs(spread) > 18:
                picks.append("no pick")
            elif predicted_margins[i] > spread + threshold:
                picks.append(test.loc[i, "home"])
            elif predicted_margins[i] < spread - threshold:
                picks.append(test.loc[i, "away"])
            else:
                picks.append("no pick")
            if true_margins[i] > spread:
                ats_winners.append(test.loc[i, "home"])
            elif true_margins[i] < spread:
                ats_winners.append(test.loc[i, "away"])
            else:
                ats_winners.append("push")
        
        wins = 0
        losses = 0
        pushes = 0
        for i in range(len(picks)):
            spread = test.loc[i, "spread"]
            if picks[i] == ats_winners[i]:
                wins += 1
            elif ats_winners[i] == "push":
                pushes += 1
            elif picks[i] != "no pick":
                losses += 1
        plays = wins + losses
        prob = wins / plays
        games.append(plays)
        probs.append(prob)
        
        budget = 100
        total_bet = 0
        for i in range(test.shape[0]):
            spread = test.loc[i, "spread"]
            if picks[i] != "no pick":
                bet = 5
                total_bet += bet
                if picks[i] == ats_winners[i]:
                    winning = bet * 10/11
                    budget += winning
                elif ats_winners[i] == "push":
                    pass
                elif picks[i] != "no pick":
                    budget -= bet
        final_balances.append(budget)
        total_bets.append(total_bet)
    plt.plot(thresholds, final_balances)

plt.title("accuracy comparison")
plt.legend(labels = predictions.keys())
plt.axhline(100, color = "red")

#principal component regression is the way to go!!!