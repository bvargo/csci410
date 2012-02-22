#!/usr/bin/env python

import sys

from assembler import Assembler

def main(args):
   if len(args) != 2:
      print "USAGE:", args[0], "program.asm"
      print "\tprogram.asm is the source asm file"
      print "\tA hack file will be created from the source file."
      print "\tThe output file will use the same prefix as the source, but"
      print "\tthe extension will be .hack"
      sys.exit(1)

   # the source filename
   source_filename = args[1]

   # create the assembler and assemble the code
   try:
      assembler = Assembler(source_filename)
      assembler.assemble()
   except IOError:
      print "ERROR: Could not open source file or error writing to destination"

if __name__ == "__main__":
   main(sys.argv)
