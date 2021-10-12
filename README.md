# Whoscored_crawling
by jaeminiman  
soccer_data_crawling from [whoscored.com](http://whoscored.com)  
using chrome version --  94.0.4606.81(64bit)  
using chromdriver -- 94.0.4606.61

a lot of soccer data for various seasons and leagues in this website.
I want to crop this data for my soccer data analysis.

## Seasonal team data
details are explained in *"seasonal team data.ipynb"* 

#### Seasonal statistics of teams
  - seasonal wins, draws, losses
  - seasonal goals(scored), goals(conceded)  
  - seasonal possesion %
  - seasonal gotten card  
... etc

ex) PL 1920 table

|team_name        |P  |W        |D  |L         |GF |GA  |GD |Pts|Goals|Shotspg|Yellow|Red|Poss%|Pass%|A_Won|Rating|Shotedpg|Tacklespg|Interceptpg|Foulspg|Offsidespg|ShotsOTpg|Dribblespg|Fouledpg|
|-----------------|---|---------|---|----------|---|----|---|---|-----|-------|------|---|-----|-----|-----|------|--------|---------|-----------|-------|----------|-----------|----------|--------|
|Liverpool        |38 |32       |3  |3         |85 |33  |52 |99 |85   |15.6   |38    |1  |59.6 |84.3 |17.6 |6.94  |9       |14.5     |9.3        |8.7    |1.4       |6.1       |10.2      |7.7     |
|Manchester City  |38 |26       |3  |9         |102|35  |67 |81 |102  |19.6   |60    |4  |62.6 |89.3 |13.6 |7.05  |7.4     |13.5     |9.3        |9.5    |1.8       |7         |12.8      |7.8     |
|Manchester United|38 |18       |12 |8         |66 |36  |30 |66 |66   |14.3   |73    |0  |54.6 |83.6 |15   |6.83  |10.3    |15.3     |9.9        |11.1   |1.5       |5.7       |11.7      |11.2    |
|Chelsea          |38 |20       |6  |12        |69 |54  |15 |66 |69   |16.4   |60    |0  |57.9 |85.2 |18.7 |6.86  |8.5     |16.8     |12.1       |10.2   |1.7       |5.9       |12.1      |10.1    |
|Leicester        |38 |18       |8  |12        |67 |41  |26 |62 |67   |14.2   |41    |3  |55.1 |82.8 |17.8 |6.87  |9.9     |19.5     |11.1       |11     |1.7       |5         |9.9       |11.7    |
|Tottenham        |38 |16       |11 |11        |61 |47  |14 |59 |61   |11.7   |82    |3  |51.5 |81.4 |17.1 |6.78  |14.2    |17.5     |10         |11.1   |1.7       |4.2       |11.8      |11.2    |



... more teams


## Seasnoal player data
details are explained in *"seasonal player data.ipynb"*

#### Seasonal statistics of players
  - age
  - position
  - appearance
  - goals & assists
  - average rating
  ... etc

ex) PL 1920 player 
|player_name    |team_number|team_name|age|position  |Apps|Mins|Assists|KeyP|AvgP|PS% |Crosses|LongB|ThrB|Rating|sub|Goals|Yel|Red|SpG|AerialsWon|MoM|Dribble|Fouled|Off|Disp|UnsTch|Tackles|Inter|Fouls|Offsides|Clear|Drb|Blocks|OwnG|
|---------------|-----------|---------|---|----------|----|----|-------|----|----|----|-------|-----|----|------|---|-----|---|---|---|----------|---|-------|------|---|----|------|-------|-----|-----|--------|-----|---|------|----|
|Kevin De Bruyne|167        |Man City |30 |M(CLR),FW |32  |2800|20     |3.9 |54.5|81.5|2.1    |3.5  |0.4 |7.97  |3  |13   |3  |0  |2.8|0.5       |10 |1.4    |0.8   |0.1|0.9 |1.3   |1.3    |0.5  |0.7  |0       |0.7  |1.4|0.1   |0   |
|Ricardo Pereira|14         |Leicester|28 |D(LR),M(R)|28  |2520|2      |1   |56.1|78.9|0.3    |2.1  |0.1 |7.5   |0  |3    |1  |0  |0.6|1.5       |2  |2.1    |1.3   |0  |1.1 |1.6   |4.3    |1.8  |1.6  |0.3     |2.6  |1.9|0.2   |0   |
|Adama Traore   |161        |Wolves   |25 |M(CLR),FW |27  |2608|9      |1.3 |19.2|74.4|1.2    |0.2  |0.1 |7.49  |10 |4    |1  |0  |1.2|1.2       |6  |5      |2.1   |0.2|1.8 |2.4   |0.9    |0.4  |1.1  |0       |0.4  |0.4|0.1   |0   |
|Riyad Mahrez   |167        |Man City |30 |AM(CLR)   |21  |1942|9      |1.8 |33.2|90.1|0.6    |1.7  |0.2 |7.48  |12 |11   |0  |0  |2.2|0.3       |3  |1.6    |0.9   |0.4|1   |1.4   |0.8    |0.5  |0.4  |0       |0.2  |0.8|0     |0   |
|Sadio Mane     |26         |Liverpool|29 |AM(CLR),FW|31  |2756|7      |1.7 |31.5|81.6|0.3    |1    |0.1 |7.45  |4  |18   |3  |0  |2.2|1.2       |7  |2      |1.5   |0.4|1.6 |2.9   |1.3    |0.4  |1.3  |0       |0.2  |0.8|0     |0   |
|Mohamed Salah  |26         |Liverpool|29 |AM(CLR),FW|33  |2888|10     |1.8 |28.8|76.5|0.3    |0.4  |0.1 |7.4   |1  |19   |1  |0  |3.9|0.4       |6  |1.5    |0.5   |0.6|2   |2.6   |0.5    |0.2  |0.5  |0       |0.1  |0.5|0     |0   |

