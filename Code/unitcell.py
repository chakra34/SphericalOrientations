#!/usr/bin/env python

#   line [thinvectorstyle] (O)(px) 
#   line [thinvectorstyle] (O)(py) 
# # line [thinvectorstyle] (O)(pz) 
#   special | \path #1 -- #2 node[at end, below] {$ x $}; | (O)(px)
#   special | \path #1 -- #2 node[at end, below] {$ y $}; | (O)(py)
#   special | \path #1 -- #2 node[at end, above] {$ z $}; | (O)(pz)

import sys,os,math
from optparse import OptionParser

unitcell_choices = ['cubic','hexagonal']
  
parser = OptionParser(usage='%prog [options]', description = """
Generate vector-based crystal unit overlays from Euler angles.
Angles are specified either directly as argument, resulting in a single file with name derived from the orientation and lattice,
or by scanning through an EDAX/TSL unitcell file from which a batch of unitcells located at the respective positions is produced.

Requires a working setup of 'sketch' (by Gene Ressler) plus 'LaTeX' with 'TikZ' extension.
Column headings need to have names 'phi1', 'Phi', 'phi2'.

$Id: unitcell.py 474 2017-03-10 19:31:50Z p.eisenlohr $
""")

parser.add_option('-u', '-t', '--unitcell', type='string', metavar = 'string',
                  dest='unitcell',
                  help='type of unit cell [%s]'%(','.join(unitcell_choices)))
parser.add_option('-n', '--name', type='string', metavar = 'string',
                  dest='name',
                  help='filename of output')
parser.add_option('-e', '--eulers', type='float', nargs=3, metavar = 'float float float',
                  dest='eulers',
                  help='3-1-3 Euler angles in degrees [%default]')
parser.add_option('-r', '--radians', action='store_true',
                  dest='radians',
                  help='Euler angles in radians [%default]')
parser.add_option('-c', '--covera', type='float', metavar = 'float',
                  dest='ca',
                  help='c over a ratio [ideal]')
parser.add_option('-o', '--opacity', type='float', metavar = 'float',
                  dest='opacity',
                  help='opacity level [%default]')
parser.add_option('-a', '--axes', action='store_true',
                  dest='axes',
                  help='show all axes [%default]')
parser.add_option('--globalaxes', action='store_true',
                  dest='globalaxes',
                  help='show global axes [%default]')
parser.add_option('--localaxes', action='store_true',
                  dest='localaxes',
                  help='show local axes [%default]')
parser.add_option('--vector', type='float', nargs=3, metavar = 'float float float',
                  dest='vector',
                  help='draw a lattice vector')
parser.add_option('-p', '--perspective', action='store_true',
                  dest='perspective',
                  help='perspective view [%default]')
parser.add_option('-y', '--eye', type='float', nargs=3, metavar = 'float float float',
                  dest='eye',
                  help='position of eye on scene [%default]')
parser.add_option(      '--up', type='float', nargs=3, metavar = 'float float float',
                  dest='up',
                  help='vector corresponding to up direction [%default]')
parser.add_option('-f', '--figure', action='store_true',
                  dest='figure',
                  help='produce LaTeX figure compatible file instead of PDF [%default]')
parser.add_option('-k', '--keep', action='store_true',
                  dest='keep',
                  help='keep intermediate files [%default]')
parser.add_option('-b', '--batch', type='string', metavar = 'string',
                  dest='batchfile',
                  help='EDAX/TSL unitcell file')
parser.add_option('-l', '--label', action='store_true',
                  dest='label',
                  help='mark batch processed unit cells by number [%default]')
parser.add_option('-s', '--scale', type='float', metavar = 'float',
                  dest='scale',
                  help='scale of diagonal bounding box in batch file [%default]')
parser.add_option('-v', '--verbose', action='store_true',
                  dest='verbose',
                  help='verbose output')

parser.set_defaults(unitcell = 'cubic',
                    batchfile = None,
                    eulers = [0.0,0.0,0.0],
                    ca = None,
                    opacity = 0.8,
                    scale = 7,
                    globalaxes  = False,
                    localaxes   = False,
                    axes        = False,
                    perspective = False,
                    line = None,
                    eye = [0.0,0.0,1.0],
                    up = [-1.0,0.0,0.0],
                    figure = False,
                    keep = False,
                    radians = False,
                    label = False,
                    verbose = False,
                   )

(options, args) = parser.parse_args()

if options.unitcell not in unitcell_choices:
  parser.error('"%s" not a valid choice for unitcell [%s]'%(options.unitcell,','.join(unitcell_choices)))

if options.axes: options.globalaxes = options.localaxes = options.axes
  
