import pandas as pd
from sportsreference.ncaaf.teams import Teams
from sklearn.decomposition import PCA
from sklearn.svm import LinearSVR

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

odds2019 = pd.read_csv("cfb odds 2019.csv")

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

current_games = odds2019[501:].reset_index()
for feature in features:
    current_games.insert(current_games.shape[1], feature, 0)
weights = [n ** 2 for n in range(1, 6)]
years = [stats2015[features], stats2016[features], stats2017[features], stats2018[features],
         stats2019[features]]

def weighted_average(years, weights):
    weighted_stats = pd.DataFrame(index = years[0].index, columns = features)
    weighted_stats = weighted_stats.fillna(0)
    for i in range(len(years)):
        weight = years[i].multiply(weights[i])
        weighted_stats = weighted_stats.add(weight)
    weighted_stats = weighted_stats.div(sum(weights))
    return weighted_stats

weighted_stats = weighted_average(years, weights)

for i in range(current_games.shape[0]):
    away_team = current_games.at[i, "away"]
    home_team = current_games.at[i, "home"]
    game_stats = weighted_stats.loc[home_team] - weighted_stats.loc[away_team]
    current_games.loc[i, features] = game_stats

#specify test and train
train = games2016.append(games2017.append(games2018.append(games2019)))
test = current_games

x_train = train[features]
x_test = test[features]

y_train = train.home_score.sub(train.away_score)

#fit model using 100 iterations
iterations = pd.DataFrame(columns = range(test.shape[0]))
for i in range(10):
    pca = PCA(n_components = 0.9, svd_solver = "full", random_state = i + 1)
    x_pca_train = pca.fit_transform(x_train)
    x_pca_test = pca.transform(x_test)
    for j in range(10):
        svm = LinearSVR(max_iter = 10000000, random_state = j + 1)
        svm.fit(x_pca_train, y_train)
        iteration = pd.Series(svm.predict(x_pca_test))
        iterations = iterations.append(iteration, ignore_index = True)
        
predictions = iterations.mean()