... more players

## match results data 
details are explained in *"match results data.ipynb"*
some codes for utilized functions are in *"utils.py"*

#### match results statistics
  - score
  - pass accuracy
  - total shot 
  - total passes
  ... etc

ex) PL 2021 season match results

|home_shot      |away_shot|home_possession|away_possession|home_pass_success|away_pass_success|home_dribbles|away_dribbles|home_aerials_won|away_aerials_won|home_tackles|away_tackles|home_corners|away_corners|home_dispossessed|away_dispossessed|home_missing_player|away_missing_player|home_missing_player_rating|away_missing_player_rating|home|away|half_home_score|half_away_score|full_home_score|full_away_score|kick_off|date           |matchup_home_goals|matchup_away_goals|matchup_home_wins|matchup_draw|matchup_away_wins|home_total_att|away_total_att|home_open_att|away_open_att|home_set_att|away_set_att|home_counter_att|away_counter_att|home_pk_att|away_pk_att|home_own_att|away_own_att|home_total_passes|away_total_passes|home_crosses_passes|away_crosses_passes|home_long_balls|away_long_balls|home_short_passes|away_short_passes|
|---------------|---------|---------------|---------------|-----------------|-----------------|-------------|-------------|----------------|----------------|------------|------------|------------|------------|-----------------|-----------------|-------------------|-------------------|--------------------------|--------------------------|----|----|---------------|---------------|---------------|---------------|--------|---------------|------------------|------------------|-----------------|------------|-----------------|--------------|--------------|-------------|-------------|------------|------------|----------------|----------------|-----------|-----------|------------|------------|-----------------|-----------------|-------------------|-------------------|---------------|---------------|-----------------|-----------------|
|21             |5        |73.5           |26.5           |85               |64               |9            |5            |23              |27              |12          |12          |14          |2           |8                |8                |3                  |3                  |6.13                      |6.49                      |Brighton|Sheffield United|0              |0              |1              |1              |12:00   |Jpl, 20-Des-20 |5                 |8                 |Won (17%)        |Drew (33%)  |Won (50%)        |21            |5             |13           |2            |8           |2           |0               |1               |0          |0          |0           |0           |591              |215              |37                 |9                  |57             |51             |497              |155              |
|11             |6        |54.8           |45.2           |86               |79               |14           |6            |21              |19              |21          |14          |9           |2           |6                |11               |3                  |3                  |6.67                      |6.87                      |Wolverhampton Wanderers|Tottenham|0              |1              |1              |1              |19:15   |Jpl, 27-Des-20 |10                |11                |Won (33%)        |Drew (17%)  |Won (50%)        |11            |6             |8            |2            |3           |3           |0               |1               |0          |0          |0           |0           |579              |476              |30                 |7                  |62             |51             |486              |417              |
|13             |9        |69.2           |30.8           |80               |60               |8            |10           |16              |21              |18          |16          |7           |5           |8                |11               |8                  |4                  |6.58                      |6.9                       |Leeds|Aston Villa|0              |1              |0              |1              |17:30   |Jmos, 27-Feb-21|9                 |6                 |Won (33%)        |Drew (50%)  |Won (17%)        |13            |9             |9            |3            |4           |4           |0               |2               |0          |0          |0           |0           |547              |243              |27                 |11                 |66             |73             |454              |159              |
|14             |10       |47.1           |52.9           |85               |88               |6            |10           |12              |9               |9           |14          |6           |2           |6                |7                |3                  |3                  |6.53                      |6.65                      |Wolverhampton Wanderers|Fulham|0              |0              |1              |0              |14:00   |Jpl, 04-Okt-20 |11                |8                 |Won (50%)        |Drew (33%)  |Won (17%)        |14            |10            |8            |3            |4           |6           |2               |1               |0          |0          |0           |0           |500              |561              |18                 |28                 |53             |59             |429              |474              |
|17             |4        |72.7           |27.3           |86               |64               |8            |3            |17              |11              |19          |10          |7           |3           |7                |9                |4                  |1                  |6.67                      |6.21                      |Leicester|West Bromwich Albion|3              |0              |3              |0              |20:00   |Alh, 22-Apr-21 |11                |5                 |Won (67%)        |Drew (17%)  |Won (17%)        |17            |4             |13           |2            |3           |2           |1               |0               |0          |0          |0           |0           |721              |270              |10                 |10                 |48             |57             |662              |203              |
|15             |15       |52.4           |47.6           |82               |81               |13           |18           |19              |24              |14          |13          |6           |5           |9                |4                |2                  |0                  |6.78                      |                          |Tottenham|Fulham|1              |0              |1              |1              |20:15   |Jtan, 13-Jan-21|13                |5                 |Won (83%)        |Drew (0%)   |Won (17%)        |15            |15            |9            |9            |5           |5           |1               |1               |0          |0          |0           |0           |545              |496              |21                 |20                 |56             |60             |468              |416              |