if not options.ca: options.ca = {'cubic':1,'hexagonal':1.633}[options.unitcell]

opacity = max(0.0,min(1.0,options.opacity))

if options.perspective:
  options.perspective = 'view((%f,%f,%f),(0,0,0),[%f,%f,%f]) then perspective(%f)'%((5.0+options.scale)*options.eye[0],\
                                                                                    (5.0+options.scale)*options.eye[1],\
                                                                                    (5.0+options.scale)*options.eye[2],\
                                                                                    options.up[0],\
                                                                                    options.up[1],\
                                                                                    options.up[2],\
                                                                                    80.0/options.scale**0.4)
else:
  options.perspective = 'view((%f,%f,%f),(0,0,0),[%f,%f,%f]) then scale(%f)'%(options.scale*options.eye[0],\
                                                                              options.scale*options.eye[1],\
                                                                              options.scale*options.eye[2],\
                                                                              options.up[0],\
                                                                              options.up[1],\
                                                                              options.up[2],\
                                                                              20.0/options.scale)


coords = {
          'x':[4,1],         # column 4 positive
          'y':[3,1],         # column 3 positive
         }

header = """
def O (0,0,0)
def J [0,0,1]

def px [1,0,0]+(O)
def py [0,1,0]+(O)
def pz [0,0,1]+(O)

def globalSystemAxes
{{

line[color=black,line width=0.5pt] (O)(px)
line[color=black,line width=0.5pt] (O)(py)
line[color=black,line width=0.5pt] (O)(pz)
special | 
 \path #1 -- #2 node[color=black,font=\\footnotesize,pos=1.25] {{$x$}};
 \path #1 -- #3 node[color=black,font=\\footnotesize,pos=1.25] {{$y$}};
 \path #1 -- #4 node[color=black,font=\\footnotesize,pos=1.25] {{$z$}};
| (O)(px)(py)(pz)
  
}}


def localSystemAxes
{{

line[color=red,line width=1.5pt] (O)(px)
line[color=red,line width=1.5pt] (O)(py)
line[color=red,line width=1.5pt] (O)(pz)
special | 
 \path #1 -- #2 node[color=red,font=\\footnotesize,pos=1.25] {{$x$}};
 \path #1 -- #3 node[color=red,font=\\footnotesize,pos=1.25] {{$y$}};
 \path #1 -- #4 node[color=red,font=\\footnotesize,pos=1.25] {{$z$}};
| (O)(px)(py)(pz)

}}


def unitcell_hexagonal
{{
  def n 6
  def ca {ca}
  
  sweep[cull=false,line width={linewidth}pt,fill=white,draw=black,fill opacity={opacity}]
        {{n<>,rotate(360/n,(O),[J])}} line (1,0,-ca/2)(1,0,ca/2)
}}


def unitcell_cubic
{{
  def n 4
  def ca {ca}
  
  sweep[cull=false,line width={linewidth}pt,fill=white,draw=black,fill opacity={opacity}]
        {{n<>,rotate(360/n,(O),[J])}} line (0.5,0.5,-ca/2)(0.5,0.5,ca/2)
}}


"""

rotation = """
def EulerRotation_{0}_{1}_{2}
                        rotate({0},[0,0,1]) then
             rotate({1},rotate({0},[0,0,1])*[1,0,0]) then 
  rotate({2},rotate({1},rotate({0},[0,0,1])*[1,0,0])*[0,0,1])

"""

unitcell   = "put {{ [[EulerRotation_{euler[0]}_{euler[1]}_{euler[2]}]] then translate([{dx},{dy},0]) }} {{unitcell_{celltype}}}"
vector     = "put {{ [[EulerRotation_{euler[0]}_{euler[1]}_{euler[2]}]] then translate([{dx},{dy},0]) }} {{ line[color=blue,line width=2pt] (O)({vector}) }}"
localaxes  = "put {{ [[EulerRotation_{euler[0]}_{euler[1]}_{euler[2]}]] then translate([{dx},{dy},0]) then scale(1.25) }} {{ {{localSystemAxes}} }}"
globalaxes = '{globalSystemAxes}'
label      = "special |\\node at #1 {%i};|(%f,%f,0)"  

view = """
put { %s }
    { 
     %s
    }
"""

footer = """
global { language tikz }
"""


