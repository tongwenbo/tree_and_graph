# Tree and graph


## python scripts for data-processing
under path ./python/ are 4 filers:

### dataset_exploration.ipynb 
It is the jupyter notebook file of the dataset. In this file you can have a thorough understanding of the dataset in this work, which is the dataset of all the steam games.

### steam-store-games.csv 
It is the original dataset.

### make_hierarchy.py 
It transfers a dataset to a tree structure. 

1. After cloning the repo, use cd .\python\ to go to the folder.
2. Then use python .\make_hierarchy.py -h to see the arguments of this script. Notice parameter "value" should be used.

3. For instance, if genres should be valued based on average playtime, then use python `.\make_hierarchy.py .\steam-store-games.csv genres average_playtime`.
This will create a filtered_steam.csv file under the python folder, which contains the data filtered by the filtering function.

4. The filtering parameters can be changed in function: def filter_csv(path). These parameters can be input arguments, however, that will make the argument-
list incredibly long and not user-friendly. So I put them in the function for now.

5. The generated json file for visualization will be in ./public/data/ with a "_try" to avoid covering the data I used for visualization.


## visualization
1. If you are now in python folder, use cd .. to get back.
2. Use `npm install` to install the necessary packages.
3. Then use `npm run dev` to start the server.
4. Use Ctrl + C to end the terminal.
