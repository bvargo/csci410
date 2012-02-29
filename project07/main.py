#!/usr/bin/env python

import sys

from vm_translator import VMTranslator

def main(args):
   if len(args) != 2:
      print "USAGE:", args[0], "[program.vm | program_directory]"
      print "\tprogram.vm is the source vm file"
      print "\tprogram_directory is a directory containing vm files"
      print "\tA asm file will be created from the source."
      print "\tThe output file will use the same prefix as the source, but"
      print "\tthe extension will be .asm"
      sys.exit(1)

   # the source filename
   source_filename = args[1]

   # create the translator and translate the code
   try:
      translator = VMTranslator(source_filename)
      translator.translate()
   except IOError:
      print "ERROR: Could not open source file or error writing to destination"

if __name__ == "__main__":
   main(sys.argv)
