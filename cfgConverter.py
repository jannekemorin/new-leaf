import networkx as nx
from networkx.algorithms.community.centrality import girvan_newman
from networkx import edge_betweenness_centrality as betweenness
import community as community_louvain
import matplotlib.pyplot as plt
from networkx.generators.duplication import partial_duplication_graph
'''
Helper program which converts control flow graph files produced by pycfg to Prolog or Python graphs
and returns pertinent fault localization information.

Code for coloring nodes based on community was inspired by:
https://stackoverflow.com/questions/50828284/networkx-specifying-colors-to-communities-nodes-in-a-graph
'''

def convert2Prolog(fileName):
    '''
    Convert2Prolog returns a list of Prolog reachability queries which tell us how nodes (statements)
    are connected. The Prolog graph used to produced these queries should be a list of vertices in 
    the vertex-[neighbors] pair form. See here for more documentation: 
    https://www.swi-prolog.org/pldoc/man?predicate=reachable/3
    '''
    #--------------------------------------------------------------------
    # Create list of nodes
    nodeList = []
    # Create list of neighbors for each node
    neighborList = []
    # Create variable for number of lines

    #--------------------------------------------------------------------
    # Open the file
    file = open("cfgs/text/" + fileName.split(".")[0] + ".txt")
    lines = file.readlines()

    #--------------------------------------------------------------------
    # Get the length (number of lines) of the original program
    faultyProgram = open("testFiles/" + fileName)
    length = 0
    for line in faultyProgram.readlines():
        if len(line.strip()) != 0:
            length += 1

    #--------------------------------------------------------------------
    # Address each line appropriately for the matching case:
    # 1) The line instantiates a node
    index = 1
    if lines[0].rstrip() == "strict digraph \"\" {":
        index = 3
    for line in lines[index:]:
        if line.find("[") != -1:
            line_split = line.split("[")
            line_split[0] = line_split[0].strip()
            line_split[1] = line_split[1][:-3]
            nodeList.append(line_split)

    # Create dictionary from nodeList
    dict = {}
    for node in nodeList:
        dict[node[0]] = node[1].split(":")[0][-1]
    all_values = dict.values()
    for i in range(length + 1): #+1 to account for the 0 start/stop lines
        neighborList.append([])

    #--------------------------------------------------------------------
    #  2) The line instantiates an edge
    for line in lines[1:]:
        line_split = line.split()
        if ("->" in line_split and len(line_split) == 3):
            # Edges start at 0...
            node1 = int(dict[line_split[0]])
            node2 = int(dict[line_split[2][:-1]])  # the -1 removes the semicolon at the end...
            neighborList[node1].append(node2)

   #--------------------------------------------------------------------
   # Create a list which will hold a string representation of each node-[its neighbors]
    node_edge_list = []
    for i in range(1, length + 1):
        node_edge_list.append(str(i) + "-" + str(neighborList[i]))
    prolog_graph = "[" + ', '.join(node_edge_list) + "]"
    
    #--------------------------------------------------------------------
    # Create a list of Prolog queries to return
    returnList = []
    for i in range(length):
        returnList.append("reachable({0}, {1}, V).".format((i+1), prolog_graph))
    return returnList



