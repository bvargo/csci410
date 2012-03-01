# the code writer module
# translates vm commands into hack assembly code

class CodeWriter(object):
   # the destination file
   destination_file = None

   # the jump number, for different jump labels for comparisons
   jump_number = 0

   # constructor
   # saves the output file handle
   def __init__(self, destination_file):
      self.destination_file = destination_file

   # informs the code writer that the translation of a new VM file has started
   def set_filename(self, filename):
      pass

   # writes the assembly code for the translation of an arithmetic command
   def write_arithemtic(self, command):
      if command in ["add", "sub", "and", "or"]:
         # simple command that consumes two operands from the stack
         
         # the symbol that represents the command
         if command == "add":
            command_symbol = "+"
         elif command == "sub":
            command_symbol = "-"
         elif command == "and":
            command_symbol = "&"
         elif command == "or":
            command_symbol = "|"

         # write the command
         self.destination_file.write("""
//
// BEGIN %s
//

// load the current stack pointer address, decrementing the value by 1
// store the new stack pointer address back to SP
@SP
AM=M-1
// load the value at the end of the stack
D=M
// move to the value two from the end of the stack
A=A-1
// compute the operation, saving the result to the location of the new end of
// the stack (2 consumed, 1 produced)
M=M%sD
""" % (command, command_symbol))
      elif command in ["neg", "not"]:
         # command that consumes one operand from the stack

         # the symbol that represents the command
         if command == "neg":
            command_symbol = "-"
         elif command == "not":
            command_symbol = "!"

         # write the command
         self.destination_file.write("""
//
// BEGIN %s
//

// load the current stack pointer address, decrementing the value by 1, but
// not saving the new value
@SP
A=M-1
// modify the value at the end of the stack with the operation
M=%sM
""" % (command, command_symbol))
      elif command in ["gt", "lt", "eq"]:
         # complex command that consumes two operands from the stack

         # the jump type for the command
         if command == "gt":
            jump = "JGT"
         elif command == "lt":
            jump = "JLT"
         elif command == "eq":
            jump = "JEQ"

         # increase the jump number
         # each comparison requires a different label for jumps
         self.jump_number += 1
         jump_number = self.jump_number

         # write the comamnd
         self.destination_file.write("""
//
// BEGIN %s
//

// load the current stack pointer address, decrementing the value by 1
// store the new stack pointer address back to SP
@SP
AM=M-1
// load the value at the end of the stack
D=M
// move to the value two from the end of the stack
A=A-1
// subtract the first value from the second, so we can jump relative to zero
D=M-D
// jump based on the value in D
@COMPARISON_%d
D;%s
// fall through the jump - jump did not happen, false
   @SP
   A=M-1
   M=0
   // jump to the end condition
   @COMPARISON_END_%d
   0;JMP
(COMPARISON_%d)
// jump did happen, true
   @SP
   A=M-1
   M=-1
(COMPARISON_END_%d)
""" % (command, jump_number, jump, jump_number, jump_number, jump_number))
      else:
         raise Error("Arithmetic command " + command + " not handled.")

   # writes the assembly code for a push or pop operation
   def write_push_pop(self, command, segment, index):
      if command == "C_PUSH":
         if segment == "constant":
            self.destination_file.write("""
//
// BEGIN PUSH of value %d
//

// put the value to write into D
@%d
D=A
// load the current stack pointer address
@SP
A=M
// write the data value into the memory location
M=D
// store the new stack pointer into SP
@SP
M=M+1
""" % (index, index))
         else:
            raise Error("Not implemented: segment type " + segment + " for push")
      elif command == "C_POP":
         """
         // EXAMPLE POP ROUTINE - replace DESTINATION as appropriate

         // load the current stack pointer address, decrementing the value by
         // 1
         @SP
         A=M-1
         // load the value at the end of the stack
         D=M
         // move A to the place where the new value will be written
         A=DESTINATION
         // write the value from the stack to the new location
         M=D
         // decrement the stack pointer
         @SP
         M=M-1
         """
         raise Error("Not implemented: segment type " + segment + " for pop")

   # closes the output file
   def close(self):
      self.destination_file.close()
