#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pandas as pd
import time
import pickle
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import sys
from tqdm import tqdm

def crawling_match_url(region_number, tournaments_number, season_number, api_delay_term=5):
    """
    find the all links of matches from a certain league
    
    Args :
        region_number : region number of the league from whoscored
        tournaments_number : tournament number of the league from whoscored
        season_number : season number of the league from whoscored
        api_delay_term : break time
    
    Returns : 
        list of all the match index(link)  

    """ 
    
    # activate webdriver
    url = 'https://www.whoscored.com/Regions/'+str(region_number)+'/Tournaments/'
    url = url+str(tournaments_number)+'/Seasons/'+str(season_number)+'/Fixtures'
    driver = webdriver.Chrome()
    driver.get(url)

    # wait get league team datas
    match_link= []
    with tqdm(total=40, file=sys.stdout) as pbar :
        for i in range(40):
            time.sleep(api_delay_term)
            elements = driver.find_elements(By.CSS_SELECTOR, 'a.result-1.rc')
            for element in elements:
                match_link.append(element.get_attribute('href'))

            # click
            try : 
                a = driver.find_element(By.CSS_SELECTOR, 'a.previous.button.ui-state-default.rc-l.is-default')
                a.click()
            except : 
                break

            time.sleep(2)
            pbar.update(1)
            pbar.set_description('page {}'.format(i+1))
    
    driver.close()
    return list(set(match_link))

