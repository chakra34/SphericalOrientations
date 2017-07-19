# -*- coding: UTF-8 no BOM -*-

# obtained from https://damask.mpie.de #

# damask utility functions
import sys,time,random,threading,os,subprocess,shlex
import numpy as np
from optparse import Option

class bcolors:
    """
    ASCII Colors (Blender code)
    
    https://svn.blender.org/svnroot/bf-blender/trunk/blender/build_files/scons/tools/bcolors.py
    http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM  = '\033[2m'
    UNDERLINE = '\033[4m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        self.BOLD = ''
        self.UNDERLINE = ''
    

# -----------------------------
def srepr(arg,glue = '\n'):
  """joins arguments as individual lines"""
  if (not hasattr(arg, "strip") and
          hasattr(arg, "__getitem__") or
          hasattr(arg, "__iter__")):
     return glue.join(srepr(x) for x in arg)
  return arg if isinstance(arg,str) else repr(arg)

# -----------------------------
def croak(what, newline = True):
  """writes formated to stderr"""
  sys.stderr.write(srepr(what,glue = '\n') + ('\n' if newline else ''))
  sys.stderr.flush()

# -----------------------------
def report(who = None,
           what = None):
  """reports script and file name"""
  croak( (emph(who)+': ' if who else '') + (what if what else '') )


# -----------------------------
def emph(what):
  """boldens string"""
  return bcolors.BOLD+srepr(what)+bcolors.ENDC


# -----------------------------
class extendableOption(Option):
  """
  used for definition of new option parser action 'extend', which enables to take multiple option arguments

  taken from online tutorial http://docs.python.org/library/optparse.html
  """

  ACTIONS = Option.ACTIONS + ("extend",)
  STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
  TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
  ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

  def take_action(self, action, dest, opt, value, values, parser):
    if action == "extend":
      lvalue = value.split(",")
      values.ensure_value(dest, []).extend(lvalue)
    else:
      Option.take_action(self, action, dest, opt, value, values, parser)

