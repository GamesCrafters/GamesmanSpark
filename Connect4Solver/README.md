# README for C4 Spark Solver

As of right now, the specifications for connect 4 live within `connect4.py`, which include `WIDTH`, `HEIGHT`, and `WIN_NUMBER` - the number of consecutive pieces one needs to win. 

This class can benefit from using C code to run instead of pure Python. A potential future project one should look into is rewriting the description in C, and using a library to allow PySpark to interact with this more efficient code. One I was looking into is called `pybind11`. An example of how it should work is in `connect4.cpp`.

The solver itself should work locally, if you have Spark and any other necessary requirements installed. You can run it by running the Python file with two additional arguments: the number of output files you want, and the path to the desired output directory (should not exist already). E.g. `python3 C4SparkSolver.py 10 Results/C4`

To actually run it, I created a cluster on Google Dataproc, with one master and N worker nodes, you can choose specific settings as you see fit. You should also create a bucket for storage, and upload both the `C4SparkSolver.py` and `connect4.py` files there. Then you can simply create a job on that cluster with the location of the solver as the main file, and the location of the game as an addition file. You can also add the arguments (output directory can also be a new location within your bucket storage).

A future project for the solver is optimizing its use of data. As of right now, its storing human-readable data, but should really be storing an integer that encodes all the information (board-state, depth, value, and remoteness). It should only store this type in the RDDs for space/networking costs, and should convert between this form and current form before being processed by the game class. 

