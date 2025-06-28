import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import namedtuple


def advanced_stats_table(year):
    # scrapes NBA advanced stats for a given season from basketball-reference.com
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html'
    response= requests.get(url)

    if response.status_code != 200:
        raise ValueError (f'Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')


    table1 = tables[0]
    tbody = table1.find('tbody')


    raw_data_advanced = tbody.text
    entries = []
    # parsing string, player stats seperated by 3 spaces
    players = raw_data_advanced.strip().split('   ')

    # top 450 players by minutes played as NBA should only have 450 at one time (15 players * 30 teams)
    for i in range (450):
        # for each player, I split all their info up into another list. This lets my select the advanced stats I want to use in the weighted equation.
        player = players[i].split()
        try:
            float(player[-1])
        except IndexError:
            pass
        except ValueError:
            player.pop()

        # handle players with 3+ word names (e.g., "Jaren Jackson Jr."), normal player with 2 worded names have info len of 28
        if len(player) < 29:
            pass
        else:
            if len(player) > 29:
                more_by = len(player) - 29
                for j in range (more_by):
                    player[2] = str(player[2] + " " + player[3])
                    del player[3]
            # filter by minimum playing time (24 MPG * 65 games = 1560). Unlikely for MVP candidate to play less than 24MPG, historical average is 36MPG. Need 65 games to be considered for awards
            if int(player[8]) > 1560:
                entries.append(player)


    Player_advanced = namedtuple('Player_advanced', ['name', 'age','team','minutes_played', 'PER', 'TS', 'WS','BPM'])
    advanced_data_filtered = []
    added_names = set()
    for entry in entries:
        player_advanced = Player_advanced(str(entry[1] + ' '+ entry[2]), int(entry[3]), entry[4], int(entry[8]), float(entry[9]), float(entry[10]), float(entry[-6]), float(entry[-2]))
        # to prevent duplicates in the final dataframe
        if player_advanced.name not in added_names:
            added_names.add(player_advanced.name)
            advanced_data_filtered.append(player_advanced)


    advanced_df = pd.DataFrame(advanced_data_filtered)
    return advanced_df

#what_year = int(input("Which season's advanced stats would you like?: "))
#try:
    #advanced_df = advanced_stats_table(what_year)
    #print(advanced_df.to_string())
#except ValueError as e:
    #print(f'Error: {e}')