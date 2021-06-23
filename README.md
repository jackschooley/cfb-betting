# cfb-betting: College Football Betting

## About

This repository contains an against-the-spread (ATS) predictor for college football games. There are two sources of data:
- Game-by-game stats are from the [SportsReference API](https://sportsreference.readthedocs.io/en/stable/)
- Historical betting lines and odds are from 
[sportsbookreviewsonline.com](https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaafootball/ncaafootballoddsarchives.htm)

There are currently five code files in the repository:
- ***ats_picks.py***: Generates picks and bets for upcoming games.
- ***ats_predictor.py***: Looks for the best model and betting strategy by running simulations on past games.
- ***cleaner.py***: Cleans the historical odds spreadsheet into another spreadsheet that is easier to work with.
- ***create_input_dfs.py***: Takes the data from the two sources to create input stats for each game.
- ***fix_names.py***: Contains a dictionary which is used to convert names in *cleaner.py*.

## Findings

I think that, at the moment, the model doesn't really show any significant ability to predict against-the-spread. Thus, I predict that as
the number of games goes to infinity, the model will approach 50% ATS. This obviously does not really help.

I think that the scores are predicted decently well, but as far as making money is concerned I'm not there yet. Luckily,
[collegefootballdata.com](http://collegefootballdata.com) also has an API that has drive and play-by-play data (along with everything else I could want), so that's where
I'll start when I resume this project.

There's also the fact that making money is a lot harder than it could be because traditional sportsbooks take such a big cut. So, I think it doesn't make as much sense to resume 
the project until decentralized betting markets are a bit further along. Projects like [Augur](https://augur.net/) are what would make it really cool to start building with this 
project again. The fees will be a lot lower and so it will be a lot easier to be profitable, there will be no limits (if I would ever get that far, haha), and the best part is 
that I could integrate my work with with their APIs to automate getting lines, making bets, etc.

## Where to Go Next

- Adjust game stats for opponent
- I actually want to make picks using the opening spread, not the closing one
- A moneyline betting strategy
