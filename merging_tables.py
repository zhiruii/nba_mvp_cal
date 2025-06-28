from scrapping_reg import reg_stats_table
from scraping import advanced_stats_table
from historical_MVP_race import historical_MVP_race_table
import pandas as pd


def pre_score_table(year):
    try:
        advanced_table = advanced_stats_table(year)
        reg_table = reg_stats_table(year)
    except ValueError as e:
        raise ValueError (f'Error while scrapping data for season {year}: {e}')
    #merging the advanced_stats and reg_stats table so that we can use all the stats in the weighted equation to calculated MVP score
    #we are only merging players with the same name, age, and team in the same season. This is to prevent merging wrong stats in the event
    #that players share the same name. The likelihood of players sharing the same name, age, and team in the same season is very very low.
    #players are dropped if they appear on one table, but not the other. This is because reg_stats manually calculated total minutes played, resulting
    #in fringe cases where they may have met the 1560 mark in the advanced_table, but not for the reg_table as we used averaged MPG. These players that
    #barely made the mark are insigifcant to our mvp candidates shortlist.
    
    merged_df = pd.merge(advanced_table, reg_table, on=['name', 'age', 'team'], how= "inner")
    return merged_df



def weightage():
    default_weights = {
        'PER_norm': 0.10,
        'TS_norm': 0.07,
        'WS_norm': 0.25,
        'BPM_norm': 0.2,
        'PPG_norm': 0.18,
        'AST_norm': 0.07,
        'TRB_norm': 0.05,
        'BLK_norm': 0.04,
        'STL_norm': 0.04
    }

    choice = input("Would you like to set your own weightage for the equation? (Y/N): ").strip().upper()

    if choice == "Y":
        weights = {}
        for stat_norm in default_weights.items():
            while True:
                try:
                    value = float(input(f"Enter weight for {stat_norm} (0 to 1): "))
                    if 0 <= value <= 1:
                        weights[stat_norm] = value
                        break
                    else:
                        print("Please enter a number between 0 and 1.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        return weights

    elif choice == "N":
        return default_weights
    else:
        raise ValueError("Invalid input. Please enter Y or N.")



def full_table(df, weights):
    stats = ['PER', 'TS', 'WS', 'BPM', 'PPG', 'AST', 'TRB', 'BLK', 'STL']
    for stat in stats:
        #make a new column for every stat, but normalised. min-max normalisation is used
        df[f'{stat}_norm'] = (df[stat] - df[stat].min()) / (df[stat].max() - df[stat].min())

    #to calculated MVP score, we used (nomalised stat x * weightage for that stat). We do that for every stat of a player and add them together
    df['MVP_score'] = sum(df[stat_norm] * weight for stat_norm, weight in weights.items())
    df = df.sort_values('MVP_score', ascending= False)

    cols = list(df.columns)
    mins_played_col_index, mvp_score_col_index = cols.index('minutes_played'), cols.index('MVP_score')
    cols[mvp_score_col_index], cols[min_played_index] = cols[mins_played_index], cols[mvp_score_col_index]
    df = df[cols]

    return df.head(10)
