import numpy as np

from sklearn.preprocessing import StandardScaler

import matplotlib.colors
import pandas as pd


def get_cols_by_type():
    '''
        Function to get different columns
        Input:
        Output:
            Tuple of lists of
            1. columns with numerical values,
            2. columns with general information,
            3. columns related to presidential election
    '''
    num_cols = ['Personal income (thousands of dollars)',
                'Net earnings by place of residence',
                'Personal current transfer receipts',
                'Income maintenance benefits',
                'Unemployment insurance compensation',
                'Retirement and other',
                'Dividends, interest, and rent',
                'Population (persons)',
                'Per capita personal income',
                'Per capita net earnings',
                'Per capita personal current transfer receipts',
                'Per capita income maintenance benefits',
                'Per capita unemployment insurance compensation',
                'Per capita retirement and other',
                'Per capita dividends, interest, and rent',
                'Earnings by place of work',
                'Wages and salaries',
                'Supplements to wages and salaries',
                'Employer contributions for employee pension and ' +
                'insurance funds',
                'Employer contributions for government social insurance',
                "Proprietors' income",
                "Farm proprietors' income",
                "Nonfarm proprietors' income",
                'Total employment (number of jobs)',
                'Wage and salary employment',
                'Proprietors employment',
                'Farm proprietors employment',
                'Nonfarm proprietors employment',
                'Average earnings per job (dollars)',
                'Average wages and salaries',
                "Average nonfarm proprietors' income"]

    info_cols = ['year', 'state', 'county', 'fips', 'pres']

    elec_cols = ['republican', 'democrat', 'total_votes', 'n_electors',
                 'winner']

    return num_cols, info_cols, elec_cols


def get_cols_for_mapper():
    '''
        Function to return columns used for Mapper Algorithm. Columns to use
        for the mapper were found by comparing the distribution of each column
        between the different election years. The ones differing throughout the
        years are selected (selection was made by eye)
        Input:
        Output:
            List of columns used for Mapper algorithm
    '''
    return ['Personal income (thousands of dollars)',
            'Net earnings by place of residence',
            'Income maintenance benefits',
            'Unemployment insurance compensation',
            'Per capita personal income',
            'Per capita net earnings',
            'Per capita personal current transfer receipts',
            'Per capita income maintenance benefits',
            'Per capita unemployment insurance compensation',
            'Per capita retirement and other',
            'Per capita dividends, interest, and rent',
            'Earnings by place of work',
            "Proprietors' income",
            "Nonfarm proprietors' income",
            'Total employment (number of jobs)',
            'Proprietors employment',
            'Farm proprietors employment',
            'Nonfarm proprietors employment',
            'Average earnings per job (dollars)',
            'Average wages and salaries',
            "Average nonfarm proprietors' income"]


def get_data(df):
    '''
        Function to extract data for Mapper from data frame.
        Input:
            df: Pandas data frame containing
        Output:
            Scaled relevant data values (ndarray)
    '''
    data_cols = get_cols_for_mapper()

    # perform a log transformation on the data
    df[data_cols] = (df[data_cols] +
                     abs(df[data_cols].min().min()) + 1).apply(np.log)

    # scale data to have zero mean and a standard deviation of one
    scaler = StandardScaler()
    df[data_cols] = scaler.fit_transform(df[data_cols])

    return df[data_cols].values


def split_data_by_year(data, df):
    '''
        Function to split entire data into different election years.
        Input:
            data: Mapper input (ndarray)
            df: Pandas data frame of entire data
        Output:
            dictionary with election year as key and corresponding economic
            data as values
    '''
    return dict(zip(['2000', '2004', '2008', '2012', '2016'],
                map(lambda x: data[x, :],
                    map(lambda x: df[df['year'] == x].index,
                        df['year'].unique()))))


def filter_2d_trafo(x):
    '''
        Transformation of PCA values to obtain final filter.
        Input:
            x: Filter values (ndarray)
        Output:
            Transformed PCA (ndarray)
    '''
    x[:, 0] = np.log(x[:, 0] - min(x[:, 0]) + 1)
    x[:, 1] = np.log(np.abs(x[:, 1]) + 1)
    return x


# for plotting
def get_node_size(node_elements):
    '''
        Function to get node size
        Input:
            node_elements: List/tuple containing, for each node, a list like
                information on all data points belonging to node
        Output:
            List of node sizes
    '''
    return list(map(len, node_elements))


def get_node_summary(node_elements, data, summary_stat=np.mean):
    '''
        Function to calculate a summary statistic per node
        Input:
            node_elements: List/tuple containing, for each node, a list like
                information on all data points belonging to node
            data: Data to be used (ndarray)
            summary_stat: Summary statistic (default: np.mean)
        Output:
            List of summary statistics
    '''
    return list(map(lambda x: summary_stat(data[x]),
                    node_elements))