def convert2Python(fileName, suspiciousnessList):
    '''
    Convert2Python creates a networkx Python graph and returns its fault localization information such
    as communities.
    '''
    #--------------------------------------------------------------------
    # Create list of nodes
    nodeList = []
    # Create list of neighbors for each node
    neighborList = []
    # Create variable for number of lines

    #--------------------------------------------------------------------
    # Open the file
    file = open("cfgs/text/" + fileName.split(".")[0] + ".txt")
    lines = file.readlines()

    #--------------------------------------------------------------------
    # Get the length (number of lines) of the original program
    faultyProgram = open("testFiles/" + fileName)
    length = 0
    for line in faultyProgram.readlines():
        if len(line.strip()) != 0:
            length += 1

    #--------------------------------------------------------------------
    # Address each line appropriately for the matching case:
    # 1) The line instantiates a node
    index = 1
    if lines[0].rstrip() == "strict digraph \"\" {":
        index = 3
    for line in lines[index:]:
        if line.find("[") != -1:
            line_split = line.split("[")
            line_split[0] = line_split[0].strip()
            line_split[1] = line_split[1][:-3]
            nodeList.append(line_split)

    # Create dictionary from nodeList
    dict = {}
    for node in nodeList:
        dict[node[0]] = node[1].split(":")[0][-1]
    all_values = dict.values()
    for i in range(length + 1): #+1 to account for the 0 start/stop lines
        neighborList.append([])

    #--------------------------------------------------------------------
    #  2) The line instantiates an edge
    for line in lines[1:]:
        line_split = line.split()
        if ("->" in line_split and len(line_split) == 3):
            # Edges start at 0...
            node1 = int(dict[line_split[0]])
            node2 = int(dict[line_split[2][:-1]])  # the -1 removes the semicolon at the end...
            neighborList[node1].append(node2)

    #--------------------------------------------------------------------
    # Format the output to a Python graph
    G = nx.DiGraph()
    node_edge_list = []
    for i in range(1, length + 1):
        G.add_nodes_from([(i, {"Suspiciousness": suspiciousnessList[i-1]})])
    for i in range(1, length + 1):
        for j in range(len(neighborList[i])):
            G.add_edge(i, neighborList[i][j])

    #--------------------------------------------------------------------
    # Output the lists of nodes and neighbors
    print("Nodes: ", list(G.nodes))
    print("Edges: ", list(G.edges))

    #--------------------------------------------------------------------
    # Weight edges based on the first node in the directed Edge
    F = nx.DiGraph()
    F.add_nodes_from(G)
    print("Edges with weights attached: ")
    finalEdges = []
    for i in list(G.edges):
        print(i + (suspiciousnessList[i[0]-1],))
        finalEdges.append(i + (suspiciousnessList[i[0]-1],))
    F.add_weighted_edges_from(finalEdges)

    #--------------------------------------------------------------------
    # Print ranked suspiciousness list
    print("Ranked suspiciousness list: ")
    lineScoreList = []
    for i in range(len(suspiciousnessList)):
        lineScoreList.append([i + 1, suspiciousnessList[i]])
    lineScoreList.sort(reverse=True, key=lambda x: x[1])
    for i in range(len(lineScoreList)):
        print("Line: " + str(lineScoreList[i][0]) + ", " + str(lineScoreList[i][1]))

    #--------------------------------------------------------------------
    # Output Girvan Newman communities
    # Incorporates edge weights when choosing the edge with the highest betweenness centrality
    def most_central_edge(G):
        centrality = betweenness(G, weight="weight")
        return max(centrality, key=centrality.get)
    communities = girvan_newman(F, most_valuable_edge=most_central_edge)
    print("\nGirvan Newman Communities: ")
    # Fix positions for each node
    pos = nx.spring_layout(F) 
    # Draw the initial graph
    nx.draw(F, pos, edge_color='k',  with_labels=True,
            font_weight='light', node_size= 280, width= 0.9)
    # Draw the nodes of each community with a new color
    i = 0
    colorList = ['y', 'r', 'g']
    for lst in tuple(sorted(c) for c in next(communities)):
        print(lst)
        nx.draw_networkx_nodes(F, pos, nodelist=lst, node_color=colorList[i])
        i += 1
    plt.show()

    #--------------------------------------------------------------------
    # Output Louvain communities
    # We need to convert the directed graph to an undirected graph to do so...
    U = F.to_undirected()

    # Build a list of communities
    #print("U: " + str(U.get_edge_data(2, 5)))
    partition = community_louvain.best_partition(U)
    communityList = []
    count = 0
    for com in set(partition.values()) :
        count = count + 1.
        listNodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
        communityList.append(listNodes)
    print("\nLouvain Communities:")
    # Fix positions for each node
    pos = nx.spring_layout(F) 
    # Draw the initial graph
    nx.draw(F, pos, edge_color='k',  with_labels=True,
            font_weight='light', node_size= 280, width= 0.9)
    # Draw the nodes of each community with a new color
    i = 0
    colorList = ['y', 'r', 'g']
    for lst in communityList:
        print(lst)
        nx.draw_networkx_nodes(F, pos, nodelist=lst, node_color=colorList[i])
        i += 1
    plt.show()