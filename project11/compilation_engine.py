# the "compilation engine" (really the parser) for jack

# note: for all "compile" sub-methods, the token is expected to have already
# been advanced onto the token that starts the compilation; on return,
# the current token will be the first token following the statement
# the exception is compile_class, which is called before advancing onto the
# first token in the file

from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from vmwriter import VMWriter

class CompilationEngine(object):
   # the destination file for writing
   destination_file = None

   # the tokenizer for the input file
   tokenizer = None

   # current indentation level
   indent = 0

   # symbol table
   symbol_table = SymbolTable()

   # vm writer
   vm_writer = None

   # the class name
   class_name = ""

   # indicies for if and while loops
   while_index = 0
   if_index = 0

   # the constructor for compiling a single class
   # the next method to be called after construction must be compile_class
   # source_filename must be a single file, not a directory
   def __init__(self, source_filename):
      # destination filename
      # if the original extension was .jack, then make the extension .vm
      # if the original extension was not .jack, then append .vm
      if source_filename.lower().endswith(".jack"):
         destination_filename = source_filename[:-5] + ".vm"
      else:
         destination_filename = source_filename + ".vm"

      # open the destination filename for writing
      self.destination_file = open(destination_filename, 'w')

      # create a tokenizer for the input file
      self.tokenizer = JackTokenizer(source_filename)

      # create the vm writer
      self.vm_writer = VMWriter(self.destination_file)

   # compiles a complete class and closes the output file
   def compile_class(self):
      # class keyword
      tt, t = self._token_next(True, "KEYWORD", "class")

      # name of class
      tt, t = self._token_next(True, "IDENTIFIER")
      self.class_name = t

      # open brace
      tt, t = self._token_next(True, "SYMBOL", "{")

      # one or more variable declarations
      self.tokenizer.advance()
      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t in ["field", "static"]:
            self.compile_class_var_dec()
         else:
            # stop trying to process variable declarations
            break

      # one or more subroutine declarations
      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t in ["constructor", "function", "method"]:
            self.compile_subroutine()
         else:
            # stop trying to process functions
            break

      # close brace
      # do not advance because we already advanced upon exiting the last loop
      tt, t = self._token_next(False, "SYMBOL", "}")

      # done with compilation; close the output file
      self.destination_file.close()

   # compiles a static declaration or field declaration
   def compile_class_var_dec(self):
      # compile the variable declaration
      # False means this is a class (not a subroutine)
      self.compile_var_dec(False)

   # compiles a complete method, function, or constructor
   def compile_subroutine(self):
      # start of subroutine
      self.symbol_table.start_subroutine()

      # constructor, function, or method keyword
      tt, type = self._token_next(False, "KEYWORD")
      if type == "constructor":
         # TODO
         pass
      elif type == "function":
         # TODO
         pass
      elif type == "method":
         # TODO
         pass
      else:
         print "WARNING: Expected constructor, function, or name; got", type

      # type of the return value
      # can be either keyword (void) or an identifier (any type)
      tt, t = self._token_next(True)

      # name of the method/function/constructor
      tt, name = self._token_next(True)
      name = self.class_name + "." + name

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")

      # arguments
      self.tokenizer.advance()
      self.compile_parameter_list()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")

      # opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")

      # variable declarations
      self.tokenizer.advance()
      num_locals = 0
      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t == "var":
            num_locals += self.compile_var_dec()
         else:
            # stop trying to process variable declarations
            break

      # write the function
      self.vm_writer.write_function(name, num_locals)

      # statements
      self.compile_statements()

      # closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")

      self.tokenizer.advance()

   # compiles a (possibly empty) parameter list, not including the enclosing
   # parentheses
   def compile_parameter_list(self):
      num_args = 0

      # check for empty list
      tt, t = self._token_next(False)
      if tt == "SYMBOL" and t == ")":
         # the parameter list was empty; do not process any more
         pass
      else:
         # there are things in the parameter list
         while True:
            # keyword (variable type)
            tt, type = self._token_next(False)

            # identifier (variable name)
            tt, name = self._token_next(True)

            # the kind is always an arg, since these are all parameters to the
            # function
            kind = SymbolTable.ARG

            # define the variable in the symbol table
            self.symbol_table.define(name, type, kind)
            num_args += 1

            # possible comma
            tt, t = self._token_next(True)
            if tt != "SYMBOL" or t != ",":
               # not a comma; stop processing parameters
               break

            self.tokenizer.advance()

      return num_args

   # compiles a var declaration
   # if subroutine is true, only the var keyword can be used
   # if subroutine is false, only the static and field keywords can be used
   def compile_var_dec(self, subroutine=True):
      # the keyword to start the declaration
      tt, kind = self._token_next(False, "KEYWORD")

      # the number of variables compiled
      num_vars = 0

      # check for required types
      if subroutine:
         if kind == "var":
            kind = SymbolTable.VAR
         else:
            print "WARNING: expecting var, but received %s" % (str(kind))
      else:
         if kind == "static":
            kind = SymbolTable.VAR
         elif kind == "field":
            kind = SymbolTable.FIELD
         else:
            print "WARNING: expecting static or field, but received %s" % (str(kind))

      # type of the declaration
      # could be an identifier or a keyword (int, etc)
      tt, type = self._token_next(True)

      # name of the declaration
      tt, name = self._token_next(True, "IDENTIFIER")

      # define the variable in the symbol table
      self.symbol_table.define(name, type, kind)
      num_vars += 1

      # can support more than one identifier name, to declare more than one
      # variable, separated by commas; process the 2nd-infinite variables
      self.tokenizer.advance()
      while True:
         tt, t = self._token_next(False)
         if tt == "SYMBOL" and t == ",":
            # another variable name follows
            tt, name = self._token_next(True, "IDENTIFIER")

            # define the variable in the symbol table
            self.symbol_table.define(name, type, kind)
            num_vars += 1

            self.tokenizer.advance()
         else:
            # no more variable names
            break

      # should be on the semicolon at the end of the line
      tt, t = self._token_next(False, "SYMBOL", ";")

      self.tokenizer.advance()

      return num_vars

   # compiles a sequence of statements, not including the enclosing {}
   def compile_statements(self):
      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t in ["do", "let", "while", "return", "if"]:
            # call compile_t, where t is the type of compilation we want
            token = getattr(self, "compile_" + t)()
         else:
            # not a statement; stop processing statements
            break

   # compiles a do statement
   def compile_do(self):
      # do keyword
      tt, t = self._token_next(False, "KEYWORD", "do")

      # subroutine call
      self.tokenizer.advance()
      self.compile_subroutine_call()

      # do statements do not have a return value, so eliminate the return
      # off of the stack
      self.vm_writer.write_pop(self.vm_writer.TEMP, 0)

      # semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")

      self.tokenizer.advance()

   # compiles a let statement
   def compile_let(self):
      # let keyword
      tt, t = self._token_next(False, "KEYWORD", "let")

      # variable name
      tt, name = self._token_next(True, "IDENTIFIER")

      # possible brackets for array
      tt, t = self._token_next(True)
      if tt == "SYMBOL" and t == "[":
         # TODO
         # write bracket
         self._write(tt, t)

         # compile the expression
         self.tokenizer.advance()
         self.compile_expression()

         # closing bracket
         tt, t = self._token_next(False, "SYMBOL", "]")
         self._write(tt, t)

         # advance to the next token, since we are expected to be on the = for
         # the next line
         self.tokenizer.advance()

      # equals sign
      tt, t = self._token_next(False, "SYMBOL", "=")

      # expression
      self.tokenizer.advance()
      self.compile_expression()

      # pop to the variable name
      segment, index = self._resolve_symbol(name)
      self.vm_writer.write_pop(segment, index)

      # semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")

      self.tokenizer.advance()

   # compiles a while statement
   def compile_while(self):
      # labels for this while loop
      self.while_index += 1
      while_start = "WHILE_START_%d" % (self.while_index)
      while_end = "WHILE_END_%d" % (self.while_index)

      # while keyword
      tt, t = self._token_next(False, "KEYWORD", "while")

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")

      # label for the start of the while statement
      self.vm_writer.write_label(while_start)

      # the expression that is the condition of the while statement
      self.tokenizer.advance()
      self.compile_expression()

      # the closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")

      # the result of the evaluation is now on the stack
      # if false, then goto to the end of the loop
      # to do this, negate and then call if-goto
      self.vm_writer.write_arithmetic("not")
      self.vm_writer.write_if(while_end)

      # the opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")

      # the statments that is the body of the while loop
      self.tokenizer.advance()
      self.compile_statements()

      # the closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")

      # after the last statement of the while loop
      # need to jump back up to the top of the loop to evaluate again
      self.vm_writer.write_goto(while_start)

      # label at the end of the loop
      self.vm_writer.write_label(while_end)

      self.tokenizer.advance()

   # compiles a return statement
   def compile_return(self):
      # return keyword
      tt, t = self._token_next(False, "KEYWORD", "return")

      # possible expression to return
      tt, t = self._token_next(True)
      if tt != "SYMBOL" and t != ";":
         self.compile_expression()
      else:
         # no return expression; return 0
         self.vm_writer.write_push(self.vm_writer.CONST, 0)

      # ending semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")

      self.vm_writer.write_return()

      self.tokenizer.advance()

   # compiles a if statement, including a possible trailing else clause
   def compile_if(self):
      # it is more efficient in an if-else case to have the else portion first
      # in the code when testing, but we use the less-efficient but
      # easier-to-write true-false pattern here

      # labels for this if statement
      self.if_index += 1
      if_false = "IF_FALSE_%d" % (self.if_index)
      if_end = "IF_END_%d" % (self.if_index)

      # if keyword
      tt, t = self._token_next(False, "KEYWORD", "if")

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")

      # expression of if statement
      self.tokenizer.advance()
      self.compile_expression()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")

      # the result of the evaluation is now on the stack
      # if false, then goto the false label
      # if true, fall through to executing code
      # if there is no else, then false and end are the same, but having two
      # labels does not increase code size
      self.vm_writer.write_arithmetic("not")
      self.vm_writer.write_if(if_false)

      # opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")

      # statements for true portion
      self.tokenizer.advance()
      self.compile_statements()

      # closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")

      tt, t = self._token_next(True)
      if tt == "KEYWORD" and t == "else":
         # else statement exists

         # goto the end of the if statement at the end of the true portion
         self.vm_writer.write_goto(if_end)

         # label for the start of the false portion
         self.vm_writer.write_label(if_false)

         # opening brace
         tt, t = self._token_next(True, "SYMBOL", "{")

         # statements
         self.tokenizer.advance()
         self.compile_statements()

         # closing brace
         tt, t = self._token_next(False, "SYMBOL", "}")

         # end label
         self.vm_writer.write_label(if_end)

         # advance tokenizer only if we are in the else, since otherwise the
         # token was advanced by the else check
         self.tokenizer.advance()
      else:
         # no else portion; only put in a label for false, since end is not
         # used
         self.vm_writer.write_label(if_false)

   # compiles an expression (one or more terms connected by operators)
   def compile_expression(self):
      # the first term
      self.compile_term()

      # finish any number of operators followed by terms
      while True:
         tt, t = self._token_next(False)
         if tt == "SYMBOL" and t in "+-*/&|<>=":
            # found an operator
            # postfix order - add the next term and then do the operator

            # the next term
            self.tokenizer.advance()
            self.compile_term()

            # the operator
            if t == "+":
               self.vm_writer.write_arithmetic("add")
            if t == "-":
               self.vm_writer.write_arithmetic("sub")
            if t == "=":
               self.vm_writer.write_arithmetic("eq")
            if t == ">":
               self.vm_writer.write_arithmetic("gt")
            if t == "<":
               self.vm_writer.write_arithmetic("lt")
            if t == "&":
               self.vm_writer.write_arithmetic("and")
            if t == "|":
               self.vm_writer.write_arithmetic("or")
            if t == "*":
               self.vm_writer.write_call("Math.multiply", 2)
            if t == "/":
               self.vm_writer.write_call("Math.divide", 2)
         else:
            # no term found; done parsing the expression
            break

   # compiles a term
   # this routine is faced with a slight difficulty when trying to decide
   # between some of the alternative parsing rules. specifically, if the
   # current token is an identifier, the routine must distinguish between a
   # variable, an array entry, and a subroutine call. a single lookahead token,
   # which may be one of [, (, or ., suffices to distinguish between the three
   # possibilities. any other token is not part of this term and should not
   # be advanced over.
   def compile_term(self):
      # a term: integer_constant | string_constant | keyword_constant |
      # varname | varname[expression] | subroutine_call | (expression) |
      # unary_op term
      tt, t = self._token_next(False)
      if tt == "INT_CONST":
         self.vm_writer.write_push(self.vm_writer.CONST, t)

         # advance for the next statement
         self.tokenizer.advance()
      elif tt == "STRING_CONST":
         # TODO

         # advance for the next statement
         self.tokenizer.advance()
      elif tt == "KEYWORD":
         if t == "true":
            # true is -1, which is 0 negated
            self.vm_writer.write_push(self.vm_writer.CONST, 0)
            self.vm_writer.write_arithmetic("not")
         elif t == "false" or t == "null":
            self.vm_writer.write_push(self.vm_writer.CONST, 0)
         elif t == "this":
            # since we must be within a method to use this, argument 0
            # must be the current object
            # FIXME - possible other ways to reference
            self.vm_writer.write_push(self.vm_writer.ARG, 0)

         # advance for the next statement
         self.tokenizer.advance()
      elif tt == "SYMBOL" and t == "(":
         # ( expression )

         # parse the expression
         self.tokenizer.advance()
         self.compile_expression()

         # closing parenthesis
         tt, t = self._token_next(False, "SYMBOL", ")")

         # advance for the next statement
         self.tokenizer.advance()

      elif tt == "SYMBOL" and t in "-~":
         # unary_op term
         # postfix order - add the next term and then do the operator

         # parse the rest of the term
         self.tokenizer.advance()
         self.compile_term()

         # write the unary operation
         if t == "-":
            self.vm_writer.write_arithmetic("neg")
         elif t == "~":
            self.vm_writer.write_arithmetic("not")

      elif tt == "IDENTIFIER":
         # varname, varname[expression], subroutine_call

         # do not write the identifer yet

         # get the next bit of the expression
         # if it is a [, then array; if it is a ( or ., then subroutine call
         # if none of above, then pass over
         tt2, t2 = self._token_next(True)

         if tt2 == "SYMBOL" and t2 in "(.":
            # subroutine call
            # back up and then compile the subroutine call
            self.tokenizer.retreat()

            self.compile_subroutine_call()
         elif tt2 == "SYMBOL" and t2 == "[":
            # TODO - handle arrays
            # array
            # write identifier
            self._write(tt, t)

            # write bracket
            self._write(tt2, t2)

            # compile the expression
            self.tokenizer.advance()
            self.compile_expression()

            # closing bracket
            tt, t = self._token_next(False, "SYMBOL", "]")
            self._write(tt, t)

            # advance for the next statement
            self.tokenizer.advance()
         else:
            # none of above - just a single identifier
            segment, index = self._resolve_symbol(t)
            self.vm_writer.write_push(segment, index)

      else:
         # unknown
         print "WARNING: Unknown term expression object:", tt, t

   # compiles a (possible empty) comma-separated list of expressions
   def compile_expression_list(self):
      num_args = 0

      # check for empty list
      tt, t = self._token_next(False)
      if tt == "SYMBOL" and t == ")":
         # the parameter list was empty; do not process any more
         pass
      else:
         # there are things in the parameter list
         while True:
            # expression to pass
            self.compile_expression()
            num_args += 1

            # possible comma
            tt, t = self._token_next(False)
            if tt == "SYMBOL" and t == ",":
               self.tokenizer.advance()
            else:
               # not a comma; stop processing parameters
               break

      return num_args

   # compiles a subroutine call
   # two cases:
   # - subroutineName(expressionList)
   # - (class|var).subroutineName(expressionList)
   def compile_subroutine_call(self):
      # first part of name
      tt, name1 = self._token_next(False, "IDENTIFIER")

      # a dot and another name may exist, or it could be a parenthesis
      name2 = None
      tt, t = self._token_next(True)
      if tt == "SYMBOL" and t == ".":
         # the name after the dot
         tt, name2 = self._token_next(True, "IDENTIFIER")

         # advance so that we are on the parenthesis
         self.tokenizer.advance()

      # determine if this is a method call
      # three possibilities
      # - class.func() - function call
      # - var.func()   - method call
      # - func()       - method call on current object
      if self.symbol_table.contains(name1):
         method_call = True
         local_call = False
      elif name2 == None:
         method_call = True
         local_call = True
      else:
         method_call = False

      # if a method call, push variable name1
      # this a method call if the symbol table contains name1 and name2 exists
      # OR name1 is a method in the current object
      if method_call and local_call:
         # push the current object onto the stack as a hidden argument
         # since we must be within a method to make a local call, argument 0
         # must be the current object
         # FIXME - possible other ways to reference
         self.vm_writer.write_push(self.vm_writer.ARG, 0)
      elif method_call and not local_call:
         # push the variable onto the stack as a hidden argument
         segment, index = self._resolve_symbol(name1)
         self.vm_writer.write_push(segment, index)

      # opening parenthesis
      tt, t = self._token_next(False, "SYMBOL", "(")

      # expression list
      self.tokenizer.advance()
      num_args = self.compile_expression_list()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")

      # write the call
      if method_call and local_call:
         # methd + <blank>

         # get the name of the vm function to call
         classname = self.class_name
         vm_function_name = classname + "." + name1

         # increase arguments by 1, since there is the hidden "this"
         num_args += 1

         # make the call
         self.vm_writer.write_call(vm_function_name, num_args)

      elif method_call and not local_call:
         # variable name + method

         # get the name of the vm function to call
         classname = self.symbol_table.get(name1)[1]
         vm_function_name = classname + "." + name2

         # increase arguments by 1, since there is the hidden "this"
         num_args += 1

         # make the call
         self.vm_writer.write_call(vm_function_name, num_args)
      else:
         # get the name of the vm function to call
         vm_function_name = name1 + "." + name2

         # make the call
         self.vm_writer.write_call(vm_function_name, num_args)

      self.tokenizer.advance()

   # returns the token_type and token of the next token after advancing the
   # tokenizer before reading if advance is True
   def _token_next(self, advance=False, expected_type=None, expected_value=None):
      # advance the tokenizer, if requested
      if advance:
         self.tokenizer.advance()

      # get the token type and the token itself
      token_type = self.tokenizer.token_type()
      token = str(getattr(self.tokenizer, token_type.lower())())

      if expected_type and token_type != expected_type:
         print "WARNING: Type", token_type, "found; expected", expected_type
         import traceback, sys
         traceback.print_stack()
         sys.exit(1)
      if expected_value and token != expected_value:
         print "WARNING: Value", token, "found; expected", expected_value
         import traceback, sys
         traceback.print_stack()
         sys.exit(1)

      return token_type, token

   # writes the given token to the output file
   def _write(self, token_type, token):
      # lowercase for tag name
      token_type = token_type.lower()

      # special types
      token_type = token_type.replace("int_const", "integerConstant")
      token_type = token_type.replace("string_const", "stringConstant")

      # special values to replace for output
      s = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "&": "&amp;"}
      for s, r in s.iteritems():
         token = token.replace(s, r)

      # print the token type and token to the file
      output = ['<', token_type, '>', ' ', token, ' ', '</', token_type,
            '>', '\n']
      self.destination_file.write(self._indent("".join(output)))

   # starts an XML block
   def _start_block(self, block_name):
      self.destination_file.write(self._indent("<" + block_name + ">\n"))
      self.indent += 2

   # ends an XML block
   def _end_block(self, block_name):
      self.indent -= 2
      self.destination_file.write(self._indent("</" + block_name + ">\n"))

   # indents a single line of text at the current indentation level
   def _indent(self, text):
      return " " * self.indent + text

   # convets a symbol table type into a segment type
   def _type_to_segment(self, type):
      if type == self.symbol_table.STATIC:
         return self.vm_writer.STATIC
      elif type == self.symbol_table.FIELD:
         return self.vm_writer.THIS
      elif type == self.symbol_table.ARG:
         return self.vm_writer.ARG
      elif type == self.symbol_table.VAR:
         return self.vm_writer.LOCAL
      else:
         print "ERROR: Bad type %s" % (str(type))
 
   # resolves the symbol from the symbol table
   # the segment and index is returned as a 2-tuple
   def _resolve_symbol(self, name):
      kind, type, index = self.symbol_table.get(name)
      return self._type_to_segment(kind), index