def crawling_game_results(url, api_delay_term=2):
    """
    crawling results from a match
    
    
    Args :
        url : match url
        api_delay_term : break time
    
    Returns : 
        dictionary of match results

    """ 
    # activate webdriver
    driver = webdriver.Chrome()
    
    # wait get league team datas
    time.sleep(api_delay_term) 
    
    url_preview = url.replace('Live','Preview')
    url_show = url.replace('Live','Show')
    url_matchreport = url.replace('Live','MatchReport')
    
    driver.get(url)
    match_log = driver.find_element(By.CSS_SELECTOR, 'div.match-centre-stats').find_elements(By.CSS_SELECTOR, 'span.match-centre-stat-value')
    home_shot = match_log[2].get_attribute("textContent").split("\t")[0]
    away_shot = match_log[3].get_attribute("textContent").split("\t")[0]
    home_possession  = match_log[4].get_attribute("textContent").split("\t")[0]
    away_possession = match_log[5].get_attribute("textContent").split("\t")[0]
    home_pass_success = match_log[6].get_attribute("textContent").split("\t")[0]
    away_pass_success = match_log[7].get_attribute("textContent").split("\t")[0]
    home_dribbles = match_log[8].get_attribute("textContent").split("\t")[0]
    away_dribbles = match_log[9].get_attribute("textContent").split("\t")[0]
    home_aerials_won = match_log[10].get_attribute("textContent").split("\t")[0]
    away_aerials_won = match_log[11].get_attribute("textContent").split("\t")[0]
    home_tackles = match_log[12].get_attribute("textContent").split("\t")[0]
    away_tackles = match_log[13].get_attribute("textContent").split("\t")[0]
    home_corners = match_log[14].get_attribute("textContent").split("\t")[0]
    away_corners = match_log[15].get_attribute("textContent").split("\t")[0]
    home_dispossessed = match_log[16].get_attribute("textContent").split("\t")[0]
    away_dispossessed = match_log[17].get_attribute("textContent").split("\t")[0]
    
    driver.get(url_preview)
    time.sleep(api_delay_term)
    # get home and away
    missing_players_home = driver.find_element(By.CSS_SELECTOR, 'div.col12-lg-6.col12-m-6.col12-s-6.col12-xs-12.home.small-display-on')
    ratings = missing_players_home.find_elements(By.CSS_SELECTOR, 'td.rating')
    home_missing_player = len(ratings)
    home_missing_player_rating = []
    for rating in ratings:
        try : home_missing_player_rating.append(float(rating.get_attribute("textContent").split("\t")[0]))
        except : continue
    home_missing_player_rating = round(np.mean(np.array(home_missing_player_rating)),2)
    

    missing_players_away = driver.find_element(By.CSS_SELECTOR, 'div.col12-lg-6.col12-m-6.col12-s-6.col12-xs-12.away.small-display-off')
    ratings = missing_players_away.find_elements(By.CSS_SELECTOR, 'td.rating')
    away_missing_player = len(ratings)
    away_missing_player_rating = []
    for rating in ratings:
        try : away_missing_player_rating.append(float(rating.get_attribute("textContent").split("\t")[0]))
        except : continue
    away_missing_player_rating = round(np.mean(np.array(away_missing_player_rating)),2)
    
    home = driver.find_element(By.CSS_SELECTOR, 'span.col12-lg-4.col12-m-4.col12-s-0.col12-xs-0.home.team').get_attribute("textContent").split("\t")[0]
    away = driver.find_element(By.CSS_SELECTOR, 'span.col12-lg-4.col12-m-4.col12-s-0.col12-xs-0.away.team').get_attribute("textContent").split("\t")[0]
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.info-block.cleared')
    score = elements[1]
    half_home_score = score.find_elements(By.CSS_SELECTOR, 'dd')[0].get_attribute("textContent").split("\t")[0].split(':')[0]
    half_away_score = score.find_elements(By.CSS_SELECTOR, 'dd')[0].get_attribute("textContent").split("\t")[0].split(':')[1]
    full_home_score = score.find_elements(By.CSS_SELECTOR, 'dd')[1].get_attribute("textContent").split("\t")[0].split(':')[0]
    full_away_score = score.find_elements(By.CSS_SELECTOR, 'dd')[1].get_attribute("textContent").split("\t")[0].split(':')[1]
    
    kick_off = elements[2].find_elements(By.CSS_SELECTOR, 'dd')[0].get_attribute("textContent").split("\t")[0]
    date = elements[2].find_elements(By.CSS_SELECTOR, 'dd')[1].get_attribute("textContent").split("\t")[0]
    
    ########### show data
    driver.get(url_show)
    # wait get league team datas
    time.sleep(api_delay_term) 
    
    # get home and away
    matchup_home_goals = driver.find_elements(By.CSS_SELECTOR, 'td.previous-meetings-stat')[0].get_attribute("textContent").split("\t")[0]
    matchup_away_goals = driver.find_elements(By.CSS_SELECTOR, 'td.previous-meetings-stat')[3].get_attribute("textContent").split("\t")[0]
    matchup_home_wins = driver.find_elements(By.CSS_SELECTOR, 'span.title')[0].get_attribute("textContent").split("\t")[0] 
    matchup_draw = driver.find_elements(By.CSS_SELECTOR, 'span.title')[1].get_attribute("textContent").split("\t")[0] 
    matchup_away_wins = driver.find_elements(By.CSS_SELECTOR, 'span.title')[2].get_attribute("textContent").split("\t")[0] 
    
    ########### show data
    driver.get(url_matchreport)
    # wait get league team datas
    time.sleep(api_delay_term) 
    attempt = driver.find_element(By.CSS_SELECTOR, 'div.stat-group').find_elements(By.CSS_SELECTOR, 'span.stat-value')
    home_total_att = attempt[0].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_total_att = attempt[1].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_open_att = attempt[2].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_open_att = attempt[3].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_set_att = attempt[4].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_set_att = attempt[5].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_counter_att = attempt[6].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_counter_att = attempt[7].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_pk_att = attempt[8].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_pk_att = attempt[9].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_own_att = attempt[10].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0] 
    away_own_att = attempt[11].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0] 
    
    passes = driver.find_element(By.CSS_SELECTOR, '#live-chart-stats-options')
    passes.find_elements(By.CSS_SELECTOR, 'a')[1].click()
    
    time.sleep(2)
    passes = driver.find_elements(By.CSS_SELECTOR, 'div.stat-group')[2].find_elements(By.CSS_SELECTOR, 'span.stat-value')
    home_total_passes = passes[0].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_total_passes = passes[1].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_crosses_passes = passes[2].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_crosses_passes = passes[3].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_long_balls = passes[6].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_long_balls = passes[7].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    home_short_passes = passes[8].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    away_short_passes = passes[9].find_elements(By.CSS_SELECTOR, 'span')[0].get_attribute("textContent").split("\t")[0]
    
    
    driver.close()
    
    
    # close webdriver
    game_dict = {
        'home_shot' : home_shot,
        'away_shot' : away_shot,
        'home_possession' : home_possession,
        'away_possession' : away_possession, 
        'home_pass_success' : home_pass_success, 
        'away_pass_success' : away_pass_success,
        'home_dribbles' : home_dribbles,
        'away_dribbles' : away_dribbles,
        'home_aerials_won' : home_aerials_won,
        'away_aerials_won' : away_aerials_won,
        'home_tackles' : home_tackles,
        'away_tackles' : away_tackles,
        'home_corners' : home_corners,
        'away_corners' : away_corners,
        'home_dispossessed' : home_dispossessed,
        'away_dispossessed' : away_dispossessed,
        'home_missing_player' : home_missing_player,
        'away_missing_player' : away_missing_player,
        "home_missing_player_rating": home_missing_player_rating, 
        "away_missing_player_rating": away_missing_player_rating, 
        "home": home,
        "away": away,
        'half_home_score': half_home_score,
        'half_away_score': half_away_score,
        'full_home_score': full_home_score,
        'full_away_score': full_away_score,
        'kick_off': kick_off,
        'date' : date,
        'matchup_home_goals' : matchup_home_goals,
        'matchup_away_goals' : matchup_away_goals,
        'matchup_home_wins' : matchup_home_wins,
        'matchup_draw': matchup_draw,
        'matchup_away_wins': matchup_away_wins,
        'home_total_att' : home_total_att,
        'away_total_att' : away_total_att,
        'home_open_att' : home_open_att,
        'away_open_att' : away_open_att,
        'home_set_att' : home_set_att,
        'away_set_att' : away_set_att,
        'home_counter_att' : home_counter_att,
        'away_counter_att' : away_counter_att,
        'home_pk_att' : home_pk_att,
        'away_pk_att' : away_pk_att,
        'home_own_att' : home_own_att,
        'away_own_att' : away_own_att,
        'home_total_passes' : home_total_passes,
        'away_total_passes' : away_total_passes,
        'home_crosses_passes' : home_crosses_passes,
        'away_crosses_passes' : away_crosses_passes,
        'home_long_balls' : home_long_balls,
        'away_long_balls' : away_long_balls,
        'home_short_passes' : home_short_passes,
        'away_short_passes' : away_short_passes
        }
    
    return game_dict

