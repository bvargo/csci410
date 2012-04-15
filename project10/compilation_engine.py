# the "compilation engine" (really the parser) for jack

class CompilationEngine(object):
   # the constructor for compiling a single class
   # the next method to be called after construction must be compile_class
   def __init__(self, source_filename):
      pass

   # compiles a complete class
   def compile_class(self):
      pass

   # compiles a static declaration or field declaration
   def compile_class_var_dec(self):
      pass

   # compiles a complete method, function, or constructor
   def compile_subroutine(self):
      pass

   # compiles a (possibly empty) parameter list, not including the enclosing
   # parentheses
   def compile_parameter_list(self):
      pass

   # compiles a var declaration
   def compile_var_dec(self):
      pass

   # compiles a sequence of statements, not inclujding the enclosing {}
   def compile_statements(self):
      pass

   # compiles a do statement
   def compile_do(self):
      pass

   # compiles a let statement
   def compile_let(self):
      pass

   # compiles a while statement
   def compile_while(self):
      pass

   # compiles a return statement
   def compile_return(self):
      pass

   # compiles a if statement, including a possible trailing else clause
   def compile_if(self):
      pass

   # compiles an expression
   def compile_expression(self):
      pass

   # compiles a term
   # this routine is faced with a slight difficulty when trying to decide
   # between some of the alternative parsing rules. specifically, if the
   # current token is an identifier, the routine must distinguish between a
   # variable, an array entry, and a subroutine call. a single lookahead token,
   # which may be one of [, (, or ., suffices to distinguish between the three
   # possibilities. any other token is not part of this term and should not
   # be advanced over.
   def compile_term(self):
      pass

   # compiles a (possible empty) comma-separated list of expressions
   def compile_expression_list(self):
      pass
