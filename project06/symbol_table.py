# the symbol table
# all addresses should be integers; all symbols should be strings

class SymbolTable(object):
   symbols = dict()

   def __init__(self):
      # add the predefined symbols
      symbols = self.symbols
      symbols["SP"] = 0
      symbols["LCL"] = 1
      symbols["ARG"] = 2
      symbols["THIS"] = 3
      symbols["THAT"] = 4
      symbols["R0"] = 0
      symbols["R1"] = 1
      symbols["R2"] = 2
      symbols["R3"] = 3
      symbols["R4"] = 4
      symbols["R5"] = 5
      symbols["R6"] = 6
      symbols["R7"] = 7
      symbols["R8"] = 8
      symbols["R9"] = 9
      symbols["R10"] = 10
      symbols["R11"] = 11
      symbols["R12"] = 12
      symbols["R13"] = 13
      symbols["R14"] = 14
      symbols["R15"] = 15
      symbols["SCREEN"] = 16384
      symbols["KBD"] = 24576

   # adds the pair (symbol, address) to the table
   def addEntry(self, symbol, address):
      self.symbols[symbol] = address

   # does the symbol table contain the given symbol
   def contains(self, symbol):
      return symbol in self.symbols

   def __contains__(self, symbol):
      return self.contains(symbol)

   # returns the address asssociated with the symbol
   def getAddress(self, symbol):
      if symbol in self.symbols:
         return self.symbols[symbol]
      else:
         return None

   # representation of symbol table
   def __repr__(self):
      return str(self.symbols)
