# Sail Away!
![](images/P1090489.jpg)

By **Daniel Kristiyanto**

*Seattle. Summmer, 2016*


Language: Python 3.5

Required packages: `os`, `sys`, `json`, `datetime`, `collections`

# Challenge Summary

This challenge requires participats to:

> Use Venmo payments that stream in to build a graph of users and their relationship with one another.

> Calculate the median degree of a vertex in a graph and update this each time a new Venmo payment appears. You will be calculating the median degree across a 60-second sliding window.

> The vertices on the graph represent Venmo users and whenever one user pays another user, an edge is formed between the two users.


# Rules and Guideliness

The pipelines will process the input file, compute the median and dump it in a file. Following rules is expected by the coordinator:

#### May I use R or other analytics programming languages to solve the challenge?
Python is used for this challange. The code was tested for both Python 2.7 and Python 3.5. However, Python 3.5 is prefered.

#### What sort of system should I use to run my program on (Windows, Linux, Mac)?
It was written in MacOS environtment and should work in Linux. A Docker container for this submission is also available (more information below).

#### Can I use pre-built packages, modules, or libraries?
No "exotic" packages was used. A minimal and Python standard packages are used (e.g `json`, `datetime`).

#### Will you email me if my code doesn't run?
The codes were tested using the provided script. Additionally, a Docker container with the exact environtment is also available.

#### Do I need to update the median when the next payment in the file falls outside the 60-second window?
Any new payments with timestamps > than current maximum timestamps or 60s before current maximum timestamps are accepted. 

#### Should the 60-second window be inclusive or exclusive? 
Exclusive is used. New payment must be > ( current max timestamps - 60s)

#### Should my graph contain disconnected nodes?
The graph is pruned everytime the egdes are updated.

####  Should I check if the files in the input directory are text files or non-text files(binary)?
Only text files with the same format with given input file is accepted.

#### If there are multiple payments within a 60-second window from the same two users, should they be connected twice?
In this case, the script does not add a new egde; however, it does update the egdes if it's more recent, then followed by pruning procedures and computing the (possibly) new median.


# Input and Output

For this challenge, the input a `.txt` file containing at least three information: `actor`, `target` and `created_time` in a json format.

The output is a `.txt` file with each row is the median for every state of the transaction in the input file. 

Generally, to run the script:
```
python rolling_median.py input.txt output.txt 

```

To generate a detailed log file, use verbose. The produced logfile is generally large, and may significantly slow down the process. 

```
python rolling_median.py input.txt output.txt logfile.txt

```

# Design

### Algorithm
By analysing the given sample file, the expected graphs are less likely dense (each vertex usually only connected with few other vertex). For this approach, adjency list is a better approach (less space complexity and portentially less time complexity) than other approaches such as adjency matrix.

### Data Structure
Relatively simple object oriented designs, supported by dictionaries and tuples, are mainly used. This consideration was chosen given that a large (but skinny) data is expected. A relatively simple changes can be added should the data structure changes without sacrifying the performance.

### Time Complexity

Putting aside of the time complexity for Python built-in processes (e.g `dictionary.remove()`, or `sort()`), the time complexity for this approach is O(|V|+|E|).
Here's the detail:

Time | Procedures | Sub Procedures
--- | --- | ---
1   | Add a new node (actor) | 
    | Add an egde to target | 
1   | | Check if actor exists  
1   | | Check timestamps
V+E | | Check / update existing transaction
1   | | Add egde 
V   | Update maximum timestamps |
E   | Prune egdes |
V   | Prune vertex |
    | Update median |
V+E | | Collect/iterate through graph 
1   | | Compute median 

Total = V+E + 2V + E + V+E = 4V+3E = V+E

# Docker Package

This submission is also available as a Docker package.

On docker-enabled infrastructures run:

```
docker run -v /Users/path/to/files:/data kristiyanto/orinocoflow 
```

The container will process any txt files found in the mounted directory and produce an output with suffix `.OUT` in the same directory, and exit when finished. 

Alternatively, container can also be run in an interactive mode:

```
docker run -v /Users/path/to/files:/data -ti kristiyanto/orinocoflow
```
The original directory structures can be found in `/insight` folder inside the container.

