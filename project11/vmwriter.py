# the vm writer module, which emits VM commands into a file

class VMWriter(object):
   # output stream
   output = None

   # segment constants
   CONST   = 0
   ARG     = 1
   LOCAL   = 2
   STATIC  = 3
   THIS    = 4
   THAT    = 5
   POINTER = 6
   TEMP    = 7
   segment_types = [CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP]
   segment_names = ["constant", "argument", "local", "static", "this", "that", "pointer", "temp"]

   # initialize the VM writer given an output stream
   def __init__(self, output):
      self.output = output

   # writes a push command
   # segment is one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
   def write_push(self, segment, index):
      if segment in self.segment_types:
         self.output.write("push %s %s\n" % \
                                 (self.segment_names[segment], str(index)))
      else:
         print "WARNING: Unknown segment type %s" % (str(segment))

   # writes a pop command
   # segment is one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
   def write_pop(self, segment, index):
      if segment in self.segment_types:
         self.output.write("pop %s %s\n" % \
                                 (self.segment_names[segment], str(index)))
      else:
         print "WARNING: Unknown segment type %s", str(segment)

   # writes an arithmetic command
   # command is one of ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
   def write_arithmetic(self, command):
      if command in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
         self.output.write(command + "\n")
      else:
         print "WARNING: Unknown command %s" % (command)

   # writes a label command
   def write_label(self, label):
      self.output.write("label %s\n" % (label))

   # writes a goto comamnd
   def write_goto(self, label):
      self.output.write("goto %s\n" % (label))

   # writes an if-goto command
   def write_if(self, label):
      self.output.write("if-goto %s\n" % (label))

   # writes a call command
   def write_call(self, name, num_args):
      self.output.write("call %s %s\n" % (name, str(num_args)))

   # writes a function command
   def write_function(self, name, num_locals):
      self.output.write("function %s %s\n" % (name, str(num_locals)))

   # writes a return command
   def write_return(self):
      self.output.write("return\n")
