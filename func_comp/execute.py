import ast
import tokenizer

#
#



class Compiler():
	def __init__(self):
		self.lexer = None
		self.current_token = None

	def error(self, token=None, expected=None):
		raise Exception(f"ERROR AT TOKEN {str(token)} EXPECTED {str(expected)}")

	def accept(self, token_type):
		if self.current_token.typ == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			self.error(self.current_token, token_type)

	def compile(self, code):
		#programm := [funcDefs] 'return' expr
		self.lexer = tokenizer.Lexer(code)
		self.current_token = self.lexer.get_next_token()

		if self.current_token.typ!="RETURN":
			methods = self.funcDefs()#
		else:
			methods = ast.FuncDefs([])

		self.accept("RETURN")
	
		expr = self.expr()

		return ast.Programm(methods, expr)

	def funcDefs(self):
		#funcDefs := ( '(' ID (ID)* ')' '->' expr ';' )*
		methods = []
		#self.accept(tokenizer.LPAREN)
		while self.current_token.typ!="RETURN":
			newMethod = [None, None, None, []]#name len, expr, args
			self.accept(tokenizer.LPAREN)

			newMethod[0] = self.current_token.value
			self.accept("ID")
			while self.current_token.typ!=tokenizer.RPAREN:
				newMethod[-1].append(self.current_token.value)
				self.accept("ID")
			newMethod[1] = len(newMethod[-1])
			self.accept(tokenizer.RPAREN)
			self.accept(tokenizer.FUNCDEF)

			newMethod[2] = self.expr()

			methods.append(newMethod)
			self.accept(tokenizer.SEMICOLON)

		
		return ast.FuncDefs(methods)

	def expr(self):
		#expr := NUMBER | ID | '(' cond ')' | '(' funcCall ')'
		if self.current_token.typ==tokenizer.NUMBER:
			ret = ast.Number(self.current_token.value)
			self.accept(tokenizer.NUMBER)
			return ret
		if self.current_token.typ=="ID":
			ret = ast.ID(self.current_token.value)
			self.accept("ID")
			return ret
		if self.current_token.typ==tokenizer.LSPAREN:
			self.accept(tokenizer.LSPAREN)
			values = []
			while self.current_token.typ!=tokenizer.RSPAREN:
				values.append(self.expr())
			ret = ast.DefineArray(values)
			self.accept(tokenizer.RSPAREN)
			return ret
		if self.current_token.typ==tokenizer.LPAREN:
			self.accept(tokenizer.LPAREN)
			if self.current_token.typ=="COND":
				ret = self.cond()
			else:
				ret = self.funcCall()
			self.accept(tokenizer.RPAREN)
			return ret

	def cond(self):
		#cond :=  COND ('(' expr expr ')')*
		self.accept("COND")
		cases = []

		while self.current_token.typ==tokenizer.LPAREN:
			self.accept(tokenizer.LPAREN)
			cases.append([self.expr(), self.expr()])
			self.accept(tokenizer.RPAREN)

		return ast.Cond(cases)

	def funcCall(self):
		#funcCall := funcID (expr)*
		funcName = self.current_token.value
		self.accept("ID")
		args = []
		while self.current_token.typ!=tokenizer.RPAREN:
			args.append(self.expr())

		return ast.FuncCall(funcName, args)

		


#




if __name__=="__main__":
	code = """  
				(pow a b)->(cond 
							((= b 0) a)
							(1 (* a (pow a (- b 1))))
							);

				return (* 2 2)
	"""
	print("CODE:")
	print(code)
	comp = Compiler()
	resultAst = comp.compile(code)

	print(resultAst.visit())
