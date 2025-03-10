import argparse
from selenium import webdriver
import time

parser = argparse.ArgumentParser(description='Whoscored crawling by jaeminiman')

parser.add_argument('--type', required=True, help='type of crawling data -- seasonal team data: 1, seasonal player data: 2, match result data: 3')
parser.add_argument('--path', required=False, default='.', help='directory for saving data')
parser.add_argument('--league', required=True, help='One of for leagues (PL, LIGA, SA, BL)')
parser.add_argument('--season', required=True, help='a number of season')
parser.add_argument('--filename', required=True, help='a name of saved data file')
#parser.add_argument('--team', required=False, default=0, help='a number of team')

args = parser.parse_args()

region_lis = {'PL' : 252,
    'LIGA': 206,
    'SA': 108,
    'BL': 81}

tournament_lis = {
    'PL' : 2,
    'LIGA' : 4,
    'SA' : 5,
    'BL' : 3
}

print(args.league)
print(region_lis['PL'])
print(region_lis[args.league])

# assign argument
region_number = region_lis[args.league]
tournaments_number = tournament_lis[args.league]
season_number = args.season
path = str(args.path) + '/webdriver' 

# test webdriver
def test_webdriver(region_number, tournaments_number, season_number, path):
    url = 'https://www.whoscored.com/Regions/'+str(region_number)+'/Tournaments/'
    url = url+str(tournaments_number)+'/Seasons/'+str(season_number)+'/Fixtures'
    try :
        driver = webdriver.Chrome(str(path))
        driver.get(url)
        time.sleep(1)
        driver.close() 
    except :
        raise KeyError('webdriver is not working!')
    return 0

test_webdriver(region_number, tournaments_number, season_number, path)

# crawling seasonal data





    


