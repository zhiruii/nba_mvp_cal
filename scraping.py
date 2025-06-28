
import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import namedtuple


def advanced_stats_table(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html'
    response= requests.get(url)

    if response.status_code != 200:
        raise ValueError (f'Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')

    if not tables:
        raise ValueError(f"No data available for NBA season {year} (no tables found on page).")

    table1 = tables[0]
    tbody = table1.find('tbody')

    if not tbody or not tbody.find_all('tr'):
        raise ValueError(f"No advanced stats data available for NBA season {year}.")

    raw_data_advanced = tbody.text
    entries = []

    players = raw_data_advanced.strip().split('   ')


    for i in range (450):
        player = players[i].split()
        try:
            float(player[-1])
        except ValueError:
            player.pop()


        if len(player) < 29:
            pass
        else:
            if len(player) > 29:
                more_by = len(player) - 29
                for j in range (more_by):
                    player[2] = str(player[2] + " " + player[3])
                    del player[3]
            if int(player[8]) > 1560:
                entries.append(player)


    Player_advanced = namedtuple('Player_advanced', ['name', 'age','team','minutes_played', 'PER', 'TS', 'WS','BPM'])
    advanced_data_filtered = []
    added_names = set()
    for entry in entries:
        player_advanced = Player_advanced(str(entry[1] + ' '+ entry[2]), int(entry[3]), entry[4], int(entry[8]), float(entry[9]), float(entry[10]), float(entry[-6]), float(entry[-2]))

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