# Generates leaderboards from DontPad
# Manual input to game_data/leaderboard.json then let the sorting do the work

import json
from env import DP_URL, dry_run, actual_run
from dpad_manager import read_dp

def read_json(filename):
    datafile = open(filename, 'r',  encoding='utf-8')
    return json.loads(datafile.read())

# Data format: dictionary with key = LB name, value = DontPad data
# lb_data = read_json("game_data/leaderboard.json")
lb_data = dict(map(lambda x: (x[0],json.loads(read_dp(x[1]))),actual_run.items()))

# Data cleaning
new_lb_data = []
for k,v in lb_data.items():
    new_lb_data.append([k,v['score'],v['solved_time']])

# Old sorting key: sort by score descending, then for the same score sort by time taken to solve each puzzle ascending.
# new_lb_data.sort(key = lambda x:[-int(x[1]),[x[2][0]]+[x[2][i]-x[2][i-1] for i in range(1,len(x[2]))]])

# New sorting key: sort by score descending, then for the same score sort by total time taken to solve the last puzzle until the first puzzle ascending.
new_lb_data.sort(key = lambda x:[-int(x[1]),x[2][::-1]])

# Update content before final output
new_lb_data = list(map(lambda x: x[0]+": "+x[1], new_lb_data))

# Display top 4
emotes = ['🥇','🥈','🥉','🆒']
print("👾 CURRENT SCORES 👾")
for i in range(min(4,len(new_lb_data))):
    print(emotes[i]+" "+new_lb_data[i])