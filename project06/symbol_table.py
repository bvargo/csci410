# the symbol table
# all addresses should be integers; all symbols should be strings

class SymbolTable(object):
   symbols = dict()

   def __init__(self):
      # add the predefined symbols here
      pass

   # adds the pair (symbol, address) to the table
   def addEntry(self, symbol, address):
      pass

   # does the symbol table contain the given symbol
   def contains(self, symbol):
      pass

   # returns the address asssociated with the symbol
   def getAddress(self, symbol):
      pass
