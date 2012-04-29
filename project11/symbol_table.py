# the symbol table for the compiler
# the symbol table supports the two scopes of Jack: class and subroutine

class SymbolTable(object):
   # constants for each type of symbol
   STATIC = 0
   FIELD  = 1
   ARG    = 2
   VAR    = 3
   kinds = [STATIC, FIELD, ARG, VAR]

   # counts the number of each segment enountered thus far during parsing
   # the indexes correspond to the constants above
   counts = None

   # the two symbol tables for class and subroutine scopes
   # each is a dictonary of name -> (kind, type, index)
   # kind is one of STATIC, FIELD, ARG, or VAR
   # type is a string of the type of variable
   # index is the index in the VM segment that is used by this variable
   class_symbols = None
   subroutine_symbols = None

   def __init__(self):
      self.class_symbols = dict()
      self.subroutine_symbols = dict()
      self.counts = [0, 0, 0, 0]

   # starts a new subroutine
   def start_subroutine(self):
      self.subroutine_symbols = dict()
      self.counts[self.ARG] = 0
      self.counts[self.VAR] = 0

   # defines a new identifier of a given name, type, and kind, assigning it to
   # a running index for each type
   # STATIC and FIELD have a class scope, while ARG and VAR have a subroutine
   # scope
   def define(self, name, type, kind):
      if kind not in self.kinds:
         print "WARNING: Unknown kind %s" % (str(kind))
         return

      # use the correct symbol table
      if kind in [self.STATIC, self.FIELD]:
         table = self.class_symbols
      else:
         table = self.subroutine_symbols

      # check to see if the variable has already been defined
      if name in table:
         print "WARNING: Identifier", name, "is being redefined."

      # insert the identifier into the table
      index = self.counts[kind]
      table[name] = (kind, type, index)

      # increase the number of identifiers in the table
      self.counts[kind] += 1

   # returns the number of variabels of a given kind already defined in the
   # current scope
   def var_count(self, kind):
      if kind in self.kinds:
         return self.counts[kind]
      else:
         print "WARNING: unknown kind %s" % (str(kind))
         return None

   # returns an identifier's information as a 3-tuple (kind, type, index)
   # if the identifier is not known, then None is returned
   def get(self, name):
      if name in self.subroutine_symbols:
         return self.subroutine_symbols[name]
      elif name in self.class_symbols:
         return self.class_symbols[name]
      else:
         print "WARNING: unknown identifier %s" % (str(name))
         return None

   def contains(self, name):
      return name in self.subroutine_symbols or name in self.class_symbols
