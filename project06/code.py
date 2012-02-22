# the code module
# translates hack assembly language mnemonics into binary codes

class Code(object):
   # returns the binary code of the dest mnemonic as ascii-encoded binary (3
   # digits)
   def dest(self, mnemonic):
      dest = []

      if "A" in mnemonic:
         dest.append("1")
      else:
         dest.append("0")

      if "D" in mnemonic:
         dest.append("1")
      else:
         dest.append("0")

      if "M" in mnemonic:
         dest.append("1")
      else:
         dest.append("0")

      return "".join(dest)

   # returns the binary code of the comp mnemonic as ascii-encoded binary (7
   # digits)
   def comp(self, mnemonic):
      # a = 0
      if mnemonic == "0":
         return "0101010"
      elif mnemonic == "1":
         return "0111111"
      elif mnemonic == "-1":
         return "0111010"
      elif mnemonic == "D":
         return "0001100"
      elif mnemonic == "A":
         return "0110000"
      elif mnemonic == "!D":
         return "0001101"
      elif mnemonic == "!A":
         return "0110001"
      elif mnemonic == "-D":
         return "0001111"
      elif mnemonic == "-A":
         return "0110011"
      elif mnemonic == "D+1":
         return "0011111"
      elif mnemonic == "A+1":
         return "0110111"
      elif mnemonic == "D-1":
         return "0001110"
      elif mnemonic == "A-1":
         return "0110010"
      elif mnemonic == "D+A" or mnemonic == "A+D":
         return "0000010"
      elif mnemonic == "D-A":
         return "0010011"
      elif mnemonic == "A-D":
         return "0000111"
      elif mnemonic == "D&A" or mnemonic == "A&D":
         return "0000000"
      elif mnemonic == "D|A" or mnemonic == "A|D":
         return "0010101"
      # a = 1
      elif mnemonic == "M":
         return "1110000"
      elif mnemonic == "!M":
         return "1110001"
      elif mnemonic == "-M":
         return "1110011"
      elif mnemonic == "M+1":
         return "1110111"
      elif mnemonic == "M-1":
         return "1110010"
      elif mnemonic == "D+M" or mnemonic == "M+D":
         return "1000010"
      elif mnemonic == "D-M":
         return "1010011"
      elif mnemonic == "M-D":
         return "1000111"
      elif mnemonic == "D&M" or mnemonic == "M&D":
         return "1000000"
      elif mnemonic == "D|M" or mnemonic == "M|D":
         return "1010101"
      # error case
      else:
         raise Exception("Unknown comp mnemonic", mnemonic)

   # returns the binary code of the jump mnemonic as ascii-encoded binary (3
   # digits)
   def jump(self, mnemonic):
      if mnemonic == "JGT":
         return "001"
      elif mnemonic == "JEQ":
         return "010"
      elif mnemonic == "JGE":
         return "011"
      elif mnemonic == "JLT":
         return "100"
      elif mnemonic == "JNE":
         return "101"
      elif mnemonic == "JLE":
         return "110"
      elif mnemonic == "JMP":
         return "111"
      elif mnemonic == "null":
         return "000"
      else:
         raise Exception("Unknown jump mnemonic", mnemonic)

   # converts the decimal representation to an ascii-encoded 15-digit binary
   # number in 2's compliment
   # decimal can be either a string or an integer
   def decimalToBinary(self, decimal):
      decimal = int(decimal)
      return "".join([str((decimal >> i) & 1) for i in range(14, -1, -1)])