def match_df():
    """
    empty dataframe about features of match results.
    """
    match_df = pd.DataFrame(columns=[
        'home_shot',
        'away_shot',
        'home_possession',
        'away_possession', 
        'home_pass_success', 
        'away_pass_success',
        'home_dribbles',
        'away_dribbles',
        'home_aerials_won',
        'away_aerials_won',
        'home_tackles' ,
        'away_tackles',
        'home_corners' ,
        'away_corners' ,
        'home_dispossessed',
        'away_dispossessed',
        'home_missing_player',
        'away_missing_player',
        "home_missing_player_rating", 
        "away_missing_player_rating", 
        "home",
        "away",
        'half_home_score',
        'half_away_score',
        'full_home_score',
        'full_away_score',
        'kick_off',
        'date',
        'matchup_home_goals',
        'matchup_away_goals',
        'matchup_home_wins',
        'matchup_draw',
        'matchup_away_wins',
        'home_total_att',
        'away_total_att',
        'home_open_att',
        'away_open_att',
        'home_set_att',
        'away_set_att',
        'home_counter_att',
        'away_counter_att',
        'home_pk_att',
        'away_pk_att',
        'home_own_att',
        'away_own_att',
        'home_total_passes',
        'away_total_passes',
        'home_crosses_passes',
        'away_crosses_passes',
        'home_long_balls',
        'away_long_balls',
        'home_short_passes',
        'away_short_passes'])
    return match_df

def test():
    return(os.listdir(os.getcwd()))

def crawling_seasons(region, tournament, season_number, season_name):
    """
    crawling detail match results of all matches from a season.
    save 
        1. match URL file (.csv)
            URL of each match
            
        2. match results file (.csv)
            detail results of all matches from a season.
    
    Args :
        region : region number of the league from whoscored
        tournaments : tournament number of the league from whoscored
        season_number : season number of the league from whoscored
        season_name : season name for saving file ex) PL1920 or Serie A 1718 
     
    Retrun : 
        list of matches that are failed to crwaling 
       
    """
    
    file_name = season_name+'_match_url.csv'
    file_names = test()
    if file_name in file_names:
        match_url = pd.read_csv(file_name)['0']
        print('find '+ file_name + 'done')
    else : 
        match_url = crawling_match_url(region,tournament,season_number)
        pd.DataFrame(match_url).to_csv(file_name)
        print(file_name+": done, {} matches".format(len(match_url)))
    
    a = 0
    error_list = []
    mat_df = match_df()
    for match in match_url[len(mat_df):]:
        start_time = time.time()
    
        try :
            temp_dict = crawling_game_results(match,4)
            mat_df.loc[len(mat_df)] = temp_dict
            print('match_url {} : cawling done'.format(len(mat_df)+a))
        except :
            error_list.append(len(mat_df)+a)
            print('match_url {} : error'.format(len(mat_df)+a))
            a += 1
            continue
        if len(mat_df)%10 ==0:
            mat_df.to_csv(season_name+'_match.csv')
            time.sleep(4) 
        # print(time.time()-start_time)
    mat_df.to_csv(season_name+'_match.csv')
    print(error_list)
    return(error_list)   

def crawling_seasons_add(season_name, missing_list):
    """   
        add recrawling match results from missing list to previous dataframe.
        
        
    Args :
        season_name : season name for saving file ex) PL1920 or Serie A 1718 
        missing_list : list of match index which is failed to crwaling
     
    Retrun : 
        list of match failed to crwaling 
       
    """
    file_name = season_name+'_match_url.csv'
    file_names = os.listdir(os.getcwd())
    if file_name in file_names:
        match_number = pd.read_csv(file_name)['0']
        print('find '+ file_name + 'done')
    else : 
        print('there are no match_url.csv file')
        return()
    
    a = 0
    error_list = []
    mat_df = match_df()
    for missing_match_no in missing_list:
        start_time = time.time()
        match = match_number.iloc[missing_match_no]
    
        try :
            temp_dict = crawling_game_results(match, 4)
            mat_df.loc[len(mat_df)] = temp_dict
            print('match_number {} : cawling done'.format(missing_match_no))
        except :
            
            print('match_number {} : error'.format(missing_match_no))
            
            try :             
                temp_dict = crawling_game_results(match, 4)
                mat_df.loc[len(mat_df)] = temp_dict
                print('match_number {} : crawling done (retry)'.format(missing_match_no))
                
            except :
                print('match_number {} : final error'.format(missing_match_no))
                error_list.append(missing_match_no)
            
        if len(mat_df)%10 ==0:
            mat_df.to_csv(season_name+'_add_match.csv')
            time.sleep(4) 
    mat_df.to_csv(season_name+'_add_match.csv')
    print(error_list)    
    return(error_list)   

