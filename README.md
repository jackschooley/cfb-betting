# cfb-betting: College Football Betting

## About

This repository contains an against-the-spread (ATS) predictor for college football games. There are two sources of data:
- Game-by-game stats are from the [Sportsreference API](https://sportsreference.readthedocs.io/en/stable/)
- Historical betting lines and odds are from 
[sportsbookreviewsonline.com](https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaafootball/ncaafootballoddsarchives.htm)

There are currently five files in the repository:
- ***ats_picks.py***: Generates picks and bets for upcoming games.
- ***ats_predictor.py***: Looks for the best model and betting strategy by running simulations on past games.
- ***cleaner.py***: Cleans the historical odds spreadsheet into another spreadsheet that is easier to work with.
- ***create_input_dfs.py***: Takes the data from the two sources to create input stats for each game.
- ***fix_names.py***: Contains a dictionary which is used to convert names in *cleaner.py*.

## Findings

I think that, at the moment, the model doesn't really show any significant ability to predict against-the-spread. Thus, I predict that as
the number of games goes to infinity, the model will approach 50% ATS. This obviously does not really help.

I think that the scores are predicted decently well, but as far as making money is concerned I'm not there yet. 

## Where to Go Next

- Probably need better data, at the drive and play-by-play level (in line with the five factors)
- Adjust game stats for opponent
- I actually want to make picks using the opening spread, not the closing one
- A web scraper for current betting lines
- A moneyline betting strategy
