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
            # TODO: handle symbol

            symbol_binary = code.decimalToBinary(symbol)

            self.destination_file.write("0" + symbol_binary)
         elif command_type == "C":
            # c command
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())

            self.destination_file.write("111" + comp + dest + jump)
         elif command_type == "L":
            # label
            symbol = parser.symbol()

            # TODO: handle symbols
         else:
            # unknown command
            raise Exception("ERROR: Unknown command type encountered")

         self.destination_file.write("\n")

      # close the output file
      self.destination_file.close()
