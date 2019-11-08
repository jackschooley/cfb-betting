import numpy as np
import pandas as pd
from sportsreference.ncaaf.schedule import Schedule
from sportsreference.ncaaf.teams import Teams

#collect team stats for each season
stats2012 = Teams("2012").dataframes
stats2013 = Teams("2013").dataframes
stats2014 = Teams("2014").dataframes
stats2015 = Teams("2015").dataframes
stats2016 = Teams("2016").dataframes
stats2017 = Teams("2017").dataframes
stats2018 = Teams("2018").dataframes

#collect betting data
odds2016 = pd.read_csv("cfb odds 2016.csv")
odds2017 = pd.read_csv("cfb odds 2017.csv")
odds2018 = pd.read_csv("cfb odds 2018.csv")
odds2019 = pd.read_csv("cfb odds 2019.csv")

#drop Idaho from 2012-2017 stats
stats2012 = stats2012.drop("IDAHO")
stats2013 = stats2013.drop("IDAHO")
stats2014 = stats2014.drop("IDAHO")
stats2015 = stats2015.drop("IDAHO")
stats2016 = stats2016.drop("IDAHO")
stats2017 = stats2017.drop("IDAHO")

#add in 2012-2013 stats for App State
appstate2014 = stats2014.loc["APPALACHIAN-STATE"]
stats2012 = stats2012.append(appstate2014)
stats2013 = stats2013.append(appstate2014)

#add in 2012-2014 stats for Charlotte
c2015 = stats2015.loc["CHARLOTTE"]
stats2012 = stats2012.append(c2015)
stats2013 = stats2013.append(c2015)
stats2014 = stats2014.append(c2015)

#add in 2012-2016 stats for Coastal Carolina
cc2017 = stats2017.loc["COASTAL-CAROLINA"]
stats2012 = stats2012.append(cc2017)
stats2013 = stats2013.append(cc2017)
stats2014 = stats2014.append(cc2017)
stats2015 = stats2015.append(cc2017)
stats2016 = stats2016.append(cc2017)

#add in 2012-2013 stats for Georgia Southern
gsouth2014 = stats2014.loc["GEORGIA-SOUTHERN"]
stats2012 = stats2012.append(gsouth2014)
stats2013 = stats2013.append(gsouth2014)

#add in 2012 stats for Georgia State
gstate2013 = stats2013.loc["GEORGIA-STATE"]
stats2012 = stats2012.append(gstate2013)

#add in 2012-2017 stats for Liberty
liberty2018 = stats2018.loc["LIBERTY"]
stats2012 = stats2012.append(liberty2018)
stats2013 = stats2013.append(liberty2018)
stats2014 = stats2014.append(liberty2018)
stats2015 = stats2015.append(liberty2018)
stats2016 = stats2016.append(liberty2018)
stats2017 = stats2017.append(liberty2018)

#add in 2012-2013 stats for Old Dominion
od2014 = stats2014.loc["OLD-DOMINION"]
stats2012 = stats2012.append(od2014)
stats2013 = stats2013.append(od2014)

#add in 2015-2016 stats for UAB
uab2017 = stats2017.loc["ALABAMA-BIRMINGHAM"]
stats2015 = stats2015.append(uab2017)
stats2016 = stats2016.append(uab2017)

#create input data frame
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

self_features = ["first_downs", "fumbles_lost", "interceptions", "pass_attempts", 
                 "pass_completions", "pass_touchdowns", "pass_yards", "penalties", 
                 "points_per_game", "rush_attempts", "rush_touchdowns", "rush_yards", 
                 "yards", "turnovers", "yards_from_penalties"]
opponent_features = ["opponents_first_downs", "opponents_fumbles_lost", 
                     "opponents_interceptions", "opponents_pass_attempts",
                     "opponents_pass_completions", "opponents_pass_touchdowns", 
                     "opponents_pass_yards", "opponents_penalties", 
                     "points_against_per_game", "opponents_rush_attempts", 
                     "opponents_rush_touchdowns", "opponents_rush_yards", 
                     "opponents_yards", "opponents_turnovers", 
                     "opponents_yards_from_penalties"]

home_features = ["home_first_downs", "home_fumbles_lost", "home_interceptions", 
                 "home_pass_attempts", "home_pass_completions", "home_pass_touchdowns", 
                 "home_pass_yards", "home_penalties", "home_points", "home_rush_attempts", 
                 "home_rush_touchdowns", "home_rush_yards", "home_total_yards", 
                 "home_turnovers", "home_yards_from_penalties"]
away_features = ["away_first_downs", "away_fumbles_lost", "away_interceptions", 
                 "away_pass_attempts", "away_pass_completions", "away_pass_touchdowns", 
                 "away_pass_yards", "away_penalties", "away_points", "away_rush_attempts", 
                 "away_rush_touchdowns", "away_rush_yards", "away_total_yards", 
                 "away_turnovers", "away_yards_from_penalties"]