if options.batchfile == None or not os.path.isfile(options.batchfile):
  if options.radians:
    options.eulers = map(math.degrees,options.eulers)
  options.eulers = map(lambda x: x%360.,options.eulers)                     # Euler angles between 0 and 360 deg

  filename = options.name if options.name else 'unitcell_{0}_{1}_{2}_{3}'.format(options.unitcell,*map(lambda x:int(round(x)),options.eulers))

  cmd = header.format(ca=options.ca,
                      linewidth=40/options.scale,
                      opacity=options.opacity,
                     )
  cmd += rotation.format(*map(lambda x:int(round(x)),options.eulers))
  cmd += view %(options.perspective,
                (globalaxes if options.globalaxes else '') + \
                (localaxes.format(euler = map(lambda x:int(round(x)),options.eulers),
                                  dx = 0.0,dy = 0.0,) if options.localaxes  else '') + \
                (vector.format(euler = map(lambda x:int(round(x)),options.eulers),
                               dx = 0.0, dy = 0.0,
                               vector = ','.join(map(str,options.vector))) if options.vector  else '') + \
                unitcell.format(euler = map(lambda x:int(round(x)),options.eulers),
                                dx = 0.0, dy = 0.0,
                                celltype = options.unitcell,
                               ),
               )
  cmd += footer

else:
  filename = 'unitcell_%s_%s'%(options.unitcell,os.path.basename(os.path.splitext(options.batchfile)[0]))
  
  offset = 0 if os.path.splitext(options.batchfile)[1].lower() == '.ang' else 1
  with open(options.batchfile) as batchFile:
    content = [line for line in batchFile.readlines() if line.find('#') != 0]

  dataset = [map(float,line.split(None if content[0].find(',') < 0 else ',')[offset:offset+5]) for line in content]
  
  print len(dataset)

  boundingBox = [
                  [coords['x'][1]*dataset[0][coords['x'][0]],
                   coords['y'][1]*dataset[0][coords['y'][0]],
                  ] ,
                  [coords['x'][1]*dataset[0][coords['x'][0]],
                   coords['y'][1]*dataset[0][coords['y'][0]],
                  ] ,
                ]
  
  for point in dataset[1:]:
    x = coords['x'][1]*point[coords['x'][0]]
    y = coords['y'][1]*point[coords['y'][0]]
    if boundingBox[0][0] > x:
       boundingBox[0][0] = x
    if boundingBox[1][0] < x:
       boundingBox[1][0] = x
    if boundingBox[0][1] > y:
       boundingBox[0][1] = y
    if boundingBox[1][1] < y:
       boundingBox[1][1] = y
  
  print '---------------------------------'
  print boundingBox
  print '---------------------------------'
  centre = [
            (boundingBox[0][0]+boundingBox[1][0])/2.0,
            (boundingBox[0][1]+boundingBox[1][1])/2.0,
           ]
  scale = options.scale / \
          math.sqrt( (boundingBox[1][0]-boundingBox[0][0])*(boundingBox[1][0]-boundingBox[0][0])+
                     (boundingBox[1][1]-boundingBox[0][1])*(boundingBox[1][1]-boundingBox[0][1]) )

  rotations = {}
  cells = []
  labels = []
  
  counter = 0
  
  for point in dataset:
    counter += 1
    x = coords['x'][1]*point[coords['x'][0]]
    y = coords['y'][1]*point[coords['y'][0]]
    if options.radians:
      point[:3] = map(math.degrees,point[:3])

    eulers = map(lambda x:str(int(round(x))),point[:3])
    rotations['#'.join(eulers)] = rotation.format(*eulers)
    cells.append(cell.format(euler=eulers,
                             dx=scale*(x-centre[0]),
                             dy=scale*(y-centre[1]),
                             celltype=options.unitcell)
                )
    if options.label:
      labels.append(label % (counter,
                             scale*(x-centre[0]),
                             scale*(y-centre[1]),
                            ))
  
  print len(rotations),'rotations'
  
  cmd = header.format(ca=options.ca,
                      linewidth=80/options.scale,
                      opacity=options.opacity
                     )
  cmd += '\n'.join(rotations.values())
  cmd += view %(options.perspective,
                options.axes,
                '\n'.join(cells),
                '\n'.join(labels),
               )
  cmd += footer

with open(filename+'.sk','w') as sk:
  sk.write(cmd)

verbosity =  '' if options.verbose else '&>/dev/null'

if options.figure:
  os.system('sketch -o %s.tex %s.sk %s'%(filename,filename,verbosity))
  if not options.keep:
    os.remove(filename+'.sk')
else:
  os.system('sketch -Tb -o %s.tex %s.sk %s'%(filename,filename,verbosity))    # use tightly bound (-Tb) paper output format
  os.system('pdflatex %s.tex 1>/dev/null'%(filename))                         # ignore run time messages of pdflatex
  if not options.keep:
    os.remove(filename+'.sk')
    os.remove(filename+'.tex')
    os.remove(filename+'.log')
    os.remove(filename+'.aux')
