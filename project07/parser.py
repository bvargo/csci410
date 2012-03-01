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
   # commands are:
   # - C_ARITHMETIC, 
   # - C_PUSH,
   # - C_POP, 
   # - C_LABEL,
   # - C_GOTO, 
   # - C_IF, 
   # - C_FUNCTION, 
   # - C_RETURN, 
   # - C_CALL 
   def command_type(self):
      current_command = self.current_command
      parts = current_command.split()
      if parts[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
         return "C_ARITHMETIC"
      elif parts[0] == "push":
         return "C_PUSH"
      elif parts[0] == "pop":
         return "C_POP"
      elif parts[0] == "label":
         return "C_LABEL"
      elif parts[0] == "goto":
         return "C_GOTO"
      elif parts[0] == "if-goto":
         return "C_IF"
      elif parts[0] == "function":
         return "C_FUNCTION"
      elif parts[0] == "return":
         return "C_RETURN"
      elif parts[0] == "call":
         return "C_CALL"
      else:
         raise Error("Illegal command type: " + parts[0])

   # returns the first argument of the current command
   # if the comamnd is of type C_ARITHMETIC, then the command itself (add,
   # sub, etc) is returned; should not be called if command type is C_RETURN
   def arg1(self):
      current_command = self.current_command
      parts = current_command.split()

      if self.command_type() == "C_ARITHMETIC":
         return parts[0]
      elif self.command_type() != "C_RETURN":
         return parts[1]
      else:
         raise Error("Illegal call to arg1(): C_RETURN does not have arguments")

   # returns the second argument of the current command
   # should be called only if the command tyep is C_PUSH, C_POP, C_FUNCTION,
   # or C_CALL
   def arg2(self):
      if self.command_type() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
         current_command = self.current_command
         parts = current_command.split()
         try:
            return int(parts[2])
         except:
            raise Error("Not an integer: " + parts[2])
      else:
         raise Error("Illegal call to arg2(): " + self.command_type() + \
               " does not support a second argument")
