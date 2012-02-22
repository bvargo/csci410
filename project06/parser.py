# the parser module
# encapsulates access to the input code; reasds assembly language commands,
# parses the comands, and provides access to the fields of each command
# also, all white space and comments are removed

# notes about symbols, constants, and comments:
# the rest of the language is defined in the book
#
# constants are non-negative and are written in decimal notation a symbol can
# be a sequence of letters, digits, _, ., $, : and may not begin with a digit
# labels are assigned to the instruction memory of the next instruction
# variables are assigned to the data memory consecutively starting at address
# 16
#
# predefined symbols:
# SP         0
# LCL        1
# ARG        2
# THIS       3
# THAT       4
# R0-R15     0-15
# SCREEN     16384
# KBD        24576
#
# comments begin with two slasses and go to the end of the line
# 

class Parser(object):
   # opens the filename and prepares to parse
   # if the file does not exist, then an exception is raised
   def __init__(self, filename):
      pass

   # are there more commands in the input?
   # returns a boolean
   def hasMoreCommands(self):
      pass

   # reads the next command from the input and makes it the current command
   # it should be called only if hasMoreCommands is true
   def advance(self):
      pass

   # returns the type of the current command
   # returns one of "A", for a commands, "C", for c commands, and "L", for
   # labels
   def commandType(self):
      pass

   # returns the symbol or decimal Xxx of the current command @Xxx or (Xxx)
   # should be called only when commandType is A or L
   def symbol(self):
      pass

   # returns the dest mnemonic of the current C command (28 possibilities)
   # should only be called when commandType is C
   def dest(self):
      pass

   # returns the comp mnemonic of the current C command (28 possibilities)
   # should only be called when commandType is C
   def comp(self):
      pass

   # returns the jump mnemonic in the current C command (8 possibilities)
   # should only be called when commandType is C
   def jump(self):
      pass
