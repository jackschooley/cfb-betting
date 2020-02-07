import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn import metrics
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

#import data
games2015 = pd.read_csv("cfb games 2015.csv")
games2016 = pd.read_csv("cfb games 2016.csv")
games2017 = pd.read_csv("cfb games 2017.csv")
games2018 = pd.read_csv("cfb games 2018.csv")
games2019 = pd.read_csv("cfb games 2019.csv")

base_features = ["first_downs", "opponents_first_downs", "fumbles_lost", 
                 "opponents_fumbles_lost", "interceptions", "opponents_interceptions",
                 "pass_attempts", "opponents_pass_attempts", "pass_touchdowns", 
                 "opponents_pass_touchdowns", "rush_attempts", "opponents_rush_attempts", 
                 "rush_touchdowns", "opponents_rush_touchdowns", 
                 "pass_completion_percentage", "opponents_pass_completion_percentage", 
                 "pass_yards_per_attempt", "opponents_pass_yards_per_attempt",
                 "points_per_play", "opponents_points_per_play", "rush_yards_per_attempt", 
                 "opponents_rush_yards_per_attempt"]

a_features = ["a_" + feature for feature in base_features]
h_features = ["h_" + feature for feature in base_features]

conferences = ["acc", "american", "big-12", "big-ten", "cusa", "mac", "mwc", "pac-12", 
               "sec", "sun-belt"]
a_conferences = ["a_" + conference for conference in conferences]
h_conferences = ["h_" + conference for conference in conferences]

other_features = ["simple_rating_system", "strength_of_schedule"]
a_other = ["a_" + feature for feature in other_features]
h_other = ["h_" + feature for feature in other_features]

features = a_features + a_other + h_features + h_other

#subset for "competitive" data (doesn't include weeks 0-3 or bowl games)
games2015 = games2015.iloc[135:667] #135-667
games2016 = games2016.iloc[136:683] #136-683
games2017 = games2017.iloc[118:681] #118-681
games2018 = games2018.iloc[134:721] #134-721
games2019 = games2019.iloc[139:707] #139-707

#specify test and train
train = pd.concat([games2015, games2016, games2017, games2018])
train = train.reset_index()
test = games2019
test = test.reset_index()

x_train = train[features]
x_test = test[features]

y_train = np.array((train.away_score, train.home_score)).T
y_test = np.array((test.away_score, test.home_score)).T
true_margins = test.home_score - test.away_score

#create dictionary to store predicted margins and mse
predictions = {}
mse = {}

#linear regression
lin_reg = linear_model.LinearRegression()
lin_reg.fit(x_train, y_train)
predictions["linear"] = lin_reg.predict(x_test)
mse["linear"] = metrics.mean_squared_error(y_test, predictions["linear"])
    
#principal component analysis
pca = PCA(n_components = "mle")
x_pca_train = pca.fit_transform(x_train)
x_pca_test = pca.transform(x_test)

pca_reg = linear_model.LinearRegression()
pca_reg.fit(x_pca_train, y_train)
predictions["pca"] = pca_reg.predict(x_pca_test)
mse["pca"] = metrics.mean_squared_error(y_test, predictions["pca"])

#random forest
rf = RandomForestRegressor(1000, min_samples_split = 10, min_samples_leaf = 3, 
                           max_features = "sqrt", bootstrap = False)
rf.fit(x_train, y_train)
predictions["rf"] = rf.predict(x_test)
mse["rf"] = metrics.mean_squared_error(y_test, predictions["rf"])

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
            predicted_margin = predicted_margins[i][1] - predicted_margins[i][0]
            spread = float(test.loc[i, "spread"])
            if abs(spread) > 28:
                picks.append("no pick")
            elif predicted_margin - spread > threshold:
                picks.append(test.loc[i, "home"])
            elif predicted_margin - spread < -threshold:
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
            prediction = predicted_margins[i][1] - predicted_margins[i][0]
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
plt.xlabel("threshold")
plt.ylabel("accuracy")
#plt.ylabel("balance")

plt.legend(labels = predictions.keys())
plt.axhline(0.524, color = "red") #use when plotting probabilities
#plt.axhline(100, color = "red") #use when plotting final balances