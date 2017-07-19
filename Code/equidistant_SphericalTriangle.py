#!/usr/bin/env python

###########################################################################
# Authors                                                                 #
# Aritra Chakraborty                                                      #
# Philip Eisenlohr                                                        #
###########################################################################

import os,sys,Spherical
import string
from optparse import OptionParser
import numpy as np
from subprocess import call
import math

global listAngles
listAngles = []

global listCoords
listCoords = []

scriptID   = string.replace('$Id: equidistant_SphericalTriangle.py 476 2017-06-15 15:22:25Z chakra34 $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]


parser = OptionParser(option_class=Spherical.extendableOption, usage='%prog options [file[s]]', description = """
Discretizes a spherical triangle equally based on degrees of runs.

""", version = scriptID)

parser.add_option('--degrees',
                  dest = 'degrees',
                  type = 'int',
                  help = 'number of times discretizations to be done [3]')

parser.add_option('--symm',
                  dest = 'symmetry',
                  type = 'string',
                  help = 'symmetry [cubic]')

parser.add_option("--unitcell",  action="store_true",
                  dest="unitcell",
                  help="unitcell or not [False]")

parser.add_option("--eulers",  action="store_true",
                  dest="eulers",
                  help="prints out the discretized Euler angles in Bunge convention [False]")

parser.add_option('--p1',
                  dest = 'point1',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'first point in the spherical triangle to be discretized [%default]')

parser.add_option('--p2',
                  dest = 'point2',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'second point in the spherical triangle to be discretized [%default]')

parser.add_option('--p3',
                  dest = 'point3',
                  type = 'float', nargs = 3, metavar = 'float float float',
                  help = 'third point in the spherical triangle to be discretized [%default]')

parser.add_option(      '--root',
                  dest = 'root',
                  type = 'string', metavar = 'string',
                  help = ' desired root of this process ')

parser.set_defaults(degrees       = 3,
                    symmetry    = 'cubic',
                    unitcell    = False,
                    eulers      = False,
                    point1      = [0., 0., 1.],
                    point2      = [1., 0., 1.],
                    point3      = [1., 1., 1.],
                   )

(options,filenames) = parser.parse_args()
options.root = os.path.dirname(os.path.realpath(__file__)) if options.root == None else options.root

options.point1 = np.array(options.point1)/np.linalg.norm(options.point1)
options.point2 = np.array(options.point2)/np.linalg.norm(options.point2)
options.point3 = np.array(options.point3)/np.linalg.norm(options.point3)


#----------------------------------------------#
def generate_tex_cubic(section):

  if section == 'header' :
   return'\n'.join(['\\documentclass{article}',
                    '\\usepackage{tikz}\n',
                    '\\graphicspath{{../}{./}}'
                    '\\usetikzlibrary{shapes,arrows}\n',
                    '\\usepackage{miller}\n',
                    '\\usepackage[graphics, active, tightpage]{preview}\n',
                    '\\PreviewEnvironment{tikzpicture}\n',
                    '\\begin{document}\n',
                    '\\thispagestyle{empty}\n',
                    '\\begin{tikzpicture}',
                    '\\begin{scope}[x=19.313708cm,y=19.313708cm]',
                    '\\draw[line width=1.0pt] (0,0) -- (0.414,0);',
#                    '\\draw[line width=1.0pt] (0,0) -- (0.0,0.414);',
                    '\\draw[line width=1.0pt, domain=0:15] plot ({-1 + sqrt(2)*cos(\\x)}, {sqrt(2)*sin(\\x)});',
#                    '\\draw[line width=1.0pt, domain=75:90] plot ({ sqrt(2)*cos(\\x)}, {-1 + sqrt(2)*sin(\\x)});',
                    '\\draw[line width=1.0pt] (0,0) -- (0.366,0.366);',
                    '\\begin{scope}[inner sep=0pt]',
                    '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<001>}] at (0.000000,0.000000) {};',
                    '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<101>}] at (0.414,0.000000) {};',
#                    '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<011>}] at (0.0,0.414) {};',
                    '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<111>}] at (0.366,0.366) {};',
                    '\\end{scope}\n',
                    '\\begin{scope}[inner sep=1.0pt]\n'])
  elif section == 'footer' :
   return'\n'.join(['\\end{scope}\n',
                    '\\end{scope}',
                    '\\end{tikzpicture}',
                    '\\end{document}'])

def generate_tex_tetragonal(section):
   
   if section == 'header' :
     return'\n'.join(['\\documentclass{article}',
                      '\\usepackage{tikz}\n',
                      '\\graphicspath{{../}{./}}'
                      '\\usetikzlibrary{shapes,arrows}\n',
                      '\\usepackage{miller}\n',
                      '\\usepackage[graphics, active, tightpage]{preview}\n',
                      '\\PreviewEnvironment{tikzpicture}\n',
                      '\\begin{document}\n',
                      '\\thispagestyle{empty}\n',
                      '\\begin{tikzpicture}',
                      '\\begin{scope}[x=19.313708cm,y=19.313708cm]',
                      '\\draw[line width=1.0pt] (0,0) -- (1,0);',
                      '\\draw[line width=1.0pt] (1,0) arc(0:45:1);',
#                      '\\draw[line width=1.0pt] (0,0) -- (0,1);',
                      '\\draw[line width=1.0pt] (0,0) -- (0.707,0.707);',
                      '\\begin{scope}[inner sep=0pt]',
                      '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<001>}] at (0.000000,0.000000) {};',
                      '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<100>}] at (1.000000,0.000000) {};',
                      '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<110>}] at (0.707107,0.707107) {};',
#                      '\\node[fill,diamond,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<010>}] at (0.0000,1.0000) {};',
                      '\\end{scope}\n',
                      '\\begin{scope}[inner sep=1.0pt]\n'])
   elif section == 'footer' :
     return'\n'.join(['\\end{scope}\n',
                      '\\end{scope}',
                      '\\end{tikzpicture}',
                      '\\end{document}'])

def generate_tex_hexagonal(section):
   
   if section == 'header' :
     return'\n'.join(['\\documentclass{article}',
                      '\\usepackage{tikz}\n',
                      '\\graphicspath{{../}{./}}'
                      '\\usetikzlibrary{shapes,arrows}\n',
                      '\\usepackage{miller}\n',
                      '\\usepackage[graphics, active, tightpage]{preview}\n',
                      '\\PreviewEnvironment{tikzpicture}\n',
                      '\\begin{document}\n',
                      '\\thispagestyle{empty}\n',
                      '\\begin{tikzpicture}',
                      '\\begin{scope}[x=19.313708cm,y=19.313708cm]',
                      '\\draw[line width=1.0pt] (0,0) -- (1,0);',
                      '\\draw[line width=1.0pt] (1,0) arc(0:30:1);',
#                      '\\draw[line width=1.0pt] (0,0) -- (0,1);',
                      '\\draw[line width=1.0pt] (0,0) -- (0.866,0.50);',
#                      '\\draw[line width=1.0pt] (0,0) -- (0.5,0.8660);',
                      '\\begin{scope}[inner sep=0pt]',
                      '\\node[fill,rectangle,minimum height=6pt,minimum width=6pt,label={below left:\\small\\hkl<0001>}] at (0.000000,0.000000) {};',
                      '\\node[fill,diamond,minimum height=12pt,minimum width=6pt,label={below right:\\small\\hkl<2-1-10>}] at (1.000000,0.000000) {};',
                      '\\node[fill,ellipse,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<10-10>}] at (0.866,0.5) {};',
#                      '\\node[fill,diamond,minimum height=6pt,minimum width=6pt,label={above right:\\small\\hkl<11-20>}] at (0.5,0.866) {};',
                      '\\end{scope}\n',
                      '\\begin{scope}[inner sep=1.0pt]\n'])
   elif section == 'footer' :
     return'\n'.join(['\\end{scope}\n',
                      '\\end{scope}',
                      '\\end{tikzpicture}',
                      '\\end{document}'])

#------------------------------------------------------#
def append(vector):
  color = np.array(([255,0,0]))
  if np.linalg.norm(vector) != 0.0:
    vector = vector/np.linalg.norm(vector)
  zeta = math.degrees(math.atan2(vector[1],vector[0]))
  eta  = math.degrees(math.acos(vector[2]))
  phi1 = 270 + zeta
  PHI  = eta
  phi2 = 90 - zeta
  if options.eulers == True:
    listAngles.append(phi1)
    listAngles.append(PHI)
    listAngles.append(phi2)
#   X = vector[0] * math.sqrt(1. /(1 + abs(vector[2])))                                     # homochoric projection
#   Y = vector[1] * math.sqrt(1. /(1 + abs(vector[2])))
  X = vector[0] /((1 + abs(vector[2])))                                                     # stereographic projection
  Y = vector[1] /((1 + abs(vector[2])))
  if [X,Y] not in listCoords:
    listCoords.append([X,Y])
    if options.unitcell == True :
      if options.symmetry == 'tetragonal' :
        cmd = '%s/unitcell.py -n "%s-%s-%s" -c 0.5456 --up 0 1 0 -e %.02f %.02f %.02f '%(options.root,str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
      elif options.symmetry == 'cubic' :
        cmd = '%s/unitcell.py -n "%s-%s-%s" -c 1.0 --up 0 1 0 -e %.02f %.02f %.02f '%(options.root,str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
      elif options.symmetry == 'hexagonal' :
        cmd = '%s/unitcell.py -u hexagonal -n "%s-%s-%s" --up 0 1 0 -e %.02f %.02f %.02f '%(options.root,str(int(phi1)),str(int(PHI)),str(int(phi2)),phi1,PHI,phi2)
      call(cmd,shell=True)
      out = '%s-%s-%s.pdf'%(str(int(phi1)),str(int(PHI)),str(int(phi2)))
      texfile.write('\\node at (%.03f,%.03f){\includegraphics[scale=0.1]{%s}};\n'%(X,Y,out))
    else :
      texfile.write('\\node[fill={rgb:red,%.4f;green,%.4f;blue,%.4f}, circle, minimum height=4pt] at (%.4f, %.4f) {};\n'%(color[0]/255.0, color[1]/255.0, color[2]/255.0, X, Y))
  return


def mid(vector1,vector2):
  mid1 = np.array(([(vector1[0] + vector2[0])/2 ,(vector1[1] + vector2[1])/2 ,(vector1[2] + vector2[2])/2 ]))
  append(mid1)
  return mid1

#        Using Sierpenski triangle algorithm and modifying it             #

def sierpenski(vector,degree):
  if degree > 0:
    sierpenski([vector[0],mid(vector[0],vector[1]),mid(vector[0],vector[2])],degree - 1)
    sierpenski([vector[1],mid(vector[0],vector[1]),mid(vector[1],vector[2])],degree - 1)
    sierpenski([vector[2],mid(vector[2],vector[1]),mid(vector[0],vector[2])],degree - 1)
    sierpenski([mid(vector[0],vector[1]),mid(vector[0],vector[2]),mid(vector[1],vector[2])],degree - 1)
  return


if not os.path.exists('equidistant'): os.makedirs('equidistant')


texfile = open("equidistant/equidistant_IPF.tex", 'w')
if options.symmetry == 'tetragonal':
  texfile.write(generate_tex_tetragonal('header'))
elif options.symmetry == 'cubic':
  texfile.write(generate_tex_cubic('header'))
elif options.symmetry == 'hexagonal':
  texfile.write(generate_tex_hexagonal('header'))
vector = np.array((options.point1,options.point2,options.point3))
append(vector[0])
append(vector[1])
append(vector[2])
sierpenski(vector,options.degrees)
texfile.write(generate_tex_tetragonal('footer'))
texfile.close()

if options.eulers:
  listAngles = np.array(listAngles).reshape(len(listAngles)/3,3)
  sorted_idx = np.lexsort(listAngles.T)
  sorted_data =  listAngles[sorted_idx,:]

  # Get unique row mask
  row_mask = np.append([True],np.any(np.diff(sorted_data,axis=0),1))

  # Get unique rows
  uniqueAngles = sorted_data[row_mask]
  for i in xrange(len(uniqueAngles)):
    print uniqueAngles[i,0],uniqueAngles[i,1],uniqueAngles[i,2]
    
    