import common
import argparse
import logging

import pandas as pd

from pathlib import Path
from anytree import Node, RenderTree, AsciiStyle, search, LevelOrderIter
from anytree.exporter import JsonExporter


# filter out the games we want
def filter_csv(path):
    dff = pd.read_csv(path)
    print(dff)

    for i in range(len(dff)):
        max = 0
        for j in str(dff["owners"][i]).split('-'):
            if int(j) > max:
                max = int(j)
        if max < 5000001:                                                           # filter the games at least having 500 milion owners
            dff.drop(i, axis=0, inplace=True)
        elif dff["average_playtime"][i] < 100 or dff["median_playtime"][i] < 100:   # filter the games at least having 100 hours of playtime
            dff.drop(i, axis=0, inplace=True)
        elif dff["english"][i] != 1:                                                # filter the games having english version
            dff.drop(i, axis=0, inplace=True)
        elif dff["positive_ratings"][i] / dff["negative_ratings"][i] < 7:           # filter the games with over 85% positive ratings
            dff.drop(i, axis=0, inplace=True)

    print(dff)
    out_path = "./filtered_steam.csv"
    dff.to_csv(out_path)

    return out_path


def export_hierarchy(path: str, root: object):
    """
    Exports a given anytree hierarchy to the given path.

    Parameters:
        path (str): filepath to save the tree at
        root (object): anytree node representing the tree

    Returns:
        Nothing
    """

    logging.info(f'saving tree as JSON to "{path}"')
    exporter = JsonExporter(indent=2, sort_keys=True)
    with open(path, 'w') as file:
        exporter.write(root, file)


def filter_list(df: pd.DataFrame, key: str, value: str, maxdepth: int):
    """
    Create a tree by filtering the given dataframe by the order of occurrences
    of string in a list-like attribute, e.g. the genres.

    Parameters:
        df (DataFrame): pandas dataframe holding the data
        key (str): the column name of the data to structure the tree by
        maxdepth (int): the maximum depth of the tree

    Returns:
        root (obj): root node (anytree) of the resulting tree
    """

    # get the values for the first level of the hierarchy (e.g. the first genres)
    df['g1'] = df[key].map(lambda x: x[0])
    # get unique values for the attribute and sort
    g1 = sorted(df['g1'].unique())
    # print(g1)

    # the root node of our tree
    root = Node(name='root')

    # add top level nodes
    for g in g1:
        Node(g, parent=root, all=g)

    # logging.info(f'first tree level contains {len(g1)} nodes')
    # logging.info(f'current tree\n{RenderTree(root, style=AsciiStyle()).by_attr()}')

    # for each item in our dataset (data frame)
    for d in df.itertuples():

        # get the values for our key (e.g. genres)
        values = getattr(d, key)
        # make them into a single string again (but limited to max depth)
        all_keys = ','.join(values[:maxdepth])
        # find the direct parent node (e.g. 'action' for 'action,adventure')
        parent_node = search.find(
            root,
            lambda node: hasattr(node, 'all') and node.all == all_keys
        )

        # if the parent node does not yet exist, start from the furthest parent and
        # insert missing parents (nodes) until we have the direct parent of our node
        if not parent_node:

            idx = 1
            tmp = ','.join(values[0:idx + 1])
            pnode = search.find(root, lambda node: hasattr(node, 'all') and node.all == values[0])

            while idx < maxdepth:
                tmp_node = search.find(root, lambda node: hasattr(node, 'all') and node.all == tmp)
                if not tmp_node:
                    pnode = Node(values[idx], parent=pnode, all=tmp)
                else:
                    pnode = tmp_node
                idx += 1
                tmp = ','.join(values[0:idx + 1])

    logging.info(f'current tree\n{RenderTree(root, style=AsciiStyle()).by_attr()}')

    # add a 'path' column to the dataframe where we store the path up to the max depth
    # for example: 'action,indie,adventure,shooter' could become 'action,indie,adventure'
    # when our max depth value equals 3
    df['path'] = df[key].map(lambda x: ','.join(x[:maxdepth]))

    logging.info(f'calculating additional data for all leaf nodes ...')

    num_nodes = 1
    # iterate over nodes to find update their data
    for node in LevelOrderIter(root):

        # ignore the root node
        if not hasattr(node, 'all'):
            continue

        # for each leaf, add value data to them like the mean number of positive ratings
        filtered = df[df['path'] == node.all]

        if filtered.shape[0] > 0:
            for i in filtered["name"]:
                index = filtered[filtered["name"] == i].index.to_list()[0]
                Node(i, parent=node, value=str(filtered[value][index]))  # add value to the leaf

            logging.debug(f'... updated node {node.all}')

        num_nodes += 1

    # logging.info(f'final tree contains {num_nodes} nodes (including root)')
    # logging.info(f'current tree\n{RenderTree(root, style=AsciiStyle()).by_attr()}')

    return root


def make_hierarchy(df: pd.DataFrame, column: str, value: str, maxdepth: int = 3, datapath: str = None):
    """
    Creates a hierarchy from the given data frame, based on the given column.
    The resulting tree will be saved as a JSON file.

    Parameters:
        df (DataFrame): pandas dataframe holding the data
        column (str): the column name of the data to structure the tree by
        datapath (str): the path of the original data source
        maxdepth (int): the maximum depth of the tree

    Returns:
        None - if a datapath is given
        root (obj) - if no datapath is given, returns root node (anytree)
    """
    # make all list-like columns into actual lists
    df = common.make_lists(df.copy())

    logging.debug(f'creating hierarchy based on "{column}"')

    # create the hierarchy based on one of the list attributes
    # where the hierarchy represents, e.g. tags, in terms of their order in the list
    root = filter_list(df, column, value, maxdepth)

    if datapath is None:
        return root
    else:
        outpath = f'../public/data/{column}_{value}_{maxdepth}_hierarchy_try.json'

        export_hierarchy(outpath, root)
        # print(RenderTree(root))


if __name__ == "__main__":

    # define the arguments for this script
    parser = argparse.ArgumentParser()
    path_arg = parser.add_argument('datapath', help='path to the CSV dataset')
    path_arg.required = True
    attr_arg = parser.add_argument(
        'column',
        help='which column to make the hierarchy from',
        choices=['time'] + common.LIST_ATTRS
    )
    # add argument to choose parameters
    parser.add_argument(
        'value',
        help='which value to decide the size of node',
        choices=["average_playtime", "median_playtime", "positive_ratings"]
    )
    attr_arg.required = True
    parser.add_argument(
        '--maxdepth', '-d',
        type=int,
        help='maximum depth for the tree (ignored for "time"), default is 3',
        metavar='[d > 0]',
        default=3
    )
    parser.add_argument(
        '--loglevel', '-l',
        choices=['DEBUG', 'INFO', 'ERROR'],
        help='set the loggging level, default is INFO',
        default='INFO'
    )

    # parse command line arguments
    args = parser.parse_args()

    # get path of filtered data
    filtered_path = filter_csv(args.datapath)

    common.configure_logger(args.loglevel)

    # read the data file
    try:
        df = common.read_data(filtered_path)
        logging.info(f'loaded data from "{filtered_path}"')
        logging.debug(df)
    except ValueError as e:
        logging.error(e)
        exit(-1)

    make_hierarchy(df, args.column, args.value, max(1, args.maxdepth), filtered_path)
