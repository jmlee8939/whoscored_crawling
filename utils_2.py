#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pandas as pd
import time
import pickle
import numpy as np
from selenium import webdriver
import os


def crawling_game_results_add(path, url, api_delay_term=4):
    driver = webdriver.Chrome(path)
    
    # wait get league team datas
    time.sleep(api_delay_term) 
    
    url_preview = url.replace('Live','Preview')
    url_show = url.replace('Live','Show')
    url_matchreport = url.replace('Live','MatchReport')
    
    try : 
        driver.get(url)

        match_log = driver.find_element_by_css_selector('div.match-centre-stats').find_elements_by_css_selector('span.match-centre-stat-value')
        home_shot = match_log[2].text
        away_shot = match_log[3].text
        home_possession  = match_log[4].text
        away_possession = match_log[5].text
        home_pass_success = match_log[6].text
        away_pass_success = match_log[7].text
        home_dribbles = match_log[8].text
        away_dribbles = match_log[9].text
        home_aerials_won = match_log[10].text
        away_aerials_won = match_log[11].text
        home_tackles = match_log[12].text
        away_tackles = match_log[13].text
        home_corners = match_log[14].text
        away_corners = match_log[15].text
        home_dispossessed = match_log[16].text
        away_dispossessed = match_log[17].text
    except : 
        print('open error')
        return()
    
    try : 
        driver.get(url_preview)
    except : 
        print('open_error 1')
        return()
        
    time.sleep(api_delay_term)
    # get home and away
    try :
        missing_players_home = driver.find_element_by_css_selector('div.col12-lg-6.col12-m-6.col12-s-6.col12-xs-12.home.small-display-on')
        ratings = missing_players_home.find_elements_by_css_selector('td.rating')
        home_missing_player = len(ratings)
        home_missing_player_rating = []
        for rating in ratings:
            try : home_missing_player_rating.append(float(rating.text))
            except : continue
        home_missing_player_rating = round(np.mean(np.array(home_missing_player_rating)),2)
        missing_players_away = driver.find_element_by_css_selector('div.col12-lg-6.col12-m-6.col12-s-6.col12-xs-12.away.small-display-off')
        ratings = missing_players_away.find_elements_by_css_selector('td.rating')
        away_missing_player = len(ratings)
        away_missing_player_rating = []
        for rating in ratings:
            try : away_missing_player_rating.append(float(rating.text))
            except : continue
        away_missing_player_rating = round(np.mean(np.array(away_missing_player_rating)),2)

        home = driver.find_element_by_css_selector('span.col12-lg-4.col12-m-4.col12-s-0.col12-xs-0.home.team').text
        away = driver.find_element_by_css_selector('span.col12-lg-4.col12-m-4.col12-s-0.col12-xs-0.away.team').text
        elements = driver.find_elements_by_css_selector('div.info-block.cleared')
        score = elements[1]
        half_home_score = score.find_elements_by_css_selector('dd')[0].text.split(':')[0]
        half_away_score = score.find_elements_by_css_selector('dd')[0].text.split(':')[1]
        full_home_score = score.find_elements_by_css_selector('dd')[1].text.split(':')[0]
        full_away_score = score.find_elements_by_css_selector('dd')[1].text.split(':')[1]
    
        kick_off = elements[2].find_elements_by_css_selector('dd')[0].text
        date = elements[2].find_elements_by_css_selector('dd')[1].text
    
    except :
        print('carwling preview error')
        missing_players_home = 'null'
        home_missing_player  = 'null'
        home_missing_player_rating = 'null'
        missing_players_away = 'null'
        away_missing_player  = 'null'
        away_missing_player_rating  = 'null'
        home = 'null'
        away = 'null'
        elements = 'null'
        score = 'null'
        half_home_score = 'null'
        half_away_score ='null'
        full_home_score ='null'
        full_away_score ='null'
        kick_off = 'null'
        date = 'null'
    
    ########### show data
    try :
        driver.get(url_show)
    except :
        print('open error 2')
        return()
    
    # wait get league team datas
    time.sleep(api_delay_term)
    try :
        
        # get home and away
        matchup_home_goals = driver.find_elements_by_css_selector('td.previous-meetings-stat')[0].text
        matchup_away_goals = driver.find_elements_by_css_selector('td.previous-meetings-stat')[3].text
        matchup_home_wins = driver.find_elements_by_css_selector('span.title')[0].text 
        matchup_draw = driver.find_elements_by_css_selector('span.title')[1].text 
        matchup_away_wins = driver.find_elements_by_css_selector('span.title')[2].text 

    except:
                # get home and away
        print('crawling show error')
        matchup_home_goals = 'null'
        matchup_away_goals = 'null'
        matchup_home_wins = 'null'
        matchup_draw =  'null'
        matchup_away_wins =  'null'
    
        
        ########### show data
    try:    
        driver.get(url_matchreport)
    except :
        print('open error 3')
        return()
        # wait get league team datas
    try:     
        time.sleep(api_delay_term) 
        attempt = driver.find_element_by_css_selector('div.stat-group').find_elements_by_css_selector('span.stat-value')
        home_total_att = attempt[0].find_elements_by_css_selector('span')[0].text
        away_total_att = attempt[1].find_elements_by_css_selector('span')[0].text
        home_open_att = attempt[2].find_elements_by_css_selector('span')[0].text
        away_open_att = attempt[3].find_elements_by_css_selector('span')[0].text
        home_set_att = attempt[4].find_elements_by_css_selector('span')[0].text
        away_set_att = attempt[5].find_elements_by_css_selector('span')[0].text
        home_counter_att = attempt[6].find_elements_by_css_selector('span')[0].text
        away_counter_att = attempt[7].find_elements_by_css_selector('span')[0].text
        home_pk_att = attempt[8].find_elements_by_css_selector('span')[0].text
        away_pk_att = attempt[9].find_elements_by_css_selector('span')[0].text
        home_own_att = attempt[10].find_elements_by_css_selector('span')[0].text 
        away_own_att = attempt[11].find_elements_by_css_selector('span')[0].text 

        passes = driver.find_element_by_css_selector('#live-chart-stats-options')
        passes.find_elements_by_css_selector('a')[1].click()

        time.sleep(2)
        passes = driver.find_elements_by_css_selector('div.stat-group')[2].find_elements_by_css_selector('span.stat-value')
        home_total_passes = passes[0].find_elements_by_css_selector('span')[0].text
        away_total_passes = passes[1].find_elements_by_css_selector('span')[0].text
        home_crosses_passes = passes[2].find_elements_by_css_selector('span')[0].text
        away_crosses_passes = passes[3].find_elements_by_css_selector('span')[0].text
        home_long_balls = passes[6].find_elements_by_css_selector('span')[0].text
        away_long_balls = passes[7].find_elements_by_css_selector('span')[0].text
        home_short_passes = passes[8].find_elements_by_css_selector('span')[0].text
        away_short_passes = passes[9].find_elements_by_css_selector('span')[0].text

    except:
        print('crawling show/pass error')
        attempt = 'null'
        home_total_att ='null'
        away_total_att = 'null'
        home_open_att = 'null'
        away_open_att = 'null'
        home_set_att = 'null'
        away_set_att = 'null'
        home_counter_att = 'null'
        away_counter_att = 'null'
        home_pk_att = 'null'
        away_pk_att = 'null'
        home_own_att = 'null'
        away_own_att = 'null'
        passes = 'null'
        home_total_passes = 'null'
        away_total_passes = 'null'
        home_crosses_passes ='null'
        away_crosses_passes = 'null'
        home_long_balls = 'null'
        away_long_balls ='null'
        home_short_passes ='null'
        away_short_passes = 'null'
        

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

