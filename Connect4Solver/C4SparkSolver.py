from pyspark import SparkContext
from pyspark import StorageLevel
import connect4 as c4
import sys

NUMBER_OUTPUT_FILES = int(sys.argv[1])
EXPORT_FOLDER = sys.argv[2]

LINE_BREAK = '---------------------------------------------------------------\n\n'

""" The following functions are helper functions which allow us abstract away
the parsing of various information from the values in our RDD """

def get_position(value):
    return value[0]

def get_depth(value):
    if type(value[1]) is tuple:
        return value[1][0]
    return value[1]

# Can only be used for a solved state
def get_outcome(value):
    return value[1][1]

# Can only be used for a solved state
def get_remoteness(value):
    return value[1][2]

# Can only be used for a solved state
def is_primitive(value):
    return type(value[1]) is tuple and value[1][2] == 0

# Flips the value of the outcome between win and loss, keeps tie the same
def flip(outcome):
    if outcome == module.WIN:
        return module.LOSE
    if outcome == module.LOSE:
        return module.WIN
    return outcome

def zip_values(value_list):
    return zip(*value_list)

"""
Using BFS to map down the game tree and collect all the primitives.
It does this by branching to each of the possible moves from a given position.

Unsolved values = (board_state, depth)
Primitive values = (board_state, (depth, value, remoteness))
"""
def bfs_map(value):
    position = get_position(value)
    depth = get_depth(value)
    if module.is_primitive(position):
        return [ tuple([position, (depth, module.primitive(position), 0)]) ]

    else: 
        next_states = [module.do_move(list(position), move) for move in module.generate_moves(position)]
        return [ tuple([tuple(next), depth+1]) for next in next_states ]


"""
The following 'trace_back_up' functions assign final outcomes and remoteness for each position.
Solved values = (board_state, (depth, outcome, remoteness))
"""

""" 
This function cleverly uses the undo move feature to figure out what possible positions
could have been parents to the position we are inspecting, to create a parent-child relationship.
"""
def trace_back_up_map(value):
    position = get_position(value)
    parents = module.undo_move(list(position))

    parent_details = [get_depth(value) - 1, flip(get_outcome(value)), get_remoteness(value) + 1]

    return [tuple([tuple(p), tuple(parent_details)]) for p in parents]

""" 
We have a parent state with all the children information zipped up, which we can
use to determine the outcome, and using the outcome we can then determine the remoteness.
"""
def trace_back_up_combine(value):
    children_information = list(value[1])
    depth = children_information[0][0]
    outcome = determine_outcome(children_information[1])
    remoteness = 0
    if outcome == module.LOSE:
        remoteness = max(children_information[2])
    else:
        remoteness = min(children_information[2])

    return (value[0], (depth, outcome, remoteness))

"""
Helper function for trace_back_up_combine, which takes a list of child outcomes 
and determines the parent outcome value.
"""
def determine_outcome(move_values):
    #If any winning moves, outcome is win
    if module.WIN in move_values:
        return module.WIN

    #If all losing moves, outcome is loss
    if all(m == module.LOSE for m in move_values):
        return module.LOSE

    #Else there must be a mixture of lose/tie, outcome is tie
    return module.TIE

# Used after the entire solving process, only for small RDDs.
def print_to_file(rdd, fName):
    output_file = open(fName, "w")
    writer = lambda line: output_file.write(str(line) + "\n")
    compiled = rdd.collect()

    for elem in compiled:
        writer(elem)

""" 
Instead of grouping by key and then zipping, we will use this to reduce by key
while achieving a similar result. 
"""
def trace_back_up_experimental(value1, value2):
    return tuple([value1[0], extend_tuples(value1[1], value2[1]), extend_tuples(value1[2], value2[2])])

# Helper function to convert both tuple and non-tuple to a list
def list_format(x):
    if type(x) is tuple:
        x = list(x)
    else:
        x = [x]
    
    return x

# Helper - like list.extend() but for tuples/non-tuples
def extend_tuples(a, b):
    a = list_format(a)
    b = list_format(b)
    a.extend(b)
    return tuple(a)

""" 
Experimental methods to see if we can improve performance by not using groupByKey()
"""
def trace_back_up_combine_experimental(value):
    children_information = list(value[1])
    depth = children_information[0]
    outcome = determine_outcome(list_format(children_information[1]))
    remoteness = 0
    if type(children_information[2]) is int:
        remoteness = children_information[2]
    else:
        if outcome == module.LOSE:
            remoteness = max(children_information[2])
        else:
            remoteness = min(children_information[2])

    return (value[0], (depth, outcome, remoteness))
    

# Main function, all the Spark logic is here
def main():

    # Current board level, we use this while tracing back up
    board_level = 0

    # Module of game we are playing
    global module
    module = c4

    # Remoteness to primitive position
    remoteness = 0

    print('Solving Connect 4 - Width: {}, Height: {}, Win: {}'.format(module.WIDTH, module.HEIGHT, module.WIN_NUMBER))
    print(LINE_BREAK)

    # Use this for local testing
    # sc = SparkContext("local", "C4Spark")

    sc = SparkContext()
    sc.setLogLevel('ERROR')

    blank_board = module.init_board()

    rdd = sc.parallelize([(tuple(blank_board), board_level)])
    primitives = sc.parallelize([])
    all_solved = sc.parallelize([])

    max_board_level = -1
    while not rdd.isEmpty():
        max_board_level += 1
        
        print('LEVEL ' + str(max_board_level) + ' Mapping down game tree')
        print(LINE_BREAK)
        
        rdd = rdd.flatMap(bfs_map).distinct().cache()

        primitives = rdd.filter(is_primitive).union(primitives)
        next_rdd = rdd.filter(lambda x : not is_primitive(x))
        rdd.unpersist()
        rdd = next_rdd


    print('All primitives calculated. Starting trace back up')
    print(LINE_BREAK)
    
    all_solved.persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
    all_solved = all_solved.union(primitives)

    # Put max level primitives back in RDD
    rdd = primitives.filter(lambda x: get_depth(x) == max_board_level)

    board_level = max_board_level
    while board_level > 0:
        # Classic set
        # rdd = rdd.flatMap(trace_back_up_map).distinct().groupByKey().mapValues(zip_values)
        # rdd = rdd.map(trace_back_up_combine).cache()

        # Experimental set
        rdd = rdd.flatMap(trace_back_up_map).distinct().reduceByKey(trace_back_up_experimental)
        rdd = rdd.map(trace_back_up_combine_experimental).cache()

        #Add to our collection of solved states
        all_solved = rdd.union(all_solved)

        print('LEVEL ' + str(board_level) + ' complete, starting next iteration')
        print(LINE_BREAK)

        #Update for next iteration
        board_level -= 1

        # This line is unnecessary because each entry should be mapped to following tier
        # rdd = rdd.filter(lambda x: get_depth(x) == board_level)

        next_rdd = primitives.filter(lambda x: get_depth(x) == board_level).union(rdd)
        rdd.unpersist()
        rdd = next_rdd
    
    print('DONE')
    print(LINE_BREAK)

    # all_solved = all_solved.sortBy(get_depth)

    # Use this only for small datasets, because it collects data
    # print_to_file(all_solved, "Results/C4_FinalMappingOutput.txt")

    all_solved.coalesce(NUMBER_OUTPUT_FILES).saveAsTextFile(EXPORT_FOLDER)

    print('OUTPUT COMPLETE')
    print(LINE_BREAK)


if __name__ == "__main__":
    main()
