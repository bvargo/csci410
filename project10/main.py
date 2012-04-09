#!/usr/bin/env python

import sys

from jack_analyzer import JackAnalyzer

def main(args):
   if len(args) != 2:
      print "USAGE:", args[0], "[program.jack | program_directory]"
      print "\tprogram.jack is the source jack file"
      print "\tprogram_directory is a directory containing jack files"
      print "\tA XML file will be created from the source."
      print "\tThe output file will use the same prefix as the source, with a"
      print "\tT appended for the tokenized output, and the extension.xml will"
      print "\tbe used. For example, Main.jack creates MainT.xml and Main.xml"
      sys.exit(1)

   # the source filename
   source_filename = args[1]

   # create the tokenizer and tokenize the code
   try:
      analyzer = JackAnalyzer(source_filename)
      analyzer.analyze()
   except IOError:
      print "ERROR: Could not open source file or error writing to destination"

if __name__ == "__main__":
   main(sys.argv)