def crawling_all_matches(region, tournament, season_number, season_name):
    """
    combine all functions and save all match results from certain seasons
    
    Args :
        region : region number of the league from whoscored
        tournaments : tournament number of the league from whoscored
        season_number : season number of the league from whoscored
        season_name : season name for saving file ex) PL1920 or Serie A 1718 
    
    Returns : 
        error list  
    
    """
    error_lis = crawling_seasons(region, tournament, season_number, season_name)
    result = crawling_seasons_add(season_name, error_lis)
    return(result)



def league_table_added(URL, api_delay_term=2):
    """
    crawling league table with additional features
    ex) shot per game, Tackles per game ... etc.
    
    Args : 
        URL : league table URL
        
    Output : 
        league table (data.frame)
    
    """
    url = str(URL)
    driver = webdriver.Chrome()
    driver.get(url)
    
    time.sleep(api_delay_term)
    
    league_table_df = pd.DataFrame(columns=[
        "team_name", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"])
    elements = driver.find_elements(By.CLASS_NAME, 'standings')[0].find_elements(By.CSS_SELECTOR, "tr")
    
    for element in elements:
        league_table_dict = { 
            "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].get_attribute("textContent").split("\t")[0],     
            "P": element.find_elements(By.CSS_SELECTOR, "td")[1].get_attribute("textContent").split("\t")[0],
            "W": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0], 
            "D": element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0],
            "L": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0], 
            "GF": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
            "GA": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0],
            "GD": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
            "Pts": element.find_elements(By.CSS_SELECTOR, "td")[8].get_attribute("textContent").split("\t")[0],
        }
        league_table_df.loc[len(league_table_df)] = league_table_dict
    
    time.sleep(api_delay_term)
    
    starter = driver.find_elements(By.ID, "sub-navigation")
    starter = starter[0].find_elements(By.CSS_SELECTOR, "li")[2]
    starter.click()
    
    
    team_stat_df1 = pd.DataFrame(columns=[
        "team_name", "Goals", "Shots pg", "Yellow", "Red", "Poss%", "Pass%", 
        "A_Won", "Rating"
    ])
    elements = driver.find_elements(By.ID, "top-team-stats-summary-content")
    elements = elements[0].find_elements(By.CSS_SELECTOR, "tr")
    
    for element in elements:
        team_table_dict1 = { 
            "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].get_attribute("textContent").split("\t")[0].split('. ')[1],     
            "Goals": element.find_elements(By.CSS_SELECTOR, "td")[1].get_attribute("textContent").split("\t")[0],
            "Shots pg": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0], 
            "Yellow": element.find_elements(By.CSS_SELECTOR, "td")[3].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0], 
            "Red": element.find_elements(By.CSS_SELECTOR, "td")[3].find_elements(By.CSS_SELECTOR, "span")[1].get_attribute("textContent").split("\t")[0], 
            "Poss%": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0], 
            "Pass%": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0],
            "A_Won": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0],
            "Rating": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
        }
        team_stat_df1.loc[len(team_stat_df1)] = team_table_dict1
    
    element = driver.find_element(By.CSS_SELECTOR, "a[href='#stage-team-stats-defensive']")
    element.click()
    
    time.sleep(api_delay_term)
    
    
    team_stat_df2 = pd.DataFrame(columns=[
        "team_name", "Shoted pg", "Tackles pg", "Intercept pg", "Fouls pg", "Offsides pg"
    ])
    elements = driver.find_elements(By.ID, "statistics-team-table-defensive")
    elements = elements[0].find_elements(By.ID, "top-team-stats-summary-content")
    elements = elements[0].find_elements(By.CSS_SELECTOR, "tr")
    
    for element in elements:
        team_table_dict2 = { 
            "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].get_attribute("textContent").split("\t")[0].split('. ')[1],     
            'Shoted pg': element.find_elements(By.CSS_SELECTOR, "td")[1].get_attribute("textContent").split("\t")[0],
            'Tackles pg': element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
            'Intercept pg': element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
            'Fouls pg': element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0], 
            'Offsides pg': element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
        }
        team_stat_df2.loc[len(team_stat_df2)] = team_table_dict2
    
    element = driver.find_element(By.CSS_SELECTOR, "a[href='#stage-team-stats-offensive']")
    element.click()
    
    time.sleep(api_delay_term)
    
    team_stat_df3 = pd.DataFrame(columns=[
        "team_name", "Shots OT pg", "Dribbles pg", "Fouled pg"
    ])
    elements = driver.find_elements(By.ID, "statistics-team-table-offensive")
    elements = elements[0].find_elements(By.ID, "top-team-stats-summary-content")
    elements = elements[0].find_elements(By.CSS_SELECTOR, "tr")
    
    for element in elements: 
        team_table_dict3 = { 
            "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].get_attribute("textContent").split("\t")[0].split('. ')[1],     
            'Shots OT pg': element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
            'Dribbles pg': element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
            'Fouled pg': element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0], 
        }
        team_stat_df3.loc[len(team_stat_df3)] = team_table_dict3
        
        
    team_stat_df = pd.merge(league_table_df, team_stat_df1, how='left', on='team_name')
    team_stat_df = pd.merge(team_stat_df, team_stat_df2, how='left', on='team_name')
    team_stat_df = pd.merge(team_stat_df, team_stat_df3, how='left', on='team_name')
    
    # close webdriver
    driver.close()
    
    return team_stat_df

