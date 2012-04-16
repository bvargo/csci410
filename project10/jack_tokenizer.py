# the tokenizer module
# encapsulates access to the input code; tokenizes jack input code

import itertools

class JackTokenizer(object):
   # the source input
   source = []

   # the inputs of source that have already been processed
   # the most recently processed input is at the end of the list
   # this way, the entire source input can be represented as
   # done + current_token + source
   done = []

   # the current token as a string
   current_token = ""

   # jack language keywords, lowercase
   keywords = ["class", "constructor", "function", "method", "field",
         "static", "var", "int", "char", "boolean", "void", "true", "false",
         "null", "this", "let", "do", "if", "else", "while", "return"]

   # jack language symbols
   symbols = "{}()[].,;+-*/&|<>=~"

   # opens the filename and prepares to parse
   # if the file does not exist, then an IOError is raised
   def __init__(self, source_filename):
      # open the file
      source_file = open(source_filename, 'r')

      # read and close the file
      source = source_file.readlines()
      source_file.close()

      # strip // comments
      source = map(lambda a: a.split("//")[0], source)

      # strip /* */ comments
      in_comment = False
      for line_num in range(0, len(source)):
         modified = True

         # /* we */ /* could */ /* have */ /* a */ really annoying line
         # this needs to be processed
         while modified:
            modified = False

            line = source[line_num]
            if in_comment and "*/" in line:
               source[line_num] = line.split("*/", 1)[1]
               in_comment = False
               modified = True

            line = source[line_num]
            if not in_comment and "/*" in line:
               # include all text before the comment
               source[line_num] = line.split("/*", 1)[0]
               in_comment = True

               # search for the end of a comment on the same line
               s = line.split("*/", 1)
               if len(s) == 2:
                  source[line_num] += " " + s[1]
                  # we closed the comment again, since we found the end
                  in_comment = False

               # mark that the string was modified
               modified = True

            # if nothing was modified and we are in a comment, delete the line
            # do not mark as modified, since we do not need to reprocess this
            # line
            if not modified and in_comment:
               source[line_num] = ""

      # find and replace certain characters, so tokenizing works nicely
      # this can break strings in some cases, but jack is broken enough that
      # this is probably legal
      for character in self.symbols:
         replace = lambda a: a.replace(character, " " + character + " ")
         source = map(replace, source)

      # split into tokens
      source = map(lambda a: a.split(), source)

      # merge into one list of tokens, rather than a list of lists
      source = itertools.chain.from_iterable(source)

      # strip whitespace
      source = map(lambda a: a.strip(), source)

      # remove blank lines
      source = [line for line in source if line]

      # save the source lines
      self.source = source

   # are there more tokens in the input?
   # returns a boolean
   def has_more_tokens(self):
      return bool(self.source)

   # reads the next token from the input and makes it the current token
   # it should be called only if has_more_commands is true
   def advance(self):
      if self.has_more_tokens():
         # save the last token processed
         self.done.append(self.current_token)

         # move to the next token
         self.current_token = self.source.pop(0)

   # moves the tokenizer backwards again, if possible
   # this is the opposite of advance
   def retreat(self):
      if len(self.done) != 0:
         # add the current token back into the list of tokens not yet processed
         self.source.insert(0, self.current_token)

         # adjust the current token to the last token in done
         self.current_token = self.done.pop()

   # returns the type of the current token
   # - KEYWORD
   # - SYMBOL
   # - IDENTIFIER
   # - INT_CONST
   # - STRING_CONST
   def token_type(self):
      token = self.current_token.lower()
      if token in self.keywords:
         return "KEYWORD"
      elif token in self.symbols:
         return "SYMBOL"
      elif token[0] in "0123456789":
         return "INT_CONST"
      elif token[0] == '"':
         # string is a little tricky, since the string may consist of more
         # than one raw token, due to containing strings
         # continue to add tokens to the current token until the end quotation
         # mark is found
         while token[-1] != '"':
            self.current_token += " " + self.source.pop(0)
            token = self.current_token.lower()
         return "STRING_CONST"
      else:
         return "IDENTIFIER"

   # returns the keyword that is the current token; is called only when
   # token_type() is KEYWORD
   def keyword(self):
      return self.current_token

   # returns the symbol that is the current token; is called only when
   # token_type() is SYMBOL
   def symbol(self):
      return self.current_token

   # returns the identifier that is the current token; is called only when
   # TokenType() is IDENTIFIER
   def identifier(self):
      return self.current_token

   # returns the integer value of the current token; should be called only
   # when token_type() is INT_CONST
   def int_const(self):
      return int(self.current_token)

   # returns the string value of the current token, without the double quotes
   # should be called only when token_type() is STRING_CONST
   def string_const(self):
      # ensure that token_type has been called, so that the full string is
      # fetched; see the comment in token_type
      self.token_type()

      # remove quotation marks
      return self.current_token[1:-1]
