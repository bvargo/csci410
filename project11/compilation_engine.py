# the "compilation engine" (really the parser) for jack

# note: for all "compile" sub-methods, the token is expected to have already
# been advanced onto the token that starts the compilation; on return,
# the current token will be the first token following the statement
# the exception is compile_class, which is called before advancing onto the
# first token in the file

from jack_tokenizer import JackTokenizer

class CompilationEngine(object):
   # the destination file for writing
   destination_file = None

   # the tokenizer for the input file
   tokenizer = None

   # current indentation level
   indent = 0

   # the constructor for compiling a single class
   # the next method to be called after construction must be compile_class
   # source_filename must be a single file, not a directory
   def __init__(self, source_filename):
      # destination filename
      # if the original extension was .jack, then make the extension T.xml
      # if the original extension was not .jack, then append T.xml
      if source_filename.lower().endswith(".jack"):
         destination_filename = source_filename[:-5] + ".xml"
      else:
         destination_filename = source_filename + ".xml"

      # open the destination filename for writing
      self.destination_file = open(destination_filename, 'w')

      # create a tokenizer for the input file
      self.tokenizer = JackTokenizer(source_filename)

   # compiles a complete class and closes the output file
   def compile_class(self):
      # start the class
      self._start_block("class")

      # class
      tt, t = self._token_next(True, "KEYWORD", "class")
      self._write(tt, t)

      # name of class
      tt, t = self._token_next(True, "IDENTIFIER")
      self._write(tt, t)

      # open brace
      tt, t = self._token_next(True, "SYMBOL", "{")
      self._write(tt, t)

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
      self._write(tt, t)

      # end the class
      self._end_block("class")

      # close the output file
      self.destination_file.close()

   # compiles a static declaration or field declaration
   def compile_class_var_dec(self):
      # start variable declaration
      self._start_block("classVarDec")

      # compile the variable declaration
      # False means don't print the tags
      self.compile_var_dec(False)

      # end variable declaration
      self._end_block("classVarDec")

   # compiles a complete method, function, or constructor
   def compile_subroutine(self):
      # start subroutine declaration
      self._start_block("subroutineDec")

      # constructor, function, or name keyword
      tt, t = self._token_next(False, "KEYWORD")
      self._write(tt, t)

      # type of the return value
      # can be either keyword (void) or an identifier (any type)
      tt, t = self._token_next(True)
      self._write(tt, t)

      # name of the method/function/constructor
      tt, t = self._token_next(True)
      self._write(tt, t)

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")
      self._write(tt, t)

      # arguments
      self.tokenizer.advance()
      self.compile_parameter_list()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")
      self._write(tt, t)

      # start body of subroutine
      self._start_block("subroutineBody")

      # opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")
      self._write(tt, t)

      # variable declarations
      self.tokenizer.advance()
      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t == "var":
            self.compile_var_dec()
         else:
            # stop trying to process variable declarations
            break

      # statements
      self.compile_statements()

      # closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")
      self._write(tt, t)

      # end body of subroutine
      self._end_block("subroutineBody")

      # finish subroutine declaration
      self._end_block("subroutineDec")

      self.tokenizer.advance()

   # compiles a (possibly empty) parameter list, not including the enclosing
   # parentheses
   def compile_parameter_list(self):
      self._start_block("parameterList")

      # check for empty list
      tt, t = self._token_next(False)
      if tt == "SYMBOL" and t == ")":
         # the parameter list was empty; do not process any more
         pass
      else:
         # there are things in the parameter list
         while True:
            # keyword (variable type)
            tt, t = self._token_next(False)
            self._write(tt, t)

            # identifier (variable name)
            tt, t = self._token_next(True)
            self._write(tt, t)

            # possible comma
            tt, t = self._token_next(True)
            if tt == "SYMBOL" and t == ",":
               self._write(tt, t)
            else:
               # not a comma; stop processing parameters
               break

            self.tokenizer.advance()

      self._end_block("parameterList")

   # compiles a var declaration
   def compile_var_dec(self, print_tags=True):
      if print_tags:
         self._start_block("varDec")

      # the keyword to start the declaration
      tt, t = self._token_next(False, "KEYWORD")
      self._write(tt, t)

      # type of the declaration
      # could be an identifier or a keyword (int, etc)
      tt, t = self._token_next(True)
      self._write(tt, t)

      # name of the declaration
      tt, t = self._token_next(True, "IDENTIFIER")
      self._write(tt, t)

      # can support more than one identifier name, to declare more than one
      # variable, separated by commas; process the 2nd-infinite variables
      self.tokenizer.advance()
      while True:
         tt, t = self._token_next(False)
         if tt == "SYMBOL" and t == ",":
            # write the comma
            self._write(tt, t)

            # another variable name follows
            tt, t = self._token_next(True, "IDENTIFIER")
            self._write(tt, t)

            self.tokenizer.advance()
         else:
            # no more variable names
            break

      # should be on the semicolon at the end of the line
      tt, t = self._token_next(False, "SYMBOL", ";")
      self._write(tt, t)

      self.tokenizer.advance()

      if print_tags:
         self._end_block("varDec")

   # compiles a sequence of statements, not including the enclosing {}
   def compile_statements(self):
      self._start_block("statements")

      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t in ["do", "let", "while", "return", "if"]:
            # call compile_t, where t is the type of compilation we want
            token = getattr(self, "compile_" + t)()
         else:
            # not a statement; stop processing statements
            break

      self._end_block("statements")

   # compiles a do statement
   def compile_do(self):
      self._start_block("doStatement")

      # do keyword
      tt, t = self._token_next(False, "KEYWORD", "do")
      self._write(tt, t)

      # subroutine call
      self.tokenizer.advance()
      self.compile_subroutine_call()

      # semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")
      self._write(tt, t)

      self._end_block("doStatement")
      self.tokenizer.advance()

   # compiles a let statement
   def compile_let(self):
      self._start_block("letStatement")

      # let keyword
      tt, t = self._token_next(False, "KEYWORD", "let")
      self._write(tt, t)

      # variable name
      tt, t = self._token_next(True, "IDENTIFIER")
      self._write(tt, t)

      # possible brackets for array
      tt, t = self._token_next(True)
      if tt == "SYMBOL" and t == "[":
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
      self._write(tt, t)

      # expression
      self.tokenizer.advance()
      self.compile_expression()

      # semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")
      self._write(tt, t)

      self._end_block("letStatement")
      self.tokenizer.advance()

   # compiles a while statement
   def compile_while(self):
      self._start_block("whileStatement")

      # while keyword
      tt, t = self._token_next(False, "KEYWORD", "while")
      self._write(tt, t)

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")
      self._write(tt, t)

      # the expression that is the condition of the while statement
      self.tokenizer.advance()
      self.compile_expression()

      # the closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")
      self._write(tt, t)

      # the opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")
      self._write(tt, t)

      # the statments that is the body of the while loop
      self.tokenizer.advance()
      self.compile_statements()

      # the closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")
      self._write(tt, t)

      self._end_block("whileStatement")
      self.tokenizer.advance()

   # compiles a return statement
   def compile_return(self):
      self._start_block("returnStatement")

      # return keyword
      tt, t = self._token_next(False, "KEYWORD", "return")
      self._write(tt, t)

      # possible expression to return
      tt, t = self._token_next(True)
      if tt != "SYMBOL" and t != ";":
         self.compile_expression()

      # ending semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")
      self._write(tt, t)

      self._end_block("returnStatement")
      self.tokenizer.advance()

   # compiles a if statement, including a possible trailing else clause
   def compile_if(self):
      self._start_block("ifStatement")

      # if keyword
      tt, t = self._token_next(False, "KEYWORD", "if")
      self._write(tt, t)

      # opening parenthesis
      tt, t = self._token_next(True, "SYMBOL", "(")
      self._write(tt, t)

      # expression of if statement
      self.tokenizer.advance()
      self.compile_expression()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")
      self._write(tt, t)

      # opening brace
      tt, t = self._token_next(True, "SYMBOL", "{")
      self._write(tt, t)

      # statements
      self.tokenizer.advance()
      self.compile_statements()

      # closing brace
      tt, t = self._token_next(False, "SYMBOL", "}")
      self._write(tt, t)

      tt, t = self._token_next(True)
      if tt == "KEYWORD" and t == "else":
         # else statement exists
         # write else
         seld._write(tt, t)

         # opening brace
         tt, t = self._token_next(False, "SYMBOL", "{")
         self._write(tt, t)

         # statements
         self.compile_statements()

         # closing brace
         tt, t = self._token_next(False, "SYMBOL", "}")
         self._write(tt, t)

         # advance tokenizer only if we are in the else, since otherwise the
         # token was advanced by the else check
         self.tokenizer.advance()

      self._end_block("ifStatement")

   # compiles an expression (one or more terms connected by operators)
   def compile_expression(self):
      self._start_block("expression")

      # the first term
      self.compile_term()

      # finish any number of operators followed by terms
      while True:
         tt, t = self._token_next(False)
         if tt == "SYMBOL" and t in "+-*/&|<>=":
            # found an operator
            self._write(tt, t)

            # the next term
            self.tokenizer.advance()
            self.compile_term()
         else:
            # no term found; done parsing the expression
            break

      self._end_block("expression")

   # compiles a term
   # this routine is faced with a slight difficulty when trying to decide
   # between some of the alternative parsing rules. specifically, if the
   # current token is an identifier, the routine must distinguish between a
   # variable, an array entry, and a subroutine call. a single lookahead token,
   # which may be one of [, (, or ., suffices to distinguish between the three
   # possibilities. any other token is not part of this term and should not
   # be advanced over.
   def compile_term(self):
      self._start_block("term")

      # a term: integer_constant | string_constant | keyword_constant |
      # varname | varname[expression] | subroutine_call | (expression) |
      # unary_op term
      tt, t = self._token_next(False)
      if tt in ["INT_CONST", "STRING_CONST", "KEYWORD"]:
         self._write(tt, t)

         # advance for the next statement
         self.tokenizer.advance()
      elif tt == "SYMBOL" and t == "(":
         # ( expression )

         # write the opening parenthesis
         self._write(tt, t)

         # parse the expression
         self.tokenizer.advance()
         self.compile_expression()

         # closing parenthesis
         tt, t = self._token_next(False, "SYMBOL", ")")
         self._write(tt, t)

         # advance for the next statement
         self.tokenizer.advance()

      elif tt == "SYMBOL" and t in "-~":
         # unary_op term

         # write the unary operation
         self._write(tt, t)

         # parse the rest of the term
         self.tokenizer.advance()
         self.compile_term()

      elif tt == "IDENTIFIER":
         # varname, varname[expression], subroutine_call

         # do not write the identiifer yet

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
            self._write(tt, t)

      else:
         # unknown
         print "WARNING: Unknown term expression object:", tt, t

      self._end_block("term")

   # compiles a (possible empty) comma-separated list of expressions
   def compile_expression_list(self):
      self._start_block("expressionList")

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

            # possible comma
            tt, t = self._token_next(False)
            if tt == "SYMBOL" and t == ",":
               self._write(tt, t)
               self.tokenizer.advance()
            else:
               # not a comma; stop processing parameters
               break

      self._end_block("expressionList")

   # compiles a subroutine call
   # two cases:
   # - subroutineName(expressionList)
   # - (class|var).subroutineName(expressionList)
   def compile_subroutine_call(self):
      # first part of name
      tt, t = self._token_next(False, "IDENTIFIER")
      self._write(tt, t)

      # a dot and another name may exist, or it could be a parenthesis
      tt, t = self._token_next(True)
      if tt == "SYMBOL" and t == ".":
         self._write(tt, t)

         # the name after the dot
         tt, t = self._token_next(True, "IDENTIFIER")
         self._write(tt, t)

         # advance so that we are on the parenthesis
         self.tokenizer.advance()

      # opening parenthesis
      tt, t = self._token_next(False, "SYMBOL", "(")
      self._write(tt, t)

      # expression list
      self.tokenizer.advance()
      self.compile_expression_list()

      # closing parenthesis
      tt, t = self._token_next(False, "SYMBOL", ")")
      self._write(tt, t)

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