def crawling_league_teams(region, tournaments, api_delay_term=5):

    """
    cawling league team_id and team name datas
    
    Arg :
        region : region id (from whoscored) for certain league ex) england --- 252, spain --- 206
        tournaments : tournament(or league) id ex) premier league --- 2,
    
    return :
        crawling league team_id, team_name datas belong team_id parameter
        return pandas dataframe columns=team_id, team_name
    

    """
    
    # connect webdriver
    url = "https://1xbet.whoscored.com/Regions/" + str(region) + "/Tournaments/" + str(tournaments)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    # wait get league team datas
    time.sleep(api_delay_term) 
    
    # make pandas dataframe
    team_df = pd.DataFrame(columns=["team_id","team_name"])

    # get team data
    teams = driver.find_element(By.XPATH, "//*[@id='standings-23400-content']")
    teams = teams.find_elements(By.CSS_SELECTOR, "a.team-link")
    
    for team in teams:
        team_name = team.get_attribute("innerHTML")
        team_id = team.get_attribute("href").split("/")[4]
        team_df.loc[len(team_df)] = {"team_id":team_id, "team_name":team_name }
        
    # close webdriver
    driver.close()
    
    return team_df


def crawling_player_summary(team_id, api_delay_term=5):
    """
    crawling player statistics of certain team
    
    Args :
        team_id : team number 
        
    return :
        player statistics (dataframe)
    
    """

    # connect webdriver
    url = "https://www.whoscored.com/Teams/" + str(team_id)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    # wait for getting data
    time.sleep(api_delay_term)
    
    # make pandas dataframe
    player_summary_df = pd.DataFrame(columns=[
        "player_number", "name","age","position","tall","weight","games",
        "mins", "goals", "asists", "yel", "red", "spg", "ps","aw","motm", "rating"
        ])
    
    # get player summay datas
    elements = driver.find_elements(By.CSS_SELECTOR, "#player-table-statistics-body tr")
    for element in elements:
        
        player_dict = {
            "player_number": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, ("a"))[0].get_attribute("href").split("/")[4], 
            "name": element.find_element(By.CSS_SELECTOR, "td > a > span").get_attribute("textContent").split("\t")[0],     
            "age": element.find_element(By.CSS_SELECTOR, "td > span > span:nth-child(1)").get_attribute("textContent").split("\t")[0],
            "position": element.find_element(By.CSS_SELECTOR, "td > span > span:nth-child(2)").get_attribute("textContent").split("\t")[0][2:], 
            "tall": element.find_elements(By.CSS_SELECTOR, ("td"))[2].get_attribute("textContent").split("\t")[0],
            "weight": element.find_elements(By.CSS_SELECTOR, ("td"))[3].get_attribute("textContent").split("\t")[0], 
            "games": element.find_elements(By.CSS_SELECTOR, ("td"))[4].get_attribute("textContent").split("\t")[0], 
            "mins": element.find_elements(By.CSS_SELECTOR, ("td"))[5].get_attribute("textContent").split("\t")[0],
            "goals": element.find_elements(By.CSS_SELECTOR, ("td"))[6].get_attribute("textContent").split("\t")[0],
            "asists": element.find_elements(By.CSS_SELECTOR, ("td"))[7].get_attribute("textContent").split("\t")[0],
            "yel": element.find_elements(By.CSS_SELECTOR, ("td"))[8].get_attribute("textContent").split("\t")[0],
            "red": element.find_elements(By.CSS_SELECTOR, ("td"))[9].get_attribute("textContent").split("\t")[0],
            "spg": element.find_elements(By.CSS_SELECTOR, ("td"))[10].get_attribute("textContent").split("\t")[0],
            "ps": element.find_elements(By.CSS_SELECTOR, ("td"))[11].get_attribute("textContent").split("\t")[0],
            "aw": element.find_elements(By.CSS_SELECTOR, ("td"))[12].get_attribute("textContent").split("\t")[0],
            "motm": element.find_elements(By.CSS_SELECTOR, ("td"))[13].get_attribute("textContent").split("\t")[0],
            "rating": element.find_elements(By.CSS_SELECTOR, ("td"))[14].get_attribute("textContent").split("\t")[0],
        }
        
        player_summary_df.loc[len(player_summary_df)] = player_dict
        
    # close webdriver
    driver.close()
    player_summary_df.replace("-", "0", inplace=True)
    return player_summary_df


