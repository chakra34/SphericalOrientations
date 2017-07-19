# -*- coding: UTF-8 no BOM -*-

# obtained from https://damask.mpie.de #

import os,sys
import numpy as np

# ------------------------------------------------------------------
# python 3 has no unicode object, this ensures that the code works on Python 2&3
try:
  test=isinstance('test', unicode)
except(NameError):
  unicode=str

# ------------------------------------------------------------------
class ASCIItable():
  """Read and write to ASCII tables"""

  __slots__ = ['__IO__',
               'info',
               'labeled',
               'data',
              ]

  tmpext = '_tmp'                                                                                   # filename extension for in-place access
  
# ------------------------------------------------------------------
  def __init__(self,
               name    = None,
               outname = None,
               buffered  = False,                                                                   # flush writes
               labeled   = True,                                                                    # assume table has labels
               readonly  = False,                                                                   # no reading from file
              ):
    self.__IO__ = {'output': [],
                   'buffered': buffered,
                   'labeled':  labeled,                                                             # header contains labels
                   'tags': [],                                                                      # labels according to file info
                   'readBuffer': [],                                                                # buffer to hold non-advancing reads
                   'dataStart': 0,
                  }

    self.__IO__['inPlace'] = not outname and name and not readonly
    if self.__IO__['inPlace']: outname = name + self.tmpext                                         # transparently create tmp file
    try:
      self.__IO__['in'] = (open(   name,'r') if os.access(   name, os.R_OK) else None) if name else sys.stdin
    except TypeError:
      self.__IO__['in'] = name

    try:
      self.__IO__['out'] = (open(outname,'w') if (not os.path.isfile(outname) or
                                                      os.access(     outname, os.W_OK)
                                                 ) and
                                                 (not self.__IO__['inPlace'] or
                                                  not os.path.isfile(name)   or
                                                      os.access(     name, os.W_OK)
                                                 ) else None) if outname else sys.stdout
    except TypeError:
      self.__IO__['out'] = outname

    self.info   = []
    self.tags  = []
    self.data   = []
    self.line   = ''

    if   self.__IO__['in']  is None \
      or self.__IO__['out'] is None: raise IOError                                                 # complain if any required file access not possible
     
# ------------------------------------------------------------------
  def _transliterateToFloat(self,
                            x):
    try:
      return float(x)
    except:
      return 0.0

# ------------------------------------------------------------------
  def _removeCRLF(self,
              string):
    try:
      return string.replace('\n','').replace('\r','')
    except:
      return string


# ------------------------------------------------------------------
  def _quote(self,
             what):
    """quote empty or white space-containing output"""
    import re
    
    return '{quote}{content}{quote}'.format(
             quote   = ('"' if str(what)=='' or re.search(r"\s",str(what)) else ''),
             content = what)
# ------------------------------------------------------------------
  def close(self,
            dismiss = False):
    self.input_close()
    self.output_flush()
    self.output_close(dismiss)

# ------------------------------------------------------------------
  def input_close(self):
    try:
      if self.__IO__['in'] != sys.stdin: self.__IO__['in'].close()
    except:
      pass

# ------------------------------------------------------------------
  def output_write(self,
                   what):
    """aggregate a single row (string) or list of (possibly containing further lists of) rows into output"""
    if not isinstance(what, (str, unicode)):
      try:
        for item in what: self.output_write(item)
      except:
        self.__IO__['output'] += [str(what)]
    else:
      self.__IO__['output'] += [what]

    return self.__IO__['buffered'] or self.output_flush()

# ------------------------------------------------------------------
  def output_flush(self,
                   clear = True):
    try:
      self.__IO__['output'] == [] or self.__IO__['out'].write('\n'.join(self.__IO__['output']) + '\n')
    except IOError:
      return False
    if clear: self.output_clear()
    return True

# ------------------------------------------------------------------
  def output_clear(self):
    self.__IO__['output'] = []

# ------------------------------------------------------------------
  def output_close(self,
                   dismiss = False):
    try:
      if self.__IO__['out'] != sys.stdout: self.__IO__['out'].close()
    except:
      pass
    if dismiss and os.path.isfile(self.__IO__['out'].name):
      os.remove(self.__IO__['out'].name)
    elif self.__IO__['inPlace']:
      os.rename(self.__IO__['out'].name, self.__IO__['out'].name[:-len(self.tmpext)])

