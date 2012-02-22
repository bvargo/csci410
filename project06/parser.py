# the parser module
# encapsulates access to the input code; reasds assembly language commands,
# parses the comands, and provides access to the fields of each command
# also, all white space and comments are removed

class Parser(object):
   # list of source lines
   source = []

   # the current command as a string
   current_command = ""

   # opens the filename and prepares to parse
   # if the file does not exist, then an IOError is raised
   def __init__(self, source_filename):
      # open the file
      source_file = open(source_filename, 'r')

      # read and close the file
      source = source_file.readlines()
      source_file.close()

      # strip comments
      source = map(lambda a: a.split("//")[0], source)

      # strip whitespace
      source = map(lambda a: a.strip(), source)

      # remove blank lines
      source = [line for line in source if line]

      # save the source lines
      self.source = source

   # are there more commands in the input?
   # returns a boolean
   def hasMoreCommands(self):
      return bool(self.source)

   # reads the next command from the input and makes it the current command
   # it should be called only if hasMoreCommands is true
   def advance(self):
      if self.hasMoreCommands():
         self.current_command = self.source.pop(0)

   # returns the type of the current command
   # returns one of "A", for a commands, "C", for c commands, and "L", for
   # labels
   def commandType(self):
      current_command = self.current_command
      if "(" == current_command[0]:
         return "L"
      elif "@" == current_command[0]:
         return "A"
      else:
         return "C"

   # returns the symbol or decimal version of the current A or L command
   # for A commands, this returns the contents after the @
   # for L commands, this returns the name of the label
   # should be called only when commandType is A or L
   def symbol(self):
      if self.commandType() == "L":
         return self.current_command[1:-1]
      else:
         return self.current_command[1:]

   # returns the dest mnemonic of the current C command (28 possibilities)
   # should only be called when commandType is C
   def dest(self):
      if self.commandType() == "C":
         if "=" in self.current_command:
            return self.current_command.split("=")[0]
         else:
            return "null"

   # returns the comp mnemonic of the current C command (28 possibilities)
   # should only be called when commandType is C
   def comp(self):
      if self.commandType() == "C":
         current_command = self.current_command
         if "=" in current_command:
            return current_command.split("=")[1].split(";")[0]
         else:
            return current_command.split(";")[0]

   # returns the jump mnemonic in the current C command (8 possibilities)
   # should only be called when commandType is C
   def jump(self):
      if self.commandType() == "C":
         parts = self.current_command.split(";")
         if len(parts) == 1:
            return "null"
         elif len(parts) == 2:
            return parts[1]
         else:
            raise Exception("Unknown jump semantics")
