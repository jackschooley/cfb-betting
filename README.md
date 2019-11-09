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

## How to Use

The ATS predictor should have upwards of 60% accuracy when used on conference games starting in week 4 of the college football season. The
model will generate picks and bets for nonconference games, as well as games before week 4, but there are some caveats to those games that
make the model less reliable.

### What does the model not account for?

- Strength of schedule: strength of schedule is not explicitly accounted for; however, teams from the same conference will have very
similar strengths of schedule. Thus, this is likely a non-issue for conference games, but it does cast doubt on the model's accuracy on
predicting nonconference games.
- Games with large spreads (in either direction): the model is not good at predicting against large spreads, so don't trust it to bet on
these games.
- Injuries: obviously if a team loses their star QB (or RB, WR, etc.) for a game, the model's accuracy for predicting that game is heavily
in doubt.

## What's Next

- An over/under predictor.
- A moneyline betting strategy.