# ------------------------------------------------------------------
  def head_read(self):
    """
    get column labels
    
    by either reading the first row or,
    if keyword "head[*]" is present, the last line of the header
    """
    import re,shlex

    try:
      self.__IO__['in'].seek(0)
    except:
      pass

    firstline = self.__IO__['in'].readline().strip()
    m = re.search('(\d+)\s+head', firstline.lower())                                                # search for "head" keyword
    
    if m:                                                                                           # proper ASCIItable format

      if self.__IO__['labeled']:                                                                    # table features labels

        self.info   = [self.__IO__['in'].readline().strip() for i in range(1,int(m.group(1)))]
        self.tags = shlex.split(self.__IO__['in'].readline())                                       # store tags found in last line

      else:

        self.info    = [self.__IO__['in'].readline().strip() for i in range(0,int(m.group(1)))]     # all header is info ...

    else:                                                                                           # other table format
      try:
        self.__IO__['in'].seek(0)                                                                   # try to rewind
      except:
        self.__IO__['readBuffer'] = [firstline]                                                     # or at least save data in buffer

      while self.data_read(advance = False, respectLabels = False):
        if self.line[0] in ['#','!','%','/','|','*','$']:                                           # "typical" comment indicators
          self.info_append(self.line)                                                               # store comment as info
          self.data_read()                                                                          # wind forward one line
        else: break                                                                                 # last line of comments

      if self.__IO__['labeled']:                                                                    # table features labels
        self.tags = self.data                                                                       # get tags from last line in "header"...
        self.data_read()                                                                            # ...and remove from buffer
        
    if self.__IO__['labeled']:                                                                      # table features tags
      self.__IO__['tags'] = list(self.tags)                                                         # backup tags (make COPY, not link)

    try:
      self.__IO__['dataStart'] = self.__IO__['in'].tell()                                           # current file position is at start of data
    except IOError:
      pass

# ------------------------------------------------------------------
  def head_write(self,
                 header = True):
    """write current header information (info + labels)"""
    head = ['{}\theader'.format(len(self.info)+self.__IO__['labeled'])] if header else []
    head.append(self.info)
    if self.__IO__['labeled']: head.append('\t'.join(map(self._quote,self.tags)))
    
    return self.output_write(head)

# ------------------------------------------------------------------
  def head_getGeom(self):
    """interpret geom header"""
    identifiers = {
            'grid':    ['a','b','c'],
            'size':    ['x','y','z'],
            'origin':  ['x','y','z'],
              }
    mappings = {
            'grid':            lambda x: int(x),
            'size':            lambda x: float(x),
            'origin':          lambda x: float(x),
            'homogenization':  lambda x: int(x),
            'microstructures': lambda x: int(x),
              }
    info = {
            'grid':            np.zeros(3,'i'),
            'size':            np.zeros(3,'d'),
            'origin':          np.zeros(3,'d'),
            'homogenization':  0,
            'microstructures': 0,
           }
    extra_header = []

    for header in self.info:
      headitems = list(map(str.lower,header.split()))
      if len(headitems) == 0: continue                                                              # skip blank lines
      if headitems[0] in list(mappings.keys()):
        if headitems[0] in list(identifiers.keys()):
          for i in range(len(identifiers[headitems[0]])):
            info[headitems[0]][i] = \
              mappings[headitems[0]](headitems[headitems.index(identifiers[headitems[0]][i])+1])
        else:
          info[headitems[0]] = mappings[headitems[0]](headitems[1])
      else:
        extra_header.append(header)

    return info,extra_header


# ------------------------------------------------------------------
  def head_putGeom(self,info):
    """translate geometry description to header"""
    self.info_append([
      "grid\ta {}\tb {}\tc {}".format(*info['grid']),
      "size\tx {}\ty {}\tz {}".format(*info['size']),
      "origin\tx {}\ty {}\tz {}".format(*info['origin']),
      "homogenization\t{}".format(info['homogenization']),
      "microstructures\t{}".format(info['microstructures']),
      ])
    
