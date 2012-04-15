# the analyzer module
# encapsulates the jack code analysis process

import os
import os.path

from compilation_engine import CompilationEngine

class JackAnalyzer(object):
   # source filenames
   # source filenames is a list because more than on jack file can be read
   source_filenames = []

   # initialize the translator for the source filename
   # if the source or destination file could not be opened, then an IOError is
   # thrown; likewise, if a directory is passed and does not contain any .jack
   # files, then an Error is raised
   def __init__(self, source_filename):
      source_filename = source_filename.strip()

      # remove a trailing / or \, if present
      if source_filename[-1] in ["/", "\\"]:
         source_filename = source_filename[:-1]

      if os.path.isdir(source_filename):
         # find all the .jack files in the given directory
         self.source_filenames = [f for f in os.listdir(source_filename) if f.lower().endswith(".jack")]

         # make sure that a full path to the file is provided in the list
         fullpath = lambda a: source_filename + "/" + a
         self.source_filenames = map(fullpath, self.source_filenames)
      else:
         self.source_filenames = [source_filename]

      # try to open each source file
      # on failure, IOError is thrown
      for source_filename in self.source_filenames:
         source_file = open(source_filename, 'r')

         # the source file can be closed, since the tokenizer will open it for each
         # pass; it was opened in order to ensure that it could be opened and
         # read
         source_file.close()

   # analyze the source
   def analyze(self):
      # for each source filename, compile the class
      for source_filename in self.source_filenames:
         compiler = CompilationEngine(source_filename)
         compiler.compile_class()