home_self_d = {home_features[n]:self_features[n] for n in range(len(home_features))}
away_self_d = {away_features[n]:self_features[n] for n in range(len(home_features))}
home_oppo_d = {home_features[n]:opponent_features[n] for n in range(len(home_features))}
away_oppo_d = {away_features[n]:opponent_features[n] for n in range(len(home_features))}

weights = [n ** 2 for n in range(1, 6)]

#fix dates
def fix_dates(data):
    for n in range(data.shape[0]):
        date = str(data.at[n, "date"])
        data.loc[n, "date"] = date[:-2] + "-" + date[-2:]

#create weighted average of past years' stats
def prior_weighted_average(years, weights):
    prior_weighted_stats = pd.DataFrame(index = years[0].index, columns = features)
    prior_weighted_stats = prior_weighted_stats.fillna(0)
    for i in range(len(years)):
        weight = years[i].multiply(weights[i])
        prior_weighted_stats = prior_weighted_stats.add(weight)
    prior_weighted_stats = prior_weighted_stats.div(sum(weights[:len(years)]))
    return prior_weighted_stats

#create the stats from the current year that were current as of game time
def contemp_stats(schedule, date, name, current_year):
    stats = pd.DataFrame(index = [0], columns = features)
    stats = stats.fillna(0)
    i = 0
    for game in schedule:
        match = game.boxscore.dataframe
        try:
            url = match.index[0]
        except AttributeError:
            if current_year:
                #you'll have to do this twice (once for home and away)
                new_date = input("Enter the updated date: ")
                return contemp_stats(schedule, new_date, name, current_year)
            stats.loc[0] = np.NaN
            return stats.loc[0]
        if date in url:
            break
        if name.lower() in url:
            match.rename(index = {url:0}, columns = home_self_d, inplace = True)
            match.rename(columns = away_oppo_d, inplace = True)
        else:
            match.rename(index = {url:0}, columns = away_self_d, inplace = True)           
            match.rename(columns = home_oppo_d, inplace = True)
        stats[self_features] += match[self_features]
        stats[opponent_features] += match[opponent_features]
        i += 1
    if i == 0:
        stats = stats.drop(0)
        return stats
    else:
        stats = stats.div(i)
        return stats.loc[0]

#merge weighted stats from previous years with contemporary stats
def weighted_stats(prior_stats, contemp_stats, weights):
    if not contemp_stats.empty:
        prior_weighted = prior_stats.multiply(sum(weights[:-1]))
        contemp_weighted = contemp_stats.multiply(weights[-1])
        mixed_stats = prior_weighted.add(contemp_weighted)
        mixed_stats = mixed_stats.div(sum(weights))
        return mixed_stats
    return prior_stats

def create_game_stats(prior_years, game_data, weights, year, loud = True):
    if year == 2019:
        current_year = True
    else:
        current_year = False
    prior_stats = prior_weighted_average(prior_years, weights)
    schedules = {}
    for feature in diff_features:
        game_data.insert(game_data.shape[1], feature, 0)
    for feature in level_features:
        game_data.insert(game_data.shape[1], feature, 0)
    fix_dates(game_data)
    for i in range(game_data.shape[0]):
        if loud:
            print(i)
        date = game_data.at[i, "date"]
        
        away_team = game_data.at[i, "away"]
        away_prior_stats = prior_stats.loc[away_team]
        if away_team in schedules:
            away_schedule = schedules[away_team]
        else:
            try:
                away_schedule = Schedule(away_team, year)
            except:
                continue
            schedules[away_team] = away_schedule
        away_contemp_stats = contemp_stats(away_schedule, date, away_team, current_year)
        away_stats = weighted_stats(away_prior_stats, away_contemp_stats, weights)
        
        home_team = game_data.at[i, "home"]
        home_prior_stats = prior_stats.loc[home_team]
        if home_team in schedules:
            home_schedule = schedules[home_team]
        else:
            try:
                home_schedule = Schedule(home_team, year)
            except:
                continue
            schedules[home_team] = home_schedule
        home_contemp_stats = contemp_stats(home_schedule, date, home_team, current_year)
        home_stats = weighted_stats(home_prior_stats, home_contemp_stats, weights)
        
        diff_stats = home_stats.sub(away_stats)
        diff_stats.rename(index = diff_d, inplace = True)
        game_data.at[i, diff_features] = diff_stats
        
        level_stats = home_stats
        level_stats.rename(index = level_d, inplace = True)
        game_data.at[i, level_features] = level_stats
    game_data.dropna(inplace = True)