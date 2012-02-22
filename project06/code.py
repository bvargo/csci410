# the code module
# translates hack assembly language mnemonics into binary codes

class Code(object):
   # returns the binary code of the dest mnemonic as ascii-encoded binary (3
   # digits)
   def dest(self, mnemonic):
      pass

   # returns the binary code of the comp mnemonic as ascii-encoded binary (7
   # digits)
   def comp(self, mnemonic):
      pass

   # returns the binary code of the jump mnemonic as ascii-encoded binary (3
   # digits)
   def jump(self, mnemonic):
      pass

   # converts the decimal representation to an ascii-encoded 15-digit binary
   # number
   # decimal can be either a string or an integer
   def decimalToBinary(decimal):
      pass