def crawling_seasons_add(path, season_name, missing_list):
    file_name = season_name+'_match_number.csv'
    file_names = os.listdir(os.getcwd())
    if file_name in file_names:
        match_number = pd.read_csv(file_name)['0']
        print('find '+ file_name + 'done')
    else : 
        print('there are no match_number.csv file')
        return()
    
    a = 0
    error_list = []
    mat_df = match_df()
    for missing_match_no in missing_list:
        start_time = time.time()
        match = match_number.iloc[missing_match_no]
    
        try :
            temp_dict = crawling_game_results_add(path, match, 4)
            mat_df.loc[len(mat_df)] = temp_dict
            print('match_number {} : cawling done'.format(missing_match_no))
        except :
            
            print('match_number {} : error'.format(missing_match_no))
            
            try :             
                temp_dict = crawling_game_results_add(path, match, 4)
                mat_df.loc[len(mat_df)] = temp_dict
                print('match_number {} : crawling done (retry)'.format(missing_match_no))
                
            except :
                print('match_number {} : final error'.format(missing_match_no))
                error_list.append(missing_match_no)
            
        if len(mat_df)%10 ==0:
            mat_df.to_csv(season_name+'_add_match.csv')
            time.sleep(4) 
        print(time.time()-start_time)
    mat_df.to_csv(season_name+'_add_match.csv')
    print(error_list)    
    return(error_list)   

def duplicated_match_filter(season, match_no):
    match = pd.read_csv(season+'_match.csv')[['home','away']]
    try : 
        add = pd.read_csv(season+'_add_match.csv')[['home','away']]
        full_season = pd.concat((match,add), axis=0)
    except : 
        print('there are no add match file')
        full_season = match
        print(len(full_season[full_season.duplicated()]))
        print(len(full_season))
    if len(full_season[full_season.duplicated()]) == 0 and len(full_season) == match_no:
        match = pd.read_csv(season+'_match.csv').iloc[:,1:]
        add = pd.read_csv(season+'_add_match.csv').iloc[:,1:]
        full_season_df = pd.concat((match,add), axis=0)
        full_season_df.to_csv(season+'_full_match.csv')
        print('done')

    return(full_season[full_season.duplicated()], len(full_season))
