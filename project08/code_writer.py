# the code writer module
# translates vm commands into hack assembly code

class CodeWriter(object):
   # the destination file
   destination_file = None

   # the jump number, for different jump labels for comparisons
   jump_number = 0

   # the current vm file being parsed
   vm_filename = None

   # the current function name; the default is main
   function_name = "main"

   # a counter for the number of return address labels
   return_count = 0

   # constructor
   # saves the output file handle and writes the initialization code
   def __init__(self, destination_file):
      # save the file handle
      self.destination_file = destination_file

      # write the initialization code to the file
      self.write_init()


   # informs the code writer that the translation of a new VM file has started
   def set_filename(self, filename):
      # store just the basename of the file
      # any dots in the basename are removed
      self.vm_filename = ''.join(filename.split("/")[-1].split(".")[:-1])

      self.destination_file.write("""
// ---------------------------------------------------------------------------
// start of file %s
// ---------------------------------------------------------------------------
 """ % (self.vm_filename))

   # writes bootstrap code
   def write_init(self):
      self.destination_file.write("""
//
// bootstrap code
//

// the stack pointer must be set to 256 upon program start, by convention
@256
D=A
@SP
M=D

// call Sys.init 0
// cheat a little bit by not actually storing values, since we will never
// return to this function; we must still adjust the stack pointer, since the
// test scripts expect the values to be saved

// set the stack pointer
@5
D=A
@SP
M=M+D

// set LCL to SP
@SP
D=M
@LCL
M=D

// run!
@Sys.init
0; JMP
""")

   # writes the assembly code for the translation of an arithmetic command
   def write_arithemtic(self, command):
      if command in ["add", "sub", "and", "or"]:
         # simple command that consumes two operands from the stack
         self.destination_file.write(self.arithmetic_add_sub_and_or(command))
      elif command in ["neg", "not"]:
         # command that consumes one operand from the stack
         self.destination_file.write(self.arithmetic_neg_not(command))
      elif command in ["gt", "lt", "eq"]:
         # complex command that consumes two operands from the stack
         self.destination_file.write(self.arithmetic_gt_lt_eq(command))
      else:
         raise Exception("Arithmetic command " + command + " not handled.")

   # writes the assembly code for a push or pop operation
   def write_push_pop(self, command, segment, index):
      if command == "C_PUSH":
         if segment == "constant":
            self.destination_file.write(self.push_constant(index))
         elif segment in ["argument", "local", "this", "that"]:
            self.destination_file.write(self.push_double_pointer(segment, index))
         elif segment in ["pointer", "temp", "static"]:
            # pointer is RAM[3-4] (this and that), and temp is RAM[5-12]
            # static is allocated by the assembler
            self.destination_file.write(self.push_stationary(segment, index))
         else:
            raise Exception("Invalid segment type " + segment + " for push")
      elif command == "C_POP":
         if segment in ["argument", "local", "this", "that"]:
            self.destination_file.write(self.pop_double_pointer(segment, index))
         elif segment in ["pointer", "temp", "static"]:
            # pointer is RAM[3-4] (this and that), and temp is RAM[5-12]
            # static is allocated by the assembler
            self.destination_file.write(self.pop_stationary(segment, index))
         else:
            raise Exception("Invalid segment type " + segment + " for pop")

   # writes a label command
   def write_label(self, label):
      self.destination_file.write("""
//
// label %s
//

(%s)
""" % (label, self.function_name + "$" + label))

   # writes a goto command
   def write_goto(self, label):
      self.destination_file.write("""
//
// goto %s
//

@%s
0;JMP
""" % (label, self.function_name + "$" + label))

   # writes an if-goto command
   def write_if(self, label):
      self.destination_file.write("""
//
// if-goto %s
//

// move the stack pointer back by 1
@SP
AM=M-1
// read the last data on the stack
D=M
// jump to label if D is not 0
@%s
D;JNE
""" % (label, self.function_name + "$" + label))

   # writes a call command
   def write_call(self, function_name, num_args):
      # create the return address label
      self.return_count += 1
      return_address_label = "RETURN" + str(self.return_count)

      # generate the code
      code = ["""
//
// call %s %s
//

// push return-address-label (%s)
""" % (function_name, num_args, return_address_label)]

      # push return-address-label
      code.append(self.push_constant(return_address_label))

      # push LCL
      code.append("// push LCL\n")
      code.append(self.push_stationary("LCL", 0))

      # push ARG
      code.append("// push ARG\n")
      code.append(self.push_stationary("ARG", 0))

      # push THIS
      code.append("// push THIS\n")
      code.append(self.push_stationary("THIS", 0))

      # push THAT
      code.append("// push THAT\n")
      code.append(self.push_stationary("THAT", 0))

      # ARG = SP - n - 5
      code.append("""
// ARG = SP - %d - 5
@SP
D=M
@%d
D=D-A
@5
D=D-A
@ARG
M=D
""" % (num_args, num_args))

      # LCL = SP
      code.append("""
// LCL = SP
@SP
D=M
@LCL
M=D
""")

      # goto function_name
      code.append("""
// goto %s
@%s
0;JMP
""" % (function_name, function_name))

      # (return-address-label)
      code.append("""
// return-address-label (%s)
(%s)
""" % (return_address_label, return_address_label))

      # write the code to the file
      self.destination_file.write(''.join(code))

   # writes a return command
   def write_return(self):
      # generate the code
      code = ["""
//
// return
//

"""]

      # frame = LCL
      # put frame into R13
      code.append("""
// frame = LCL
@LCL
D=M
@R13
M=D
""")

      # ret = *(frame-5)
      # put ret into R14
      code.append("""
// ret = *(frame-5)
// D already contains frame
@5
A=D-A
D=M
@R14
M=D
""")

      # reposition the return value for the caller
      # *ARG = pop()
      code.append("""
// *ARG = pop()
@SP
AM=M-1
D=M
@ARG
A=M
M=D
""")

      # restore SP
      # SP = ARG+1
      code.append("""
// SP = ARG+1
// A contains the address stored at @ARG
D=A+1
@SP
M=D
""")

      # restore THAT
      # THAT = *(FRAME-1)
      code.append("""
// THAT = *(FRAME-1)
// D contains FRAME
A=D-1
D=M
@THAT
M=D
""")

      # restore THIS
      # THIS = *(FRAME-2)
      code.append("""
// THIS = *(FRAME-2)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D
""")

      # restore ARG
      # ARG = *(FRAME-3)
      code.append("""
// ARG = *(FRAME-3)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D
""")

      # restore LCL
      # LCL = *(FRAME-4)
      code.append("""
// LCL = *(FRAME-4)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D
""")

      # goto ret
      code.append("""
// goto ret
@R14
A=M
0;JMP
""")

      # write the code to the file
      self.destination_file.write(''.join(code))

   # writes a function command
   def write_function(self, function_name, num_local_variables):
      # save the current function name
      self.function_name = function_name

      # generate the code
      code = ["""
//
// function %s %d
//

(%s)
""" % (function_name, num_local_variables, function_name)]

      # push a zero to the stack for each local variable
      for i in range(0, num_local_variables):
         code.append(self.push_constant(0))

      # write the code to the file
      self.destination_file.write(''.join(code))

   # closes the output file
   def close(self):
      self.destination_file.close()

