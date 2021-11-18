# new-leaf
A new beginning!

### Dependencies
* Please utilize the following commands for dependency installations:
  * pip install networkx
  * pip install community
  * pip install astunparse
  * pip install python-louvain
  * pip install --upgrade decorator==5.0.9
  * pip install pyswip
  * pip install pycfg
  * conda install -c alubbock pygraphviz
  * dot -c
  
* You will also need to download the following applications:
  * Anaconda
  * Visual Studio C++ Tools
  * SWI-Prolog
    * Be sure the version (64-bit versus 32-bit) matches your Python installation
    * Be sure to add swipl/bin to your path
  
### Directions
1. Place the program you would like to test in the testFiles folder
2. Place your test case inputs (in the form of a function call) in the testCases/inputs folder. Use the naming convention "input_(three-digit-representation-of-number).txt"
  * Example: input_001.txt
3. Place your test case expected outputs in the testCases/expectedOutputs folder. Use the naming convention "output_(three-digit-representation-of-number).txt"
  * Example: output_001.txt
  * The input and expected output files should be linked by their test case number
4. Run "python testDriver.py" from the new-leaf folder. Then input the name of the program you would like to test and the name of the function when prompted