def crawling_player_statistics(URL):
    """
    crawling player statistics of certain league and season.
    
    Args :
        URL : player statistics webpage URL
        
    return :
        player statistics (dataframe)
    
    """
    url = str(URL)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    tabs = driver.window_handles
    
    time.sleep(3)

    while len(tabs) != 1:
        driver.switch_to.window(tabs[1])
        driver.close()

    driver.switch_to.window(tabs[0])
    time.sleep(3)
    
    page = driver.find_elements(By.CSS_SELECTOR, '#statistics-paging-summary > div > dl.listbox.right > dt > b')[0].get_attribute("textContent").split("\\")[0]
    page = int(page.split('/')[1].split(' ')[0])
    player_statistics_df = pd.DataFrame(columns=[
        "player_name", "team_number", "team_name", "Apps", "Mins", "Goals",
        "Assists", "Yel", "Red", "SpG","PS%", "AerialsWon","MoM","Rating"])
    
    with tqdm(total=page, file=sys.stdout) as pbar :
        for i in range(page):
            if i != 0:
                driver.find_element(By.ID, 'next').click()
                time.sleep(4)

            temp_df = pd.DataFrame(columns=[
                "player_name", "team_number", "team_name", "Apps", "Mins", "Goals",
                "Assists", "Yel", "Red", "SpG","PS%", "AerialsWon","MoM","Rating"])
            elements = driver.find_elements(By.CSS_SELECTOR, "#player-table-statistics-body tr")

            for element in elements:
                player_statistics_dict = { 
                    "player_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].
                    find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0],
                    "team_number": element.find_elements(By.CSS_SELECTOR, "td")[0].
                    find_elements(By.CSS_SELECTOR, "a")[1].get_attribute("href").split("/")[4],
                    "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, ("a"))[1].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0].split(",")[0],
                    "Apps": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
                    "Mins": element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
                    "Goals": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0],
                    "Assists": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
                    "Yel": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0], 
                    "Red": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
                    "SpG": element.find_elements(By.CSS_SELECTOR, "td")[8].get_attribute("textContent").split("\t")[0],
                    "PS%": element.find_elements(By.CSS_SELECTOR, "td")[9].get_attribute("textContent").split("\t")[0],
                    "AerialsWon": element.find_elements(By.CSS_SELECTOR, "td")[10].get_attribute("textContent").split("\t")[0],
                    "MoM": element.find_elements(By.CSS_SELECTOR, "td")[11].get_attribute("textContent").split("\t")[0],
                    "Rating": element.find_elements(By.CSS_SELECTOR, "td")[12].get_attribute("textContent").split("\t")[0],
                }
                temp_df.loc[len(temp_df)] = player_statistics_dict

            player_statistics_df = pd.concat([player_statistics_df,temp_df])
            pbar.update(1)
            pbar.set_description('page {}'.format(i+1))
            
    driver.close()
    player_statistics_df.replace("-", "0", inplace=True)
    return(player_statistics_df)
    
