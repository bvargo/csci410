# the parser module
# encapsulates access to the input code; reads vm language commands, parses
# the commands, and access to the fields of each command also, all white space
# and comments are removed

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
   def has_more_commands(self):
      return bool(self.source)

   # reads the next command from the input and makes it the current command
   # it should be called only if has_more_commands is true
   def advance(self):
      if self.has_more_commands():
         self.current_command = self.source.pop(0)

   # returns the type of the current command
   # returns one of "A", for a commands, "C", for c commands, and "L", for
   # labels
   def commandType(self):
      current_command = self.current_command
      # TODO

   # returns the first argument of the current command
   # if the comamnd is of type C_ARITHMETIC, then the command itself (add,
   # sub, etc) is returned; should not be called if command type is C_RETURN
   def arg1(self):
      # TODO
      if self.commandType() == "C_ARITHMETIC":
         pass
      elif self.commandType() != "C_RETURN":
         pass

   # returns the second argument of the current command
   # should be called only if the command tyep is C_PUSH, C_POP, C_FUNCTION,
   # or C_CALL
   def arg1(self):
      if self.commandType() in ["C_PUSH", "C_POP", "C_FUNCTION"]:
         pass
