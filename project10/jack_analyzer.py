# the analyzer module
# encapsulates the jack code analysis process

import os
import os.path

from jack_tokenizer import JackTokenizer

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
      # for each source filename
      for source_filename in self.source_filenames:
         # destination filename
         # if the original extension was .jack, then make the extension T.xml
         # if the original extension was not .jack, then append T.xml
         if source_filename.lower().endswith(".jack"):
            destination_filename = source_filename[:-5] + "T.xml"
         else:
            destination_filename = source_filename + "T.xml"

         # open the destination filename for writing
         destination_file = open(destination_filename, 'w')

         tokenizer = JackTokenizer(source_filename)

         # start <tokens>
         destination_file.write("<tokens>\n")

         # parse each token
         while tokenizer.has_more_tokens():
            # advance to the next token
            tokenizer.advance()

            # get the token type and the token itself
            token_type = tokenizer.token_type().lower()
            token = str(getattr(tokenizer, token_type.lower())())

            # special types
            token_type = token_type.replace("int_const", "integerConstant")
            token_type = token_type.replace("string_const", "stringConstant")

            # special values
            s = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "&": "&amp;"}
            for s, r in s.iteritems():
               token = token.replace(s, r)

            # print the token type and token to the file
            output = ['<', token_type, '>', ' ', token, ' ', '</', token_type,
                  '>', '\n']
            destination_file.write("".join(output))

         # end <tokens>
         destination_file.write("</tokens>\n")

         # close the output file
         destination_file.close()
