
import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import namedtuple

#we are scraping advanced stats of players from a specific season
def advanced_stats_table(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html'
    response= requests.get(url)

    #error handeling for HTTP status code
    if response.status_code != 200:
        raise ValueError (f'Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    #finding all table tags
    tables = soup.find_all('table')

    #error handeling if there is no table
    if not tables:
        raise ValueError(f"No data available for NBA season {year} (no tables found on page).")
   
    #the table we need is the first table in the html
    table1 = tables[0]
    tbody = table1.find('tbody')

    #error handeling if table is empty, no tbody
    if not tbody or not tbody.find_all('tr'):
        raise ValueError(f"No advanced stats data available for NBA season {year}.")

    #I was new to html scraping, so I converted everything to a Python string, which I then parsed.lol
    raw_data_advanced = tbody.text
    entries = []

    #here, i realised that after converting everything to a string, each player's info were seperated by 3 spaces, so i used split to get a large list
    #where each element was the full player's info, like their names, age, team, position, and every advanced stats
    players = raw_data_advanced.strip().split('   ')

    #by default, Basketball reference has the players arranged in descending order based on minutes played. Since there should be 450 players in the
    #NBA (15 players for 30 teams), I only took the first 450 players in the 'players' list. In reality, there should be more players, but they are
    #insignificant to the MVP ranking due to their roles on the team (inferred through playing time).
    for i in range (450):
        #for each player, I split all their info up into another list. This lets my select the advanced stats I want to use in the weighted equation.
        player = players[i].split()
        try:
            #Basketball refernce display the awards/ recognition a player gets at the end of each player's info, like MVP votings, 
            #All-star appeareance, etc. I wanted to remove this irrelevent info
            float(player[-1])
        except ValueError:
            player.pop()

        #this was something I did because I was new to data scraping as well. I realised that some players had 3-worded names. such as names that ended
        #with 'jr', or 'III'. This messed with my extraction of specific info I wanted from each player, as the indexing will be off. I realised that
        #the default 2-word-named players had a list of info that had a len of 28. So those players were not adjusted. For players with info list that
        #had len > 29, their last names were joined together.
        if len(player) < 29:
            pass
        else:
            if len(player) > 29:
                more_by = len(player) - 29
                #just in case there were players with 4, 5 worded names, I merged eveything with the second word in their name
                
                for j in range (more_by):
                    player[2] = str(player[2] + " " + player[3])
                    del player[3]
            #at index 8, it showed the player's playing time. I filtered out the players that had a total playing time <= 1560 minutes for the season
            #, as statistically, it is almost impossible for a player to be a MVP candidate with playing time <=1560. One must play at least 65 games
            #to be considered for awards, and I set the bench mark to be 24 minutes played for 65 games. A full NBA game is 48 minutes, and on avaerage,
            #a MVP plays 36+ minutes. This is a conservative filter.
            if int(player[8]) > 1560:
                entries.append(player)


    Player_advanced = namedtuple('Player_advanced', ['name', 'age','team','minutes_played', 'PER', 'TS', 'WS','BPM'])
    advanced_data_filtered = []
    added_names = set()
    for entry in entries:
        player_advanced = Player_advanced(str(entry[1] + ' '+ entry[2]), int(entry[3]), entry[4], int(entry[8]), float(entry[9]), float(entry[10]), float(entry[-6]), float(entry[-2]))
        
        #to prevent duplicates in the final dataframe
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