def crawling_player_statistics_defensive(URL):
    """
    crawling player statistics(defensive) of certain league and season.
    
    Args :
        URL : player statistics webpage URL
        
    return :
        player statistics (dataframe)
    
    """
    url = str(URL)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    
    time.sleep(3)

    driver.find_element(By.ID, 'next').click()

    time.sleep(3)

    driver.find_element(By.ID, 'first').click()
    
    time.sleep(3)
    
    driver.find_element(By.LINK_TEXT, "Defensive").click()
    
    time.sleep(3)
    page = driver.find_elements(By.CSS_SELECTOR, '#statistics-paging-defensive > div > dl.listbox.right > dt > b')[0].get_attribute("textContent")
    page = int(page.split('/')[1].split(' ')[0])
    
    player_statistics_df = pd.DataFrame(columns=[
            "player_name", "team_number", "team_name", "age","position", "Apps", "Mins", "Tackles",
            "Inter", "Fouls", "Offsides", "Clear","Drb", "Blocks","OwnG","Rating"])
    
    with tqdm(total=page, file=sys.stdout) as pbar :
        for i in range(page):
            if i != 0:
                driver.find_element(By.LINK_TEXT, 'next').click()
                time.sleep(4)

            temp_df = pd.DataFrame(columns=[
                "player_name", "team_number", "team_name", "age","position", "Apps", "Mins", "Tackles",
                "Inter", "Fouls", "Offsides", "Clear","Drb", "Blocks","OwnG","Rating"])

            elements = driver.find_elements(By.CSS_SELECTOR, "#player-table-statistics-body tr")[10:]

            for element in elements:
                player_statistics_dict = { 
                    "player_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0],
                    "team_number": element.find_elements(By.CSS_SELECTOR, "td")[0].
                    find_elements(By.CSS_SELECTOR, "a")[1].get_attribute("href").split("/")[4],
                    "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[1].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0].split(",")[0],
                    "age": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "span")[4].get_attribute("textContent").split("\t")[0],
                    "position": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "span")[5].get_attribute("textContent").split("\t")[0][2:],
                    "Apps": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
                    "Mins": element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
                    "Tackles": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0],
                    "Inter": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
                    "Fouls": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0], 
                    "Offsides": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
                    "Clear": element.find_elements(By.CSS_SELECTOR, "td")[8].get_attribute("textContent").split("\t")[0],
                    "Drb": element.find_elements(By.CSS_SELECTOR, "td")[9].get_attribute("textContent").split("\t")[0],
                    "Blocks": element.find_elements(By.CSS_SELECTOR, "td")[10].get_attribute("textContent").split("\t")[0],
                    "OwnG": element.find_elements(By.CSS_SELECTOR, "td")[11].get_attribute("textContent").split("\t")[0],
                    "Rating": element.find_elements(By.CSS_SELECTOR, "td")[12].get_attribute("textContent").split("\t")[0],
                }
                temp_df.loc[len(temp_df)] = player_statistics_dict


            player_statistics_df = pd.concat([player_statistics_df,temp_df])
            pbar.update(1)
            pbar.set_description('page {}'.format(i+1))
        
    driver.close()
    
    player_statistics_df.replace("-", "0", inplace=True)
    return(player_statistics_df)

def crawling_player_statistics_offensive(URL):
    """
    crawling player statistics(offensive) of certain league and season.
    
    Args :
        URL : player statistics webpage URL
        
    return :
        player statistics (dataframe)
    
    """
    url = str(URL)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    
    time.sleep(3)

    driver.find_element(By.ID, 'next').click()

    time.sleep(3)

    driver.find_element(By.ID, 'first').click()
    
    time.sleep(3)
    
    driver.find_element(By.LINK_TEXT, "Offensive").click()
    
    time.sleep(3)
    page = driver.find_elements(By.CSS_SELECTOR, '#statistics-paging-offensive > div > dl.listbox.right > dt > b')[0].get_attribute("textContent").split("\t")[0]
    page = int(page.split('/')[1].split(' ')[0])
    
    player_statistics_df = pd.DataFrame(columns=[
            "player_name", "team_number", "team_name", "age","position", "Apps", "Mins", "Goals",
            "Assists", "SpG", "KeyP", "Dribble","Fouled", "Off","Disp","UnsTch","Rating"])
    
    with tqdm(total=page, file=sys.stdout) as pbar :
        for i in range(page):
            if i != 0:
                driver.find_element(By.LINK_TEXT, 'next').click()
                time.sleep(4)

            temp_df = pd.DataFrame(columns=[
                "player_name", "team_number", "team_name", "age","position", "Apps", "Mins", "Goals",
                "Assists", "SpG", "KeyP", "Dribble","Fouled", "Off","Disp","UnsTch","Rating"])

            elements = driver.find_elements(By.CSS_SELECTOR, "#player-table-statistics-body tr")[10:]

            for element in elements:
                player_statistics_dict = { 
                    "player_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].
                    find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0],
                    "team_number": element.find_elements(By.CSS_SELECTOR, "td")[0].
                    find_elements(By.CSS_SELECTOR, "a")[1].get_attribute("href").split("/")[4],
                    "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR,"a")[1].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0].split(",")[0],
                    "age": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR,"span")[4].get_attribute("textContent").split("\t")[0],
                    "position": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "span")[5].get_attribute("textContent").split("\t")[0][2:],
                    "Apps": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
                    "Mins": element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
                    "Goals": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0],
                    "Assists": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
                    "SpG": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0], 
                    "KeyP": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
                    "Dribble": element.find_elements(By.CSS_SELECTOR, "td")[8].get_attribute("textContent").split("\t")[0],
                    "Fouled": element.find_elements(By.CSS_SELECTOR, "td")[9].get_attribute("textContent").split("\t")[0],
                    "Off": element.find_elements(By.CSS_SELECTOR, "td")[10].get_attribute("textContent").split("\t")[0],
                    "Disp": element.find_elements(By.CSS_SELECTOR, "td")[11].get_attribute("textContent").split("\t")[0],
                    "UnsTch": element.find_elements(By.CSS_SELECTOR, "td")[12].get_attribute("textContent").split("\t")[0],
                    "Rating": element.find_elements(By.CSS_SELECTOR, "td")[13].get_attribute("textContent").split("\t")[0],
                }
                temp_df.loc[len(temp_df)] = player_statistics_dict


            player_statistics_df = pd.concat([player_statistics_df,temp_df])
            pbar.update(1)
            pbar.set_description('page {}'.format(i+1))
        
    driver.close()

    player_statistics_df.replace("-", "0", inplace=True)
    return(player_statistics_df)

