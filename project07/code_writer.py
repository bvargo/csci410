# the code writer module
# translates vm commands into hack assembly code

class CodeWriter(object):
   # the destination file
   destionation_file = None

   # constructor
   # saves the output file handle
   def __init__(self, destination_file):
      self.destination_file = destination_file

   # informs the code writer that the translation of a new VM file has started
   def set_filename(self, filename):
      pass

   # writes the assembly code for the translation of an arithmetic command
   def write_arithemtic(self, command):
      pass

   # writes the assembly code for a push or pop operation
   def write_push_pop(self, command, segment, index):
      pass

   # closes the output file
   def close(self):
      pass
