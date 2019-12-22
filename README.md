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

I think that the scores are predicted decently well, but as far as making money is concerned I'm not there yet. I think that this is the
ceiling for the stats that I have. If I could get more in-depth data (i.e. 5 factors, play-by-play data), then perhaps the model's accuracy
could be improved, but until then I can't really make any money using this model.

## What's Next

- A web scraper for current betting lines.
- A moneyline betting strategy.
