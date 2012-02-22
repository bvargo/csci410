# the assembler module
# encapsulates the entiire assembly process

from code import Code
from parser import Parser
from symbol_table import SymbolTable

class Assembler(object):
   # source and destination filenames and file handles
   source_filename = ""
   destination_filename = ""
   destination_file = None

   # initialize the assembler for the source filename
   # if the source or destination file could not be open, then an IOError is
   # thrown
   def __init__(self, source_filename):
      source_filename = source_filename.strip()

      # if the original extension was .asm, then make the new extension .hack
      # if the original extension was not .asm, then append .hack
      if source_filename[-4:] == ".asm":
         destination_filename = source_filename[:-4] + ".hack"
      else:
         destination_filename = source_filename + ".hack"

      # save the filenames
      self.source_filename = source_filename
      self.destination_file = destination_filename

      # try to open each file
      # on failure, IOError is thrown
      source_file = open(source_filename, 'r')
      self.destination_file = open(destination_filename, 'w')
   
      # the source file can be closed, since the parser will open it for each
      # pass; it was opened in order to ensure that it could be opened
      source_file.close()

   # assemble the source
   def assemble(self):
      #
      # first pass - build the symbol table for labels
      #

      parser = Parser(self.source_filename)
      symbol_table = SymbolTable()

      # the current instruction
      instruction = 0

      # parse each command
      while parser.hasMoreCommands():
         # advance to the next command
         parser.advance()

         # parse the command type and look for symbols
         command_type = parser.commandType()
         if command_type == "L":
            # look for an instruction label symbol
            symbol = parser.symbol()
            if symbol not in symbol_table:
               symbol_table.addEntry(symbol, instruction)
         else:
            # increment the instruction count if this was not a label
            if command_type != "L":
               instruction += 1

      #
      # second pass - build the symbol table for variables
      #

      parser = Parser(self.source_filename)

      # the memory location for the next variable
      variable_address = 16

      # parse each command
      while parser.hasMoreCommands():
         # advance to the next command
         parser.advance()

         # parse the command type and look for symbols
         command_type = parser.commandType()
         if command_type == "A":
            # look for a variable value symbol
            symbol = parser.symbol()
            if symbol[0] not in map(str, range(0, 10)):
               # the symbol is not a number; that is, it is actually a symbol
               if symbol not in symbol_table:
                  symbol_table.addEntry(symbol, variable_address)
                  variable_address += 1

      #
      # third pass - generate assembly
      #

      parser = Parser(self.source_filename)
      code = Code()

      # parse all commands
      while parser.hasMoreCommands():
         # advance to the next command
         parser.advance()

         command_type = parser.commandType()
         if command_type == "A":
            # a command
            symbol = parser.symbol()
            if symbol in symbol_table:
               symbol = symbol_table.getAddress(symbol)

            symbol_binary = code.decimalToBinary(symbol)

            self.destination_file.write("0" + symbol_binary + "\n")
         elif command_type == "C":
            # c command
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())

            self.destination_file.write("111" + comp + dest + jump + "\n")
         elif command_type == "L":
            # label - do nothing in this stage
            pass
         else:
            # unknown command
            raise Exception("ERROR: Unknown command type encountered")

      # close the output file
      self.destination_file.close()