def get_n_electors(node_elements, n_electors):
    '''
        Function to calculate percentage of electors belonging to each node
        Input:
            node_elements: List/tuple containing, for each node, a list like
                information on all data points belonging to node
            n_electors: Pandas series of number of weighted electors per
                county
        Output:
            List of percentage of electors within a node(w.r.t to total number
            of electors)
    '''
    return [100 * n_electors.iloc[x].sum() / n_electors.sum()
            for x in node_elements]


def get_node_text(node_elements, n_electors, node_color, label):
    '''
        Function to create text of node label
        Input:
            node_elements: List/tuple containing, for each node, a list like
                information on all data points belonging to node
            n_electors: Pandas series of number of weighted electors per
                county
            node_color: List of node colors
            label: Name of label (e.g. 'income') (str)
        Output:
            List of text for node labels
    '''
    return [f'Node Id: {x[0]}<br>' +
            f'Node size: {len(x[1])}<br>' +
            f'Percentage of Weighted Electors: {round(y, 2)}<br>' +
            f'Percentage of Weighted Electors per County: '
            f'{round(y / len(x[1]), 3)}<br>' +
            f'Mean {label}: {z}'
            for x, y, z in zip(node_elements.items(), n_electors, node_color)]


def get_subgraph(graph, vertices_to_remove):
    '''
        Extract a subgraph out of a given one.
        Input:
            graph: igraph object
            vertices_to_remove: List of vertices (defined by node id) to
                remove from graph
        Output:
            An igraph object containing all but specified vertices (and
            corresponding edges)
    '''
    subgraph = graph.copy()
    subgraph.delete_vertices(vertices_to_remove)

    return subgraph


def get_county_plot_data(graph, df, col, cmap):
    '''
        Function to create data for a plot of a map of the US.
        Input:
            graph: igraph object
            df: Pandas dataframe
            col: Column to base color of map on
            cmap: Colormap
        Output:
            tuple of list of color of a node (numerical value) and list of
            colors to use
    '''
    map_col = (pd.DataFrame(np.zeros((df.shape[0],
                                      2)),
                            columns=['color_sum', 'n_counties'])
               .astype({'n_counties': 'int'}))

    for rows, val in zip(graph['node_metadata']['node_elements'],
                         get_node_summary(graph['node_metadata']
                                          ['node_elements'],
                                          df[col])):
        map_col.loc[rows] = map_col.loc[rows] + [val, 1]

    colors = list(map(matplotlib.colors.rgb2hex,
                      cmap((map_col['color_sum'] /
                            map_col['n_counties']).sort_values().unique()
                           .tolist())[:, :3]))

    return ((map_col['color_sum'] / map_col['n_counties']).tolist(),
            colors)


def get_regions():
    '''
        Function to get different regions
        Input:
        Output:
            Dictionary with region id as key and sets of node ids belonging to
            them
    '''
    return {
        0: {45, 18, 1, 7, 52, 55, 50, 49, 46, 51, 47, 30, 2, 44,
            37, 54, 53, 9, 48, 13, 24},
        1: {41, 42, 43},
        2: {38, 39, 40},
        3: {25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36},
        4: {14, 15, 16, 17, 19, 20, 21, 22, 23},
        5: {0, 3, 4, 5, 6, 8, 10, 11, 12}
    }


def get_data_per_region(regions, node_elements):
    '''
        Function to assign to each region the data points enclosed in it.
        Input:
            regions: Dictionary of regions with ids as keys and set of nodes
                as values
            node_elements: List/tuple of data points per node
        Output:
            Dictionary with region ids as keys and corresponding data point ids
            as values
    '''
    # create tuples of region id with corresponding data points. The latter are
    # found by taking the union of all elements belonging to a region.
    return dict((region_id, set.union(*[set(node_elements[node])
                                        for node in regions[region_id]]))
                for region_id in regions.keys())


def hex2rgb(hex_colors):
    '''
        Function to convert a hexa coded color into RGB format.
        Input:
            hex_colors: List of hexa color codes of the format '#xxyyzz'
        Output:
            List of tuples representing RGB codes
    '''
    rgb_colors = [color.lstrip('#') for color in hex_colors]
    return [tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            for color in rgb_colors]


def mean_rgb(rgb_vals):
    '''
        Function to find the elementwise mean of a list of tuples.
        Input:
            rgb_vals: List of tuples of same length
        Output:
            Tuple containing the mean along of each entry
    '''
    # calculate mean of list of rbg values
    return tuple(map(int, np.mean(rgb_vals, axis=0)))


def get_small_cluster_ids():
    '''
        Function the get ids of singletons/small clusters.
        Input:
        Output:
            List of node ids of singletons/small clusters
    '''
    return [45, 18, 1, 7, 52, 55, 50, 49, 46, 51, 47, 30, 2, 44, 37, 54, 53, 9,
            48, 13, 24]