################################################################################

   # returns an add, sub, and, or or command
   def arithmetic_add_sub_and_or(self, command):
      # the symbol that represents the command
      if command == "add":
         command_symbol = "+"
      elif command == "sub":
         command_symbol = "-"
      elif command == "and":
         command_symbol = "&"
      elif command == "or":
         command_symbol = "|"

      # return the command
      return """
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
""" % (command, command_symbol)

################################################################################

   # returns a neg or not command
   def arithmetic_neg_not(self, command):
      # the symbol that represents the command
      if command == "neg":
         command_symbol = "-"
      elif command == "not":
         command_symbol = "!"

      # write the command
      return """
//
// BEGIN %s
//

// load the current stack pointer address, decrementing the value by 1, but
// not saving the new value
@SP
A=M-1
// modify the value at the end of the stack with the operation
M=%sM
""" % (command, command_symbol)

################################################################################

   # returns a gt, lt, or eq command
   def arithmetic_gt_lt_eq(self, command):
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
      return """
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
""" % (command, jump_number, jump, jump_number, jump_number, jump_number)

################################################################################

   def push_constant(self, index):
      return """
//
// BEGIN PUSH of value %s
//

// put the value to write into D
@%s
D=A
// load the current stack pointer address
@SP
A=M
// write the data value into the memory location
M=D
// store the new stack pointer into SP
@SP
M=M+1
""" % (index, index)

