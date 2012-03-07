# the assembler module
# encapsulates the entire vm translation process

import os
import os.path

from code_writer import CodeWriter
from parser import Parser

class VMTranslator(object):
   # source and destination filenames and file handles
   # source filenames is a list because more than on VM file can be read
   source_filenames = []
   destination_filename = ""
   destination_file = None

   # initialize the translator for the source filename
   # if the source or destination file could not be opened, then an IOError is
   # thrown; likewise, if a directory is passed and does not contain any .vm
   # files, then an Error is raised
   def __init__(self, source_filename):
      source_filename = source_filename.strip()

      # remove a trailing / or \, if present
      if source_filename[-1] in ["/", "\\"]:
         source_filename = source_filename[:-1] 

      # if the original extension was .vm, then make the new extension .asm
      # if the original extension was not .vm, then append .asm
      if source_filename.lower().endswith(".vm"):
         destination_filename = source_filename[:-3] + ".asm"
      else:
         destination_filename = source_filename + ".asm"

      if os.path.isdir(source_filename):
         # find all the .vm files in the given directory
         self.source_filenames = [f for f in os.listdir(source_filename) if f.lower().endswith(".vm")]

         # make sure that a full path to the file is provided in the list
         fullpath = lambda a: source_filename + "/" + a
         self.source_filenames = map(fullpath, self.source_filenames)
      else:
         self.source_filenames = [source_filename]

      # save the destination filename
      self.destination_filename = destination_filename

      # try to open the destination file
      # on failure, IOError is thrown
      self.destination_file = open(destination_filename, 'w')

      # try to open each source file
      # on failure, IOError is thrown
      for source_filename in self.source_filenames:
         source_file = open(source_filename, 'r')

         # the source file can be closed, since the parser will open it for each
         # pass; it was opened in order to ensure that it could be opened and
         # read
         source_file.close()

   # translate the source
   def translate(self):
      code_writer = CodeWriter(self.destination_file)

      # for each source filename
      for source_filename in self.source_filenames:
         parser = Parser(source_filename)
         code_writer.set_filename(source_filename)

         # parse each command
         while parser.has_more_commands():
            # advance to the next command
            parser.advance()

            # parse the command type
            command_type = parser.command_type()
            if command_type == "C_ARITHMETIC":
               code_writer.write_arithemtic(parser.arg1())
            elif command_type in ["C_POP", "C_PUSH"]:
               code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2())
            else:
               raise Error("Not implemented: command type " + command_type)

      # close the output file
      code_writer.close()
