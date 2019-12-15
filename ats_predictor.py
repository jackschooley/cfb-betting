import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn import metrics
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR

#import data
games2017 = pd.read_csv("cfb games 2017.csv")
games2018 = pd.read_csv("cfb games 2018.csv")

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
games2017 = games2017.iloc[220:675] #115-675
games2018 = games2018.iloc[242:715] #133-715

#specify test and train
train = games2017
train = train.reset_index()
test = games2018
test = test.reset_index()

x_train = train[features]
x_test = test[features]

y_train = train["spread"]
y_test = test["spread"]
true_margins = test.home_score - test.away_score

#create dictionary to store predicted margins and mse
predictions = {}
mse = {}

#principal component analysis
pca = PCA(n_components = "mle")
x_pca_train = pca.fit_transform(x_train)
x_pca_test = pca.transform(x_test)

pca_reg = linear_model.LinearRegression()
pca_reg.fit(x_pca_train, y_train)
predictions["linear"] = pca_reg.predict(x_pca_test)
mse["linear"] = metrics.mean_squared_error(y_test, predictions["linear"])

#random forest
rf = RandomForestRegressor(1000)
rf.fit(x_train, y_train)
predictions["rf"] = rf.predict(x_test)
mse["rf"] = metrics.mean_squared_error(y_test, predictions["rf"])

#support vector machine
svm = LinearSVR(max_iter = 10000000)
svm.fit(x_train, y_train)
predictions["linear-svm"] = svm.predict(x_test)
mse["linear-svm"] = metrics.mean_squared_error(y_test, predictions["linear-svm"])

#determine bet amount
def wager(budget, spread, prediction, odds = -110):
    def convert_odds(odds):
        if odds > 0:
            decimal_odds = odds + 1
        else:
            decimal_odds = 100 / -odds + 1
        return round(decimal_odds, 3)
    decimal_odds = convert_odds(odds)
    difference = abs(prediction - spread)
    proportion = difference / decimal_odds
    bet = budget * max(proportion, 5) / 100
    return bet
    
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
            if abs(spread) > 21:
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
        for i in range(test.shape[0]):
            spread = test.loc[i, "spread"]
            prediction = predicted_margins[i]
            if picks[i] != "no pick":
                bet = wager(budget, spread, prediction)
                if picks[i] == ats_winners[i]:
                    winning = bet * 10/11
                    budget += winning
                elif ats_winners[i] == "push":
                    pass
                elif picks[i] != "no pick":
                    budget -= bet
        final_balances.append(budget)
    plt.plot(thresholds, probs) #plot probabilities as a function of threshold
    #plt.plot(thresholds, final_balances) #plot final balances as a function of threshold

plt.title("accuracy comparison")
plt.legend(labels = predictions.keys())
plt.axhline(0.55, color = "red") #use when plotting probabilities
#plt.axhline(100, color = "red") #use when plotting final balances