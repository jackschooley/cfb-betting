import pandas as pd
from sportsreference.ncaaf.teams import Teams

#collect team stats for each season
redshirts = Teams("2015").dataframes
seniors = Teams("2016").dataframes
juniors = Teams("2017").dataframes
sophomores = Teams("2018").dataframes
freshmen = Teams("2019").dataframes

#collect betting data
odds2015 = pd.read_csv("cfb games 2015.csv")
odds2016 = pd.read_csv("cfb games 2016.csv")
odds2017 = pd.read_csv("cfb games 2017.csv")
odds2018 = pd.read_csv("cfb games 2018.csv")
odds2019 = pd.read_csv("cfb games 2019.csv")

#create input data frame

#run lasso

#run spread model

#test