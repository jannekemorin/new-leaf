# The Prolog graph should be a list of vertices in the vertex-[neighbors] pair form 
# See here for more documentation: https://www.swi-prolog.org/pldoc/man?predicate=reachable/3
import sys

def convert(fileName):
    # Create list of nodes
    node_list = []
    # Create list of neighbors for each node
    neighbor_list = []
    # Create variable for number of lines

    # Open the file
    file = open(fileName)
    lines = file.readlines()

    # Two cases: 
    # 1) The line instantiates a node
    index = 1
    if lines[0].rstrip() == "strict digraph \"\" {":
        index = 2
    for line in lines[index:]:
        if line.find("[") != -1:
            line_split = line.split("[")
            line_split[0] = line_split[0].strip()
            line_split[1] = line_split[1][:-3]
            node_list.append(line_split)

    # Create dictionary from node_list
    dict = {}
    for node in node_list:
        dict[node[0]] = node[1].split(":")[0][-1]
    all_values = dict.values()
    length = int(max(all_values))
    for i in range(length + 1): #+1 to account for the 0 start/stop lines
        neighbor_list.append([])

    #  2) The line instantiates an edge
    for line in lines[1:]:
        line_split = line.split()
        if ("->" in line_split and len(line_split) == 3):
            # Edges start at 0...
            node1 = int(dict[line_split[0]])
            node2 = int(dict[line_split[2][:-1]])  # the -1 removes the semicolon at the end...
            #print("node1orig", line_split[0], " node1: ", node1, "node2orig: ", line_split[2][:-1], "node2: ", node2)
            neighbor_list[node1].append(node2)

    # Format the output to a Prolog list
    # List of node-[neighbors]
    node_edge_list = []
    # for i in range(len(node_list)):
    #     print(node_list[i][0])
    #     print(str(dict[node_list[i][0]]))
    #     print(neighbor_list[i])
    #     print("---------------")
    #     node_edge_list.append(str(dict[node_list[i][0]]) + "-" + str(neighbor_list[i]))
    # prolog_graph = "[" + ', '.join(node_edge_list) + "]"

    for i in range(len(neighbor_list)):
        node_edge_list.append(str(i) + "-" + str(neighbor_list[i]))
    prolog_graph = "[" + ', '.join(node_edge_list) + "]"
        
    # Test statements to view the lists of nodes and neighbors
    #print(node_list)
    #print(neighbor_list)

    # # Write the Prolog list to a new file
    # outFile = open("prologOutput.pl", "w")
    # outFile.write(prolog_graph)
    # outFile.close()
    for i in range(length):
        print("reachable({0}, {1}, V).".format((i+1), prolog_graph))