# ------------------------------------------------------------------
  def labels_append(self,
                    what,
                    reset = False):
    """add item or list to existing set of labels (and switch on labeling)"""
    if not isinstance(what, (str, unicode)):
      try:
        for item in what: self.labels_append(item)
      except:
        self.tags += [self._removeCRLF(str(what))]
    else:
      self.tags += [self._removeCRLF(what)]

    self.__IO__['labeled'] = True                                                                  # switch on processing (in particular writing) of tags
    if reset: self.__IO__['tags'] = list(self.tags)                                                # subsequent data_read uses current tags as data size

# ------------------------------------------------------------------
  def labels_clear(self):
    """delete existing labels and switch to no labeling"""
    self.tags = []
    self.__IO__['labeled'] = False

# ------------------------------------------------------------------
  def labels(self,
             tags = None,
             raw = False):
    """
    tell abstract labels.
    
    "x" for "1_x","2_x",... unless raw output is requested.
    operates on object tags or given list.
    """
    from collections import Iterable
    
    if tags is None: tags = self.tags

    if isinstance(tags, Iterable) and not raw:                                                    # check whether list of tags is requested
      id = 0
      dim = 1
      labelList = []

      while id < len(tags):
        if not tags[id].startswith('1_'):
          labelList.append(tags[id])
        else:
          label = tags[id][2:]                                                                    # get label
          while id < len(tags) and tags[id] == '{}_{}'.format(dim,label):                         # check successors
            id  += 1                                                                              # next label...
            dim += 1                                                                              # ...should be one higher dimension
          labelList.append(label)                                                                 # reached end --> store
          id -= 1                                                                                 # rewind one to consider again

        id += 1
        dim = 1

    else:
      labelList = self.tags

    return labelList

# ------------------------------------------------------------------
  def label_index(self,
                  labels):
    """
    tell index of column label(s).

    return numpy array if asked for list of labels.
    transparently deals with label positions implicitly given as numbers or their headings given as strings.
    """
    from collections import Iterable

    if isinstance(labels, Iterable) and not isinstance(labels, str):                                # check whether list of labels is requested
      idx = []
      for label in labels:
        if label is not None:
          try:
            idx.append(int(label)-1)                                                                # column given as integer number?
          except ValueError:
            label = label[1:-1] if label[0] == label[-1] and label[0] in ('"',"'") else label       # remove outermost quotations
            try:
              idx.append(self.tags.index(label))                                                    # locate string in label list
            except ValueError:
              try:
                idx.append(self.tags.index('1_'+label))                                             # locate '1_'+string in label list
              except ValueError:
               idx.append(-1)                                                                       # not found...
    else:
      try:
        idx = int(labels)-1                                                                         # offset for python array indexing
      except ValueError:
        try:
          labels = labels[1:-1] if labels[0] == labels[-1] and labels[0] in ('"',"'") else labels   # remove outermost quotations
          idx = self.tags.index(labels)
        except ValueError:
          try:
            idx = self.tags.index('1_'+labels)                                                      # locate '1_'+string in label list
          except ValueError:
            idx = None if labels is None else -1

    return np.array(idx) if isinstance(idx,Iterable) else idx

