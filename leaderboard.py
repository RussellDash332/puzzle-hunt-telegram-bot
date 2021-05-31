# Generates leaderboards from DontPad
# Manual input to game_data/leaderboard.json then let the sorting do the work

import json

def read_json(filename):
    datafile = open(filename, 'r',  encoding='utf-8')
    return json.loads(datafile.read())

# Data format: dictionary with key = LB name, value = DontPad data
lb_data = read_json("game_data/leaderboard.json")

# Data cleaning
new_lb_data = []
for k,v in lb_data.items():
    new_lb_data.append([k,v['score'],v['solved_time']])

# Sorting key: sort by score descending, then for the same score sort by time taken to solve each puzzle ascending.
new_lb_data.sort(key = lambda x:[-int(x[1]),[x[2][0]]+[x[2][i]-x[2][i-1] for i in range(1,len(x[2]))]])

# Update content before final output
new_lb_data = list(map(lambda x: x[0]+": "+x[1], new_lb_data))

for i in range(len(new_lb_data)):
    print(new_lb_data[i])