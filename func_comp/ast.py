
class AST():
	def __init__(self):
		pass

	def visit(self, funcDefs, varis):
		raise NotImplementedError(" error")

	def __repr__(self):
		raise NotImplementedError(" error")





def substract2():
	return ["POP R15", "POP R1", "POP R2", "SUB R1, R1, R2", "PSH R1", "PSH R15", "RET"]
def addition2():
	return ["POP R15", "POP R1", "POP R2", "ADD R1, R1, R2", "PSH R1", "PSH R15", "RET"]
def multiplication2():
	return ["POP R15", "POP R1", "POP R2", "MLT R1, R1, R2", "PSH R1", "PSH R15", "RET"]
#def division(nArgs):
#	return reduce(lambda x,y: x/y, args)
#def power(nArgs):
#	return reduce(lambda x,y: x**y, args)
def equal2():
	return ["POP R15", "POP R1", "POP R2", "SETE R1, R1, R2", "PSH R1", "PSH R15", "RET"]
#def smaller(nArgs):
#	return reduce(lambda x,y: x<y, args)
#def smallerEquals(nArgs):
#	return reduce(lambda x,y: x<=y, args)
#def greater(nArgs):
#	return reduce(lambda x,y: x>y, args)
#def greaterEquals(nArgs):
#	return reduce(lambda x,y: x>=y, args)
#def notEqual(nArgs):
#	return reduce(lambda x,y: x!=y, args)
#



#def empty(args):
#	return (1 if len(args[0])==0 else 0)
#def cons(args):
#	return [args[0]]+args[1]
#def rest(args):
#	return args[0][1:]
#def first(args):
#	return args[0][0]
#def last(args):
#	return args[0][-1]


#ARRAY: 	mapIt filter foldl remove sort concat range cons first last

builtins = [["=",2,equal2], ["-",2,substract2], ["+",2,addition2], ["*",2,multiplication2]]

funcsCalled = []
labelCounter = 0



class Programm(AST):
	def __init__(self, funcDefs, expr):
		self.funcDefs = funcDefs
		self.expr = expr


		

	def visit(self, funcDefs=None, varis=None):
		code = self.expr.visit(self.funcDefs, {})+["HLT","HLT","HLT"]
		funcs = []
		for x,nArgs in funcsCalled:
			funcs += self.funcDefs.getFuncCode(x, nArgs)
		return code+funcs

	def __repr__(self):
		return "FUNCTIONS:\n"+str(self.funcDefs)+"\nEXPR:\n"+str(self.expr)



class FuncDefs(AST):
	def __init__(self, methods):
		self.methods = methods
		

	def isIn(self, funcName, nArgs):
		return any([(x[0]==funcName and (x[1]=="*" or x[1]==nArgs)) for x in (self.methods+builtins)])

	def isInAnyArg(self, funcName):
		return any([(x[0]==funcName) for x in (self.methods+builtins)])

	def getFuncs(self, funcName):
		return_funcs = []
		for x in (self.methods+builtins):
			if x[0]==funcName:
				return_funcs.append(x)
		return return_funcs

	def getFuncCode(self, funcName, nArgs):
		for x in self.methods:
			if x[0]==funcName and x[1]==nArgs:
				args = [f"._function_{funcName}_{nArgs}"]
				args += ["POP R15"]
				for g in range(nArgs):
					args += [f"POP R{3+g}"]

				varis = {x[3][y]:3+y for y in range(len(x[3]))}
				code = args+x[2].visit(self, varis)+["PSH R1", "PSH R15", "RET"]
				return code
		for x in builtins:
			if x[0]==funcName and (x[1]=="*" or x[1]==nArgs):
				return [f"._function_{funcName}_{nArgs}"]+x[2]()



	def visit(self, funcDefs, varis):
		pass

	def __repr__(self):
		return "\n".join([str(x) for x in self.methods])


class Cond(AST):
	def __init__(self, cases):
		self.cases = cases

	def visit(self, funcDefs, varis):
		global labelCounter
		code = []
		n = 0
		labelCounter+=1

		for x in self.cases:
			code += x[0].visit(funcDefs, varis)+[f"BRZ .skip_cond{labelCounter}_{n}"]
			code += x[1].visit(funcDefs, varis)+[f"BRA .skip_cond{labelCounter}", f".skip_cond{labelCounter}_{n}"]
			n+=1
		code.append(f".skip_cond{labelCounter}")
		return code
		

	def __repr__(self):
		return "\n".join([str(x) for x in self.cases])



class ID(AST):
	def __init__(self, name):
		self.name = name

	def visit(self, funcDefs, varis):
		#print("ID QUIT")
		#quit()
		if self.name in varis:
			return [f"MOV R1, R{varis[self.name]}"]
		#elif funcDefs.isInAnyArg(self.name):
		#	return funcDefs.getFuncs(self.name)
		else:
			raise Exception(f"Variable {self.name} not defined") 

	def __repr__(self):
		return str(self.name)



class Number(AST):
	def __init__(self, value):
		self.value = value

	def visit(self, funcDefs, varis):
		return [f"IMM R1, {str(int(self.value))}"]

	def __repr__(self):
		return str(self.value)


class FuncCall(AST):
	def __init__(self, funcName, args):
		self.funcName = funcName
		self.args = args


	def visit(self, funcDefs, varis):
		actualFuncName = self.funcName

		if self.funcName in varis:
			actualFuncName = varis[self.funcName][0][0]

		if funcDefs.isIn(actualFuncName, len(self.args)):
			coms = []

			coms += [f"PSH R15"]
			for key,value in varis.items():
				coms += [f"PSH {value}"]
				print(key,value)
			

			for x in self.args:
				coms += x.visit(funcDefs, varis)+["PSH R1"]
			coms += [f"CAL ._function_{actualFuncName}_{len(self.args)}", "POP R1"]

			for key,value in varis.items():
				coms += [f"POP {value}"]
			coms += [f"POP R15"]

			if not any([x[0]==actualFuncName for x in funcsCalled]):
				funcsCalled.append([actualFuncName, len(self.args)])
			return coms
		else:
			raise Exception("Method not defined", actualFuncName, len(self.args), " DEFINED:", [(x[0],x[1]) for x in  funcDefs.methods+builtins])

	def __repr__(self):
		if len(self.args)>0:
			return f"({self.funcName} {' '.join([str(x) for x in self.args])})"
		return f"({self.funcName} )"