# ------------------------------------------------------------------
  def label_dimension(self,
                      labels):
    """
    tell dimension (length) of column label(s).

    return numpy array if asked for list of labels.
    transparently deals with label positions implicitly given as numbers or their headings given as strings.
    """
    from collections import Iterable

    if isinstance(labels, Iterable) and not isinstance(labels, str):                                # check whether list of labels is requested
      dim = []
      for label in labels:
        if label is not None:
          myDim = -1
          try:                                                                                      # column given as number?
            idx = int(label)-1
            myDim = 1                                                                               # if found has at least dimension 1
            if self.tags[idx].startswith('1_'):                                                     # column has multidim indicator?
              while idx+myDim < len(self.tags) and self.tags[idx+myDim].startswith("%i_"%(myDim+1)):
                myDim += 1                                                                          # add while found
          except ValueError:                                                                        # column has string label
            label = label[1:-1] if label[0] == label[-1] and label[0] in ('"',"'") else label       # remove outermost quotations
            if label in self.tags:                                                                  # can be directly found?
              myDim = 1                                                                             # scalar by definition
            elif '1_'+label in self.tags:                                                           # look for first entry of possible multidim object
              idx = self.tags.index('1_'+label)                                                     # get starting column
              myDim = 1                                                                             # (at least) one-dimensional
              while idx+myDim < len(self.tags) and self.tags[idx+myDim].startswith("%i_"%(myDim+1)):
                myDim += 1                                                                          # keep adding while going through object

          dim.append(myDim)
    else:
      dim = -1                                                                                      # assume invalid label
      idx = -1
      try:                                                                                          # column given as number?
        idx = int(labels)-1
        dim = 1                                                                                     # if found has at least dimension 1
        if self.tags[idx].startswith('1_'):                                                         # column has multidim indicator?
          while idx+dim < len(self.tags) and self.tags[idx+dim].startswith("%i_"%(dim+1)):
            dim += 1                                                                                # add as long as found
      except ValueError:                                                                            # column has string label
        labels = labels[1:-1] if labels[0] == labels[-1] and labels[0] in ('"',"'") else labels     # remove outermost quotations
        if labels in self.tags:                                                                     # can be directly found?
          dim = 1                                                                                   # scalar by definition
        elif '1_'+labels in self.tags:                                                              # look for first entry of possible multidim object
          idx = self.tags.index('1_'+labels)                                                        # get starting column
          dim = 1                                                                                   # is (at least) one-dimensional
          while idx+dim < len(self.tags) and self.tags[idx+dim].startswith("%i_"%(dim+1)):
            dim += 1                                                                                # keep adding while going through object

    return np.array(dim) if isinstance(dim,Iterable) else dim

# ------------------------------------------------------------------
  def label_indexrange(self,
                       labels):
    """
    tell index range for given label(s).

    return numpy array if asked for list of labels.
    transparently deals with label positions implicitly given as numbers or their headings given as strings.
    """
    from collections import Iterable

    start = self.label_index(labels)
    dim   = self.label_dimension(labels)
  
    return np.hstack([range(c[0],c[0]+c[1]) for c in zip(start,dim)]) \
        if isinstance(labels, Iterable) and not isinstance(labels, str) \
      else range(start,start+dim)

# ------------------------------------------------------------------
  def info_append(self,
                  what):
    """add item or list to existing set of infos"""
    if not isinstance(what, (str, unicode)):
      try:
        for item in what: self.info_append(item)
      except:
        self.info += [self._removeCRLF(str(what))]
    else:
      self.info += [self._removeCRLF(what)]

# ------------------------------------------------------------------
  def info_clear(self):
    """delete any info block"""
    self.info = []

# ------------------------------------------------------------------
  def data_rewind(self):
    self.__IO__['in'].seek(self.__IO__['dataStart'])                                                # position file to start of data section
    self.__IO__['readBuffer'] = []                                                                  # delete any non-advancing data reads
    self.tags = list(self.__IO__['tags'])                                                           # restore label info found in header (as COPY, not link)
    self.__IO__['labeled'] = len(self.tags) > 0

# ------------------------------------------------------------------
  def data_skipLines(self,
                     count):
    """wind forward by count number of lines"""
    for i in range(count):
      alive = self.data_read()

    return alive

# ------------------------------------------------------------------
  def data_read(self,
                advance = True,
                respectLabels = True):
    """read next line (possibly buffered) and parse it into data array"""
    import shlex
    
    self.line = self.__IO__['readBuffer'].pop(0) if len(self.__IO__['readBuffer']) > 0 \
           else self.__IO__['in'].readline().strip()                                                # take buffered content or get next data row from file

    if not advance:
      self.__IO__['readBuffer'].append(self.line)                                                   # keep line just read in buffer

    self.line = self.line.rstrip('\n')

    if self.__IO__['labeled'] and respectLabels:                                                    # if table has labels
      items = shlex.split(self.line)[:len(self.__IO__['tags'])]                                     # use up to label count (from original file info)
      self.data = items if len(items) == len(self.__IO__['tags']) else []                           # take entries if label count matches
    else:
      self.data = shlex.split(self.line)                                                            # otherwise take all

    return self.data != []

