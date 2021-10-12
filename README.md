# Whoscored_crawling
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

| team_name         | P  | W  | D  | L  | GF  | GA | GD | Pts | Goals | Shots pg | Yellow | Red | Poss% | 
|-------------------|----|----|----|----|-----|----|----|-----|-------|----------|--------|-----|-------| 
| Liverpool         | 38 | 32 | 3  | 3  | 85  | 33 | 52 | 99  | 85    | 15.6     | 38     | 1   | 59.6  | 
| Manchester City   | 38 | 26 | 3  | 9  | 102 | 35 | 67 | 81  | 102   | 19.6     | 60     | 4   | 62.6  | 
| Manchester United | 38 | 18 | 12 | 8  | 66  | 36 | 30 | 66  | 66    | 14.3     | 73     | 0   | 54.6  | 
| Chelsea           | 38 | 20 | 6  | 12 | 69  | 54 | 15 | 66  | 69    | 16.4     | 60     | 0   | 57.9  | 
| Leicester         | 38 | 18 | 8  | 12 | 67  | 41 | 26 | 62  | 67    | 14.2     | 41     | 3   | 55.1  | 

... more teams and features 


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
|player_name    |team_number|team_name|age|position  |Apps|Mins|Assists|KeyP|AvgP|PS% |Crosses|LongB|ThrB|Rating|sub|Goals|
|---------------|-----------|---------|---|----------|----|----|-------|----|----|----|-------|-----|----|------|---|-----|
|Kevin De Bruyne|167        |Man City |30 |M(CLR),FW |32  |2800|20     |3.9 |54.5|81.5|2.1    |3.5  |0.4 |7.97  |3  |13   |
|Ricardo Pereira|14         |Leicester|28 |D(LR),M(R)|28  |2520|2      |1   |56.1|78.9|0.3    |2.1  |0.1 |7.5   |0  |3    |
|Adama Traore   |161        |Wolves   |25 |M(CLR),FW |27  |2608|9      |1.3 |19.2|74.4|1.2    |0.2  |0.1 |7.49  |10 |4    |
|Riyad Mahrez   |167        |Man City |30 |AM(CLR)   |21  |1942|9      |1.8 |33.2|90.1|0.6    |1.7  |0.2 |7.48  |12 |11   |
|Sadio Mane     |26         |Liverpool|29 |AM(CLR),FW|31  |2756|7      |1.7 |31.5|81.6|0.3    |1    |0.1 |7.45  |4  |18   |
|Mohamed Salah  |26         |Liverpool|29 |AM(CLR),FW|33  |2888|10     |1.8 |28.8|76.5|0.3    |0.4  |0.1 |7.4   |1  |19   |

## match results data 