################################################################################

   # push from argument, local, this, or that
   def push_double_pointer(self, segment, index):
      # read from a double pointer

      # the name of the register to use as the base pointer
      if segment == "argument":
         segment_reg = "ARG"
      elif segment == "local":
         segment_reg = "LCL"
      elif segment == "this":
         segment_reg = "THIS"
      elif segment == "that":
         segment_reg = "THAT"

      # the initial code for this section
      code = """
//
// BEGIN PUSH of %s %d
//""" % (segment, index)

      # only calculate the offset if the index is not 0
      if index != 0:
         code += """
// load the address of the segment into D
@%s
D=M
// add the offset to get segment[index]
@%d
A=D+A""" % (segment_reg, index)
      else:
         # offset is 0 - just load the base pointer
         code += """
// load the address of the segment into A
@%s
A=M""" % (segment_reg)

      # the rest of the code
      code += """
// put the value to push onto the stack from memory into D
D=M
// load the current stack pointer address
@SP
A=M
// write the data value into the memory location
M=D
// store the new stack pointer into SP
@SP
M=M+1
"""
      return code

################################################################################

   # pushes a value onto the stack from a stationary address (pointer, temp,
   # or static)
   def push_stationary(self, segment, index):
      # the name of the stationary memory address to use
      if segment == "pointer" and index == 0:
         memory_location = "THIS"
      elif segment == "pointer" and index == 1:
         memory_location = "THAT"
      elif segment == "temp":
         memory_location = "R" + str(index + 5)
      elif segment in ["LCL", "ARG", "THIS", "THAT"]:
         memory_location = segment
      else:
         memory_location = self.vm_filename + ".static" + str(index)

      return """
//
// BEGIN PUSH of %s %d
//

// put the value to push into D
@%s
D=M
// load the current stack pointer address
@SP
A=M
// write the data value into the memory location
M=D
// store the new stack pointer into SP
@SP
M=M+1
""" % (segment, index, memory_location)


################################################################################

   # pop from argument, local, this, or that
   def pop_double_pointer(self, segment, index):
      # write to a double pointer

      # the name of the register to use as the base pointer
      if segment == "argument":
         segment_reg = "ARG"
      elif segment == "local":
         segment_reg = "LCL"
      elif segment == "this":
         segment_reg = "THIS"
      elif segment == "that":
         segment_reg = "THAT"

      # the initial code for this section
      code = """
// BEGIN POP of %s %d

// calculate the destination
// load the address of segment into D
@%s
D=M""" % (segment, index, segment_reg)

      # only calculate the offset if the index is not 0
      if index != 0:
         code += """
// add the offset to get segment[index]
@%d
D=D+A
""" % (index)
      # the rest of the code for this section
      code += """
// store the destination location in a temporary memory location (R13)
@R13
M=D

// load the value from the stack
// load the current stack pointer address, decrementing the value by
// 1, storing the new stack pointer
@SP
AM=M-1
// load the value at the end of the stack into D
D=M
// load the precomputed destination into A
@R13
A=M
// store D into the destination address
M=D
"""
      return code

################################################################################

   # pops a value from the stack into a stationary address (pointer, temp, or
   # static)
   def pop_stationary(self, segment, index):
      # the name of the stationary memory location to use
      if segment == "pointer" and index == 0:
         memory_location = "THIS"
      elif segment == "pointer" and index == 1:
         memory_location = "THAT"
      elif segment == "temp":
         memory_location = "R" + str(index + 5)
      else:
         memory_location = self.vm_filename + ".static" + str(index)

      return """
// BEGIN POP of %s %d

// load the value from the stack
// load the current stack pointer address, decrementing the value by
// 1, storing the new stack pointer
@SP
AM=M-1
// load the value at the end of the stack into D
D=M
// load the destination into A
@%s
// store D into the destination address
M=D
""" % (segment, index, memory_location)
