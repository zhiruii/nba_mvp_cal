import pandas as pd
from bs4 import BeautifulSoup
import requests
def historical_MVP_race_table(year):

    url = f'https://www.basketball-reference.com/awards/awards_{year}.html#mvp'
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve data for year {year}. HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    mvp_table = soup.find('table', {'id': 'mvp'})

    if not mvp_table:
        raise ValueError(f"No MVP table found for NBA season {year}.")

    rows = mvp_table.find('tbody').find_all('tr')

    data = []
    for row in rows:
        if row.get('class') == ['thead']:
            continue
        rank = row.find('th').text.strip()
        player = row.find('td', {'data-stat': 'player'}).text.strip()
        data.append({'Rank': rank, 'Player': player})

    df = pd.DataFrame(data)
    return df.head(6)

#what_year = int(input('What year: '))
#try:
   #historical_race_df = historical_MVP_race(what_year)
    #print(historical_race_df.to_string())
#except ValueError as e:
    #print(f'Error: {e}')