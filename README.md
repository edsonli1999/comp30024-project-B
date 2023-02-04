# COMP30024 Cachex game playing agent

Alcos_inc algorithm made by Savas and Edson to play the University of Melbourne subject COMP30024 game; Cachex.

# Tech stack:
Python\
A* search

## Running
To run on shell, input: python -m referee <board_size> <red_player_module> <blue_player_module>;\
where <board_size> is the number of tiles vertically or horizontally (n in a board of n x n), and\
<red_player_module> and <blue_player_module> are the names of the directories that contain the AI code, with player.py in them.\

example command:
```
python -m referee 5 alcos_inc other-agents/test_greedy
```

## Additional notes:
Code developed by us is under the directory "alcos_inc", as the name of our group.
  
