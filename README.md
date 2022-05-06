# README #


### What is this repository for? ###

* This package aims to draw efficient voting districts using voronoi diagrams.
Polling locations are input as coordinates, and the program will create a 
Voronoi diagram of the points using Fortune's sweep algorithm and stored
as a Doubly Connected Edge List (DCEL).

* Version: 1.0

### How do I get set up? ###

* For a quick demo, run fortune/algorithm/fortune.py module. Choose either random data or 
Wabasha County polling location data to run on.

* Packages used: Numpy, Math, Bisect (For O(log(n)) lookup in ordered list).

* Data is a set of points hard coded into the fortune.py module.

* Each module  in the package can be individually run to execute a series of tests.


### Who do I talk to? ###

* Daniel Grange: daniel.grange@stonybrook.edu
