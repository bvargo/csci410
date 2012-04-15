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
      self.destination_file.write("<class>\n")

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
      self.destination_file.write("</class>\n")

      # close the output file
      self.destination_file.close()

   # compiles a static declaration or field declaration
   def compile_class_var_dec(self):
      # start variable declaration
      self.destination_file.write("<classVarDec>\n")

      # compile the variable declaration
      # False means don't print the tags
      self.compile_var_dec(False)

      # end variable declaration
      self.destination_file.write("</classVarDec>\n")

   # compiles a complete method, function, or constructor
   def compile_subroutine(self):
      # start subroutine declaration
      self.destination_file.write("<subroutineDec>\n")

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
      self.destination_file.write("<subroutineBody>\n")

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
      self.destination_file.write("</subroutineBody>\n")

      # finish subroutine declaration
      self.destination_file.write("</subroutineDec>\n")

      self.tokenizer.advance()

   # compiles a (possibly empty) parameter list, not including the enclosing
   # parentheses
   def compile_parameter_list(self):
      self.destination_file.write("<parameterList>\n")

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

      self.destination_file.write("</parameterList>\n")

   # compiles a var declaration
   def compile_var_dec(self, print_tags=True):
      if print_tags:
         self.destination_file.write("<varDec>\n")

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
         self.destination_file.write("</varDec>\n")

   # compiles a sequence of statements, not including the enclosing {}
   def compile_statements(self):
      self.destination_file.write("<statements>\n")

      while True:
         tt, t = self._token_next(False)
         if tt == "KEYWORD" and t in ["do", "let", "while", "return", "if"]:
            # call compile_t, where t is the type of compilation we want
            token = getattr(self, "compile_" + t)()
         else:
            # not a statement; stop processing statements
            break

      self.destination_file.write("</statements>\n")

   # compiles a do statement
   def compile_do(self):
      self.destination_file.write("<doStatement>\n")

      # do keyword
      tt, t = self._token_next(False, "KEYWORD", "do")
      self._write(tt, t)

      # subroutine call
      self.tokenizer.advance()
      self.compile_subroutine_call()

      # semicolon
      tt, t = self._token_next(False, "SYMBOL", ";")
      self._write(tt, t)

      self.destination_file.write("</doStatement>\n")
      self.tokenizer.advance()

   # compiles a let statement
   def compile_let(self):
      self.destination_file.write("<letStatement>\n")

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

      self.destination_file.write("</letStatement>\n")
      self.tokenizer.advance()

   # compiles a while statement
   def compile_while(self):
      self.destination_file.write("<whileStatement>\n")

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

      self.destination_file.write("</whileStatement>\n")
      self.tokenizer.advance()

   # compiles a return statement
   def compile_return(self):
      self.destination_file.write("<returnStatement>\n")

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

      self.destination_file.write("</returnStatement>\n")
      self.tokenizer.advance()

   # compiles a if statement, including a possible trailing else clause
   def compile_if(self):
      self.destination_file.write("<ifStatement>\n")

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

      self.destination_file.write("</ifStatement>\n")

   # compiles an expression (one or more terms connected by operators)
   def compile_expression(self):
      self.destination_file.write("<expression>\n")

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

      self.destination_file.write("</expression>\n")

   # compiles a term
   # this routine is faced with a slight difficulty when trying to decide
   # between some of the alternative parsing rules. specifically, if the
   # current token is an identifier, the routine must distinguish between a
   # variable, an array entry, and a subroutine call. a single lookahead token,
   # which may be one of [, (, or ., suffices to distinguish between the three
   # possibilities. any other token is not part of this term and should not
   # be advanced over.
   def compile_term(self):
      # TODO - right now, this only prints what it gets

      self.destination_file.write("<term>\n")

      # print whatever is in the term (should be an identifier for now)
      tt, t = self._token_next(False, "IDENTIFIER")
      self._write(tt, t)

      self.destination_file.write("</term>\n")
      self.tokenizer.advance()

   # compiles a (possible empty) comma-separated list of expressions
   def compile_expression_list(self):
      self.destination_file.write("<expressionList>\n")

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

      self.destination_file.write("</expressionList>\n")

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
      self.destination_file.write("".join(output))
