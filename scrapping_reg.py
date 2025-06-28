import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import namedtuple

#scrapes NBA per-game stats for a given season from basketball-reference.com
def reg_stats_table(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
    response= requests.get(url)

    if response.status_code != 200:
        raise ValueError (f"Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    #extract target table and its body
    table1 = tables[0]
    tbody = table1.find('tbody')

    raw_data_reg = tbody.text

    entries_reg = []
    games_played = 0
    minutes_pg = 0
    
    #player stats separated by 3 spaces
    players_reg = raw_data_reg.strip().split('   ')

    for player in players_reg:
        player_reg = player.split()

        #removal of trailing MVP/ All-star tags, just like in the scraping of advanced stats
        try:
            float(player_reg[-1])
        except IndexError:
            pass
        except ValueError:
            player_reg.pop()
        
        #handle players with 3+ word names (e.g., "Kelly Oubre Jr."). Players with typcial 2-worded names have info len of 30
        if len(player_reg) < 31:
            pass
        else:
            if len(player_reg) > 31:
                more_by = len(player_reg) - 31
                #in case player has 4, 5 worded-names
                for j in range(more_by):
                    player_reg[2] = str(player_reg[2] + " " + player_reg[3])
                    del player_reg[3]
            #unlike in advanced stats, total minutes played must be manually calculated. This is done after removing award tags and name incosistancy
            #so that the indexing stays consistant
            try:
                games_played = float(player_reg[6])
                minutes_pg = float(player_reg[8])
            except ValueError:
                pass
            #filter by playing time (24MPG * 65 games = 1560)
            if int(games_played * minutes_pg) > 1560:
                entries_reg.append(player_reg)

    Player_reg = namedtuple('Player_reg', ['name', 'age','team','PPG', 'AST', 'TRB', 'BLK','STL'])
    reg_data_filtered = []
    added_names = set()
    for entry in entries_reg:
        player_reg = Player_reg(str(entry[1] + ' '+ entry[2]), int(entry[3]), entry[4], float(entry[-1]), float(entry[-6]), float(entry[-7]), float(entry[-4]), float(entry[-5]))

        if player_reg.name not in added_names:
            added_names.add(player_reg.name)
            reg_data_filtered.append(player_reg)

    reg_df = pd.DataFrame(reg_data_filtered)
    return reg_df
