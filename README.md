# Assignment 3 of Tong


## python script
under path ./python/ are 4 filers:

### Task1.ipynb 
It is the jupyter notebook file of Task 1.

### steam-store-games.csv 
It is the original dataset.

### make_hierarchy.py 
It transfers a dataset to a tree structure. 

After cloning the repo, use cd .\assignment-03\python\ to go to the folder.
Then use python .\make_hierarchy.py -h to see the arguments of this script. I added a new parameter "value".

For instance, if genres should be valued based on average playtime, then use python .\make_hierarchy.py .\steam-store-games.csv genres average_playtime.
This will create a filtered_steam.csv file under the python folder, which contains the data filtered by the filtering function.

The filtering parameters can be changed in function: def filter_csv(path). These parameters can be input arguments, however, that will make the argument-
list incredibly long and not user-friendly. So I put them in the function for now.

The generated json file for visualization will be in ./public/data/ with a "_try" to avoid covering the data I used for visualization.


## visualization
If you are now in python folder, use cd .. to get back.
Then use npm run dev to start the server.
