import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import namedtuple

def reg_stats_table(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
    response= requests.get(url)

    if response.status_code != 200:
        raise ValueError (f"Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')

    if not tables:
        raise ValueError(f"No data available for NBA season {year} (no tables found on page).")

    table1 = tables[0]
    tbody = table1.find('tbody')

    if not tbody or not tbody.find('tr'):
        raise ValueError(f"No per game stats data available for NBA season {year}.")


    raw_data_reg = tbody.text

    entries_reg = []
    games_played = 0
    minutes_pg = 0
    players_reg = raw_data_reg.strip().split('   ')

    for i in players_reg:
        player_reg = i.split()

        try:
            float(player_reg[-1])
        except IndexError:
            pass
        except ValueError:
            player_reg.pop()

        if len(player_reg) < 31:
            pass
        else:
            if len(player_reg) > 31:
                more_by = len(player_reg) - 31
                for j in range(more_by):
                    player_reg[2] = str(player_reg[2] + " " + player_reg[3])
                    del player_reg[3]

            try:
                games_played = float(player_reg[6])
                minutes_pg = float(player_reg[8])
            except ValueError:
                pass

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

#what_year = int(input("Which season's reg stats would you like?: "))
#try:
    #reg_df = reg_stats_table(what_year)
    #print(reg_df.to_string())
#except ValueError as e:
    #print(f'Error: {e}')