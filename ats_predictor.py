import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSSVD
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR

#import data
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

#subset for "competitive" data (doesn't include weeks 0-3 or bowl games)
games2016 = games2016.iloc[134:681] #134-681
games2017 = games2017.iloc[118:681] #118-681
games2018 = games2018.iloc[134:734] #134-734
games2019 = games2019.iloc[139:] #139-

#specify test and train
train = games2016
train = train.reset_index()
test = games2017.append(games2018.append(games2019))
test = test.reset_index()

x_train = train[features]
x_test = test[features]

y_train = train.home_score.sub(train.away_score)
true_margins = test.home_score.sub(test.away_score)

#create dictionary to store predicted margins
predictions = {}

#calculate home field advantage coefficient
hfa = sum(train["home_score"] - train["away_score"]) / train.shape[0]

#run lasso after cross-validating
lasso_cv = linear_model.LassoCV(cv = 10, max_iter = 1000000)
lasso_cv.fit(x_train, y_train)

lasso = linear_model.Lasso(lasso_cv.alpha_, max_iter = 1000000)
lasso.fit(x_train, y_train)

lasso_selected_vars = []
for i in range(len(lasso.coef_)):
    if lasso.coef_[i]:
        lasso_selected_vars.append(features[i])
x_lasso_train = x_train[lasso_selected_vars]
x_lasso_test = x_test[lasso_selected_vars]

lasso_reg = linear_model.LinearRegression()
lasso_reg.fit(x_lasso_train, y_train)
#predictions["lasso"] = lasso_reg.predict(x_lasso_test)

#principal component analysis
pca = PCA(n_components = 0.9, svd_solver = "full")
x_pca_train = pca.fit_transform(x_train)
x_pca_test = pca.transform(x_test)

pca_reg = linear_model.LinearRegression()
pca_reg.fit(x_pca_train, y_train)
#predictions["pca"] = pca_reg.predict(x_pca_test)

#partial least squares
pls = PLSSVD()
pls.fit(x_train, y_train)
x_pls_train = pls.transform(x_train)
x_pls_test = pls.transform(x_test)

pls_reg = linear_model.LinearRegression()
pls_reg.fit(x_pls_train, y_train)
#predictions["pls"] = pls_reg.predict(x_pls_test)

#random forest
rf = RandomForestRegressor(100)
rf.fit(x_pca_train, y_train)
#predictions["rf"] = rf.predict(x_pca_test)

#support vector machine
svm = LinearSVR(max_iter = 10000000)
svm.fit(x_pca_train, y_train)
predictions["svm-0"] = svm.predict(x_pca_test)

#test
thresholds = [x * 0.5 for x in range(30)] #stop at 14.5 points
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
            if predicted_margins[i] > spread + threshold:
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
            spread = float(test.loc[i, "spread"])
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
        
        budget = 1000
        total_bet = 0
        for i in range(test.shape[0]):
            spread = float(test.loc[i, "spread"])
            if picks[i] != "no pick":
                bet = budget * 0.01
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
    plt.plot(thresholds, probs)

plt.title("accuracy comparison")
plt.legend(labels = predictions.keys())
plt.axhline(0.55, color = "red")

#i think i'm gonna go with the svm using principal components