def crawling_player_statistics_passing(URL):
    url = str(URL)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    
    time.sleep(3)

    driver.find_element(By.ID, 'next').click()

    time.sleep(3)

    driver.find_element(By.ID, 'first').click()
    
    time.sleep(3)
    
    driver.find_element(By.LINK_TEXT, "Passing").click()
    
    time.sleep(3)
    page = driver.find_elements(By.CSS_SELECTOR, '#statistics-paging-passing > div > dl.listbox.right > dt > b')[0].get_attribute("textContent")
    page = int(page.split('/')[1].split(' ')[0])
    
    player_statistics_df = pd.DataFrame(columns=[
            "player_name", "team_number", "team_name", "age","position", "Apps", "Mins", "Assists",
            "KeyP", "AvgP","PS%", "Crosses","LongB","ThrB","Rating"])
    
    with tqdm(total=page, file=sys.stdout) as pbar :
        for i in range(page):
            if i != 0:
                driver.find_element(By.LINK_TEXT, 'next').click()
                time.sleep(4)

            temp_df = pd.DataFrame(columns=[
                "player_name", "team_number", "team_name", "age","position", "Apps", "Mins","Assists",
                "KeyP", "AvgP","PS%", "Crosses","LongB","ThrB","Rating"])

            elements = driver.find_elements(By.CSS_SELECTOR, "#player-table-statistics-body tr")[10:]

            for element in elements:
                player_statistics_dict = { 
                    "player_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[0].
                    find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0],
                    "team_number": element.find_elements(By.CSS_SELECTOR, "td")[0].
                    find_elements(By.CSS_SELECTOR, "a")[1].get_attribute("href").split("/")[4],
                    "team_name": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "a")[1].find_elements(By.CSS_SELECTOR, "span")[0].get_attribute("textContent").split("\t")[0].split(",")[0],
                    "age": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "span")[4].get_attribute("textContent").split("\t")[0],
                    "position": element.find_elements(By.CSS_SELECTOR, "td")[0].find_elements(By.CSS_SELECTOR, "span")[5].get_attribute("textContent").split("\t")[0][2:],
                    "Apps": element.find_elements(By.CSS_SELECTOR, "td")[2].get_attribute("textContent").split("\t")[0],
                    "Mins": element.find_elements(By.CSS_SELECTOR, "td")[3].get_attribute("textContent").split("\t")[0], 
                    "Assists": element.find_elements(By.CSS_SELECTOR, "td")[4].get_attribute("textContent").split("\t")[0],
                    "KeyP": element.find_elements(By.CSS_SELECTOR, "td")[5].get_attribute("textContent").split("\t")[0], 
                    "AvgP": element.find_elements(By.CSS_SELECTOR, "td")[6].get_attribute("textContent").split("\t")[0], 
                    "PS%": element.find_elements(By.CSS_SELECTOR, "td")[7].get_attribute("textContent").split("\t")[0],
                    "Crosses": element.find_elements(By.CSS_SELECTOR, "td")[8].get_attribute("textContent").split("\t")[0],
                    "LongB": element.find_elements(By.CSS_SELECTOR, "td")[9].get_attribute("textContent").split("\t")[0],
                    "ThrB": element.find_elements(By.CSS_SELECTOR, "td")[10].get_attribute("textContent").split("\t")[0],
                    "Rating": element.find_elements(By.CSS_SELECTOR, "td")[11].get_attribute("textContent").split("\t")[0],
                }
                temp_df.loc[len(temp_df)] = player_statistics_dict


            player_statistics_df = pd.concat([player_statistics_df,temp_df])
            pbar.update(1)
            pbar.set_description('page {}'.format(i+1))
        
    driver.close()
    player_statistics_df.replace("-", "0", inplace=True)

    return(player_statistics_df)

def crwaling_player_stats_at_once(URL):
    stats_summary = crawling_player_statistics(URL)
    print('player stats summary : done')
    stats_defensive = crawling_player_statistics_defensive(URL)
    print('player stats defensive : done')
    stats_offensive = crawling_player_statistics_offensive(URL)
    print('player stats offensive : done')
    stats_passing = crawling_player_statistics_passing(URL)
    print('player stats pasing : done')
    player_stats = pd.merge(pd.merge(stats_passing, stats_summary), 
                            pd.merge(stats_offensive, stats_defensive))
    return(player_stats)