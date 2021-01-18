
NUMBER,   LPAREN, RPAREN, LSPAREN, RSPAREN, KOMMA, SEMICOLON, FUNCDEF, EOF = (
'NUMBER', '(',    ')',    "[",     "]",     ",",   ';',       "->",   'EOF')

RESERVED = ["cond", "return"]

class Token():
	def __init__(self, typ, value, posi):
		self.typ = typ
		self.value = value
		self.position = posi

	def __str__(self):
		return f'Token({self.typ}, {repr(self.value)}, at {self.position})'

	def __repr__(self):
		return self.__str__()



class Lexer():
	def __init__(self, code):
		self.code = code
		self.pos = 0
		self.current_char = self.code[self.pos]
		self.last_token = ""

	def getRest(self):
		return self.code[self.pos-1:]

	def error(self, token=None):
		raise Exception(f"ERROR AT CHAR {str(self.pos)}:{str(token)}")

	def advance(self):
		self.pos +=1
		if self.pos>=len(self.code):
			self.current_char = None
		else:
			self.current_char=self.code[self.pos]

	def whitespace(self):
		while self.current_char is not None and self.current_char.isspace():
			self.advance()

	def number(self):
		result = ''
		while self.current_char is not None and self.current_char.isdigit() or self.current_char==".":
			result += self.current_char
			self.advance()
		return float(result)

	def id(self):
		result = ''
		while self.current_char is not None and (not self.current_char.isspace()) and (self.current_char not in ["(", ")", "[", "]", "EOF"]):
			result += self.current_char
			self.advance()
		global RESERVED
		if result in RESERVED:
			self.last_token = result
			return Token(result.upper(), result, self.pos)
		return Token("ID", result, self.pos)

	def peek(self):
		peek_pos = self.pos + 1
		if peek_pos >= len(self.code):
			return None
		else:
			return self.code[peek_pos]



	def get_next_token(self):
		while self.current_char is not None:
			if self.current_char.isspace():
				self.whitespace()
				continue

			elif self.current_char.isdigit():
				return Token(NUMBER, self.number(), self.pos)

			elif self.current_char == '-' and self.peek()==">":
				self.advance()
				self.advance()
				return Token(FUNCDEF, '->', self.pos)

			elif self.current_char == '(':
				self.advance()
				return Token(LPAREN, '(', self.pos)

			elif self.current_char == ';':
				self.advance()
				return Token(SEMICOLON, ';', self.pos)

			elif self.current_char == ')':
				self.advance()
				return Token(RPAREN, ')', self.pos)

			elif self.current_char == '[':
				self.advance()
				return Token(LSPAREN, '[', self.pos)

			elif self.current_char == ']':
				self.advance()
				return Token(RSPAREN, ']', self.pos)

			elif self.current_char == ',':
				self.advance()
				return Token(KOMMA, ',', self.pos)
			else:
				return self.id()



			self.error(token=self.current_char)

		return Token(EOF, None, self.pos)