# ------------------------------------------------------------------
  def data_readArray(self,
                     labels = []):
    """read whole data of all (given) labels as numpy array"""
    from collections import Iterable

    try:
      self.data_rewind()                                                                            # try to wind back to start of data
    except:
      pass                                                                                          # assume/hope we are at data start already...

    if labels is None or labels == []:
      use = None                                                                                    # use all columns (and keep labels intact)
      labels_missing = []
    else:
      if isinstance(labels, str) or not isinstance(labels, Iterable):                               # check whether labels are a list or single item
        labels = [labels]
      indices    = self.label_index(labels)                                                         # check requested labels ...
      dimensions = self.label_dimension(labels)                                                     # ... and remember their dimension
      present  = np.where(indices >= 0)[0]                                                          # positions in request list of labels that are present ...
      missing  = np.where(indices <  0)[0]                                                          # ... and missing in table
      labels_missing = np.array(labels)[missing]                                                    # labels of missing data

      columns = []
      for i,(c,d) in enumerate(zip(indices[present],dimensions[present])):                          # for all valid labels ...
        # ... transparently add all components unless column referenced by number or with explicit dimension
        columns += list(range(c,c + \
                          (d if str(c) != str(labels[present[i]]) else \
                           1)))
      use = np.array(columns) if len(columns) > 0 else None

      self.tags = list(np.array(self.tags)[use])                                                    # update labels with valid subset

    self.data = np.loadtxt(self.__IO__['in'],usecols=use,ndmin=2)

    return labels_missing

# ------------------------------------------------------------------
  def data_write(self,
                 delimiter = '\t'):
    """write current data array and report alive output back"""
    if len(self.data) == 0: return True

    if isinstance(self.data[0],list):
      return self.output_write([delimiter.join(map(self._quote,items)) for items in self.data])
    else:
      return self.output_write( delimiter.join(map(self._quote,self.data)))

# ------------------------------------------------------------------
  def data_writeArray(self,
                      fmt = None,
                      delimiter = '\t'):
    """write whole numpy array data"""
    for row in self.data:
      try:
        output = [fmt % value for value in row] if fmt else list(map(repr,row))
      except:
        output = [fmt % row] if fmt else [repr(row)]
      
      self.__IO__['out'].write(delimiter.join(output) + '\n')

# ------------------------------------------------------------------
  def data_append(self,
                  what):
    if not isinstance(what, (str, unicode)):
      try:
        for item in what: self.data_append(item)
      except:
        self.data += [str(what)]
    else:
      self.data += [what]

# ------------------------------------------------------------------
  def data_set(self,
               what, where):
    """update data entry in column "where". grows data array if needed."""
    idx = -1
    try:
      idx = self.label_index(where)
      if len(self.data) <= idx:
        self.data_append(['n/a' for i in range(idx+1-len(self.data))])                              # grow data if too short
      self.data[idx] = str(what)
    except(ValueError):
      pass

    return idx

# ------------------------------------------------------------------
  def data_clear(self):
    self.data = []

# ------------------------------------------------------------------
  def data_asFloat(self):
    return list(map(self._transliterateToFloat,self.data))



# ------------------------------------------------------------------
  def microstructure_read(self,
                          grid,
                          type = 'i',
                          strict = False):
    """read microstructure data (from .geom format)"""
    def datatype(item):
      return int(item) if type.lower() == 'i' else float(item)
      
    N = grid.prod()                                                                          # expected number of microstructure indices in data
    microstructure = np.zeros(N,type)                                                        # initialize as flat array

    i = 0
    while i < N and self.data_read():
      items = self.data
      if len(items) > 2:
        if   items[1].lower() == 'of': items = np.ones(datatype(items[0]))*datatype(items[2])
        elif items[1].lower() == 'to': items = np.arange(datatype(items[0]),1+datatype(items[2]))
        else:                          items = list(map(datatype,items))
      else:                            items = list(map(datatype,items))

      s = min(len(items), N-i)                                                              # prevent overflow of microstructure array
      microstructure[i:i+s] = items[:s]
      i += len(items)

    return (microstructure, i == N and not self.data_read()) if strict else microstructure  # check for proper point count and end of file
