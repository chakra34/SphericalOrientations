# SphericalOrientations
Crystal directions to spherical angles

###########################################################################
# Machinery to convert orientation to spherical angles along with         #
# a discretization scheme                                                 #
#=========================================================================#
# Authors                                                                 #
# Aritra Chakraborty (chakra34@egr.msu.edu)                               #
# Philip Eisenlohr                                                        #
# DESCRIPTION                                                             #
#  Reading manual                                                         #
###########################################################################



#--- Prerequisites --#

Python 2.7.*          # The code is written in Python version 2.7

LaTeX to output images

Python web application "sketch" for drawing the corresponding unitcell (https://pypi.python.org/pypi/Sketch/0.2)

#------------------------#

Usage

"add_SphericalOrientations.py"

This code converts a given orientation into the spherical angles as explained in the text, and is based on Zambaldi, Claudio, et al. "Orientation informed nanoindentation of α-titanium: Indentation pileup in hexagonal metals deforming by prismatic slip." Journal of Materials Research 27.1 (2012): 356-367.
The exemplary Euler angles are also based on the mentioned paper.

syntax:

An example EulerAngles.txt file is given in the "example" directory with a set of Euler angles as:

2 header
Euler angles are taken from "Zambaldi, Claudio, et al. "Orientation informed nanoindentation of α-titanium: Indentation pileup in hexagonal metals deforming by prismatic slip. Journal of Materials Research 27.1 (2012): 356-367."
1_eulerangles 2_eulerangles 3_eulerangles
53.0 66.0 329.0
107.9 26.0 277.7
77.3 81.0 261.4
95.0 86.4 239.4
186.0 50.8 169.0
268.3 55.5 89.7


Nt: The file shows a format of a typical ASCII file with some 'header' and column labels.
The input file needs to be consistent with the prescribed format.

syntax: (starting in the 'examples' directory)

../Code/add_SphericalOrientations.py --symmetry hexagonal --eulers eulerangles --degrees EulerAngles.txt

Once the above command is executed the new 'EulerAngles.txt' file looks as follows:

3	header
Euler angles are taken from "Zambaldi, Claudio, et al. "Orientation informed nanoindentation of α-titanium: Indentation pileup in hexagonal metals deforming by prismatic slip. Journal of Materials Research 27.1 (2012): 356-367."
$Id: add_SphericalOrientations.py 61 2015-09-12 17:53:29Z chakra34 $	--symmetry hexagonal --eulers eulerangles --degrees
1_eulerangles	2_eulerangles	3_eulerangles	1_SphericalEulers	2_SphericalEulers	3_SphericalEulers
53.0	66.0	329.0	1.0	66.0	-142.0
107.9	26.0	277.7	52.3	26.0	-145.6
77.3	81.0	261.4	8.6	81.0	-158.7
95.0	86.4	239.4	30.6	86.4	-154.4
186.0	50.8	169.0	41.0	50.8	125.0
268.3	55.5	89.7	0.3	55.5	2.0

P.S. The last three spherical angles are consistent with Table II in the cited paper (Zambaldi et al. 2014).

#_____________________________________________________________________________________________________________#

"equidistant_SphericalTriangle.py"

The above code discretizes a given spherical triangle 

syntax ("examples" being the current working directory):

To see the help options enter:

../Code/equidistant_SphericalTriangle.py -h

Nt: The vertices of the spherical triangle (corresponding to crystal directions) have to be converted into Cartesian space and entered.
For example: When discretizing 'hexagonal' crystal directions the vertices for the standard stereographic triangle would be
"--p1 0.0 0.0 1.587 --p2 3.0 0.0 0.0 --p3 1.5 0.86667 0.0" corresponding to < 0, 0, 0, 1 >, < 2, -1, -1, 0> and < 1, 0, -1, 0 > Miller-Bravais indices respectively.

To generate examples/figures/equidistant_IPF_degree0.pdf 

enter the following:

../Code/equidistant_SphericalTriangle.py --sym cubic --p1 0.0 0.0 1.0 --p2 1.0 0.0 1.0 --p3 1.0 1.0 1.0 --degrees 0

To generate examples/figures/equidistant_IPF_degree1.pdf 

enter the following:

../Code/equidistant_SphericalTriangle.py --sym cubic --p1 0.0 0.0 1.0 --p2 1.0 0.0 1.0 --p3 1.0 1.0 1.0 --degrees 1

To generate examples/figures/equidistant_IPF_degree2.pdf 

enter the following:

../Code/equidistant_SphericalTriangle.py --sym cubic --p1 0.0 0.0 1.0 --p2 1.0 0.0 1.0 --p3 1.0 1.0 1.0 --degrees 2

Once either of the command is executed a directory named "equidistant" will be created in the current working directory.
Compile the "equidistant_IPF.tex" file to generate the figure.

P.S. LaTeX is a prerequisite for this.

To generate examples/figures/example_hexagonal_unitcell.pdf

execute the following:

../Code/equidistant_SphericalTriangle.py --symm hexagonal --p1 0.0 0.0 1.0 --p2 1.0 0. 0. --p3 1.5 0.8667 0.0 --degrees 2 --unitcell

and compile the "equidistant_IPF.tex" file generated in the newly created folder "equidistant"

P.S. LaTeX and sketch are prerequisites for this.


Nt: The utility functions are all obtained from "https://damask.mpie.de" which provides a wonderful package to perform
crystal plasticity simulations along with various built in pre and post processing scripts.



