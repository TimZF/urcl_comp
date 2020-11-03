from pycparser import c_parser, c_ast, preprocess_file

fileToCompile = "test.c"
mpR = "R15"
initFunc = "test"
debugComments = True
onlyUncommentOptims = False



urclEx = True




branchingComms = ["CAL","RET","BRA","BRC","BNC","BRZ","BNZ","BRN","BRP","BRL","BRG","BRE","BNE","BOD","BEV","BLE","BGE"]
varsInMemory = []
constants = []

programInitComs = []

builtInMethods = {}


skipId = 0 
structs = {}
dataStrings = []





class MethodsVarHolder():
	def __init__(self):
		self.methods = {}
		self.types = {}
		self.arraysMethods = {}

	def addMethod(self, method):
		self.methods[method] = []

	def append(self, varName, inMethod, typee):
		if inMethod:
			self.methods[inMethod].append(varName)
		self.types[inMethod+"."+varName] = typee

	def getType(self, varName, inMethod):
		return self.types[inMethod+"."+varName]

	def isIn(self, var, inMethod):
		return (var in self.methods[inMethod])

	def get(self, var, inMethod):
		return str(self.methods[inMethod].index(var))

methods = MethodsVarHolder()


text = preprocess_file(fileToCompile, cpp_path='./mcpp-2.7.2/bin/mcpp.exe', cpp_args='')
parser = c_parser.CParser()
ast = parser.parse(text, filename='test')
#ast.show(showcoord=True)


def debugADD(command, sub=False):
	add = "\n//"
	if sub:
		add = ""

	if type(command)==c_ast.Decl:
		return debugADD(command.type, sub)

	if type(command)==c_ast.TypeDecl:
		if sub:
			return add+"define "+command.declname
		return [add+"define "+command.declname]

	if type(command)==c_ast.PtrDecl:
		return [add+"define *"+command.type.declname]

	if type(command)==c_ast.ArrayDecl:
		return [add+"define *"+command.type.declname+"[]"]

	if type(command)==c_ast.FuncDef:
		return []

	if type(command)==c_ast.Assignment:
		return [add+debugADD(command.lvalue,True)+" "+command.op+" "+debugADD(command.rvalue,True)]

	if type(command)==c_ast.While:
		return [add+"while("+debugADD(command.cond,True)+")"]

	if type(command)==c_ast.For:
		return [add+"for("+debugADD(command.init,True)+"; "+debugADD(command.cond,True)+"; "+debugADD(command.next,True)+")"]

	if type(command)==c_ast.If:
		return [add+"if("+debugADD(command.cond,True)+")"]

	if type(command)==c_ast.Return:
		return [add+"Return "+"".join(debugADD(command.expr))]

	if type(command)==c_ast.FuncCall:
		if sub:
			return add+"FuncCall "+command.name.name+"("+debugADD(command.args, True)+")"
		return [add+"FuncCall "+command.name.name+"("+debugADD(command.args, True)+")"]


	if type(command)==c_ast.DeclList:
		print(command)
		return "".join([debugADD(x,True) for x in command.decls])


	if type(command)==c_ast.ID:
		return command.name

	if type(command)==c_ast.Constant:
		return command.value

	if type(command)==c_ast.ArrayRef:
		return debugADD(command.name.name,True)+"["+debugADD(command.subscript,True)+"]"

	if type(command)==c_ast.ExprList:
		return ",".join([ debugADD(x, True) for x in command.exprs])

	if type(command)==c_ast.BinaryOp:
		return f"{''.join(debugADD(command.left, True))} {command.op} {''.join(debugADD(command.right, True))}"

	if type(command)==c_ast.UnaryOp:
		if sub:
			if command.op.startswith("p"):
				return f"{''.join(debugADD(command.expr, True))}{command.op.replace('p','')}"
			return f"{command.op}{''.join(debugADD(command.expr, True))}"
		if command.op.startswith("p"):
			return [f"//{''.join(debugADD(command.expr, True))}{command.op.replace('p','')}"]
		return [f"//{command.op}{''.join(debugADD(command.expr, True))}"]

	if type(command)==c_ast.Break:
		return ["//break"]

	if type(command)==c_ast.Continue:
		return ["//continue"]

	if type(command)==str:
		return command


	if command==None:
		return ""


	print(command)
	raise NotImplementedError()















def compound(ast, inMethod = None, inLoop = None):
	global programInitComs
	coms = []
	for x in ast:
		if debugComments:
			coms += debugADD(x)

		if type(x) is c_ast.FuncDef:
			coms += funcDef(x, inMethod)
		elif type(x) is c_ast.FuncCall:
			coms += funcCall(x, inMethod)
		elif type(x) is c_ast.Return:
			if x.expr:
				returnWhat = expression(x.expr, inMethod)
				if type(returnWhat[0])==list:
					coms += ["POP R2"]
					for x in returnWhat:
						coms += x+["PSH R1"]
					coms += ["PSH R2"]
				else:
					coms += returnWhat
			coms += ["RET"]
		elif type(x) is c_ast.Decl:
			c,_ = declare(x, inMethod)
			if inMethod==None:
				programInitComs += c
			else:
				coms += c
		elif type(x) is c_ast.Assignment:
			coms += assignment(x, inMethod)
		elif type(x) is c_ast.If:
			coms += ifDef(x, inMethod, inLoop)
		elif type(x) is c_ast.While:
			coms += whileDef(x, inMethod)
		elif type(x) is c_ast.UnaryOp:
			coms += unaryOp(x, inMethod)
		elif type(x) is c_ast.For:
			coms += forLoopDef(x, inMethod)
		elif type(x) is c_ast.Typedef:
			coms += typeDefi(x, inMethod)
		elif type(x) is c_ast.Continue:
			if inLoop:
				coms += ["BRA "+inLoop[0]]
			else:
				raise Exception("CANT CONTINUE OUTSIDE OF LOOPS")
		elif type(x) is c_ast.Break:
			if inLoop:
				coms += ["BRA "+inLoop[1]]
			else:
				raise Exception("CANT BREAK OUTSIDE OF LOOPS")
		else:

			print(x)
			raise NotImplementedError("")
	return coms


def debugOutInt(x, inMethod):
	return expression(x.args, inMethod)+["OUT 0, R1"]

builtInMethods["__debugInt__"] = debugOutInt

def debugOutChar(x, inMethod):
	return expression(x.args, inMethod)+["OUT 1, R1"]

builtInMethods["__debugChar__"] = debugOutChar

def debugOutScreen(x, inMethod):
	return expression(x.args, inMethod)+["OUT 3, R1"]

builtInMethods["__debugScreen__"] = debugOutScreen


def inputChar(x, inMethod):
	return ["IN R1, 3"]

builtInMethods["__input__"] = inputChar


def typeDefi(x, inMethod):
	if type(x.type)==c_ast.TypeDecl:
		return declare(x.type, inMethod)
	else:
		print(x)
		raise NotImplementedError()


def toAsm(x, inMethod):
	coms = []
	for x in x.args.exprs:
		if type(x)==c_ast.Constant and x.type=="string":
			coms += [x.value.replace('"',"")]
		else:
			coms += expression(x, inMethod)
	return coms
builtInMethods["__asm__"] = toAsm


def forLoopDef(x, inMethod):

	skipEnd = "._for_skip_end_" + str(skipId)
	skipStart = "._for_skip_start_" + str(skipId)
	skipContinue = "._for_skip_continue_" + str(skipId)

	coms = []
	if x.init:
		init = x.init
		for decla in init.decls:
			c,_ = declare(decla, inMethod)
			coms += c
	
	coms += [skipStart] + condCheck(x.cond, inMethod, skipEnd)

	coms += compound(x.stmt, inMethod, [skipContinue,skipEnd])+[skipContinue]+compound([x.next], inMethod)+["BRA "+skipStart, skipEnd]

	return coms

def unaryOp(x, inMethod, onItsOwn=True):
	coms = expression(x.expr, inMethod)
	if x.op=="-":
		coms += ["SUB R1, 0, R1"]
	elif x.op=="p++":
		coms += ["INC R1, R1"]
	elif x.op=="p--":
		coms += ["DEC R1, R1"]
	elif x.op=="&":
		coms = ["SUB R1, "+mpR+", "+methods.get(x.expr.name, inMethod)]
	else:
		print(x)
		raise NotImplementedError("")
	if onItsOwn:
		coms += setVariableMemoryAddress(x.expr.name, inMethod)
	return coms


def whileDef(x, inMethod):
	global skipId

	skipStart = "._while_skip_start_" + str(skipId)
	skipEnd = "._while_skip_end_" + str(skipId)
	skipContinue = skipStart
	
	skipId += 1
	coms = condCheck(x.cond, inMethod, skipEnd)
	
	coms = [skipStart]+coms+compound(x.stmt, inMethod, [skipContinue,skipEnd])+["BRA "+skipStart, skipEnd]
	return coms



def condCheck(x, inMethod, skipToo):

	if type(x)==c_ast.Constant:
		coms = expression(x, inMethod)
		coms += ["BRZ "+skipToo]
	elif type(x)==c_ast.ID:
		coms = expression(x, inMethod)
		coms += ["BRZ "+skipToo]
	else:
		if x.op in ["&&", "||","|","&"]:
			coms = binaryOp(x, inMethod, "BRZ "+skipToo)
			coms += ["BRZ "+skipToo]
		else:
			coms = expression(x, inMethod)
			if x.op==">":
				coms += ["BRZ "+skipToo, "BRN "+skipToo]
			elif x.op=="<":
				coms += ["BRP "+skipToo, "BRZ "+skipToo]
			elif x.op==">=":
				coms += ["BRN "+skipToo]
			elif x.op=="=<":
				coms += ["BRP "+skipToo]
			elif x.op=="==":
				coms += ["BNZ "+skipToo]
			elif x.op=="!=":
				coms += ["BRZ "+skipToo]
			else:
				print(x)
				raise NotImplementedError("")
	return coms
	#quit()



def ifDef(x, inMethod, inLoop):
	global skipId

	skipNameEnd = "._if_skip_end_" + str(skipId)
	if x.iffalse == None:
		skipNameFalse = skipNameEnd
	else:
		skipNameFalse = "._if_skip_false_" + str(skipId)

	coms = condCheck(x.cond, inMethod, skipNameFalse)
	skipId += 1
	
	coms += compound(x.iftrue, inMethod, inLoop)+((["BRA "+skipNameEnd, skipNameFalse]+compound(x.iffalse, inMethod, inLoop)) if x.iffalse else [])+[skipNameEnd]
	return coms


def assignment(x, inMethod):
	coms = expression(x.rvalue, inMethod)
	if x.op=="=":
		if type(x.lvalue)==c_ast.StructRef:
			se = setVariableMemoryAddress(x.lvalue.name.name+"."+x.lvalue.field.name, inMethod)

		elif type(x.lvalue)==c_ast.ArrayRef:
			if x.lvalue.subscript != c_ast.Constant:
				se = ["PSH R1"]
				#print(x)
				#print(x.lvalue.name)
				#print(x.lvalue.subscript)
				#quit()
				se += expression(x.lvalue.subscript, inMethod)+["MOV R2, R1"]+getVariableMemoryAddress(x.lvalue.name.name,inMethod)+["ADD R1, R1, R2"]
				se += ["POP R2", "STORE R1, R2"]
			else:
				se = setVariableMemoryAddress(x.lvalue.name.name+"."+x.lvalue.subscript.value, inMethod)
		else:
			se = setVariableMemoryAddress(x.lvalue.name, inMethod)

		if type(se[0])==list:
			for x in se:
				coms += ["POP R1"]+x
		else:
			coms += se
	else:
		print(x)
		raise NotImplementedError("")
	return coms

def funcCall(x, inMethod):
	if x.name.name in builtInMethods:
		return builtInMethods[x.name.name](x, inMethod)
	callFuncLabel = "._function_"+x.name.name
	coms = []
	if x.args:
		for expr in x.args:
			c = expression(expr, inMethod)
			if type(c[0]) is list:
				for x in c:
					coms += x+["PSH R1"]
			else:
				coms += c+["PSH R1"]
	coms += ["CAL "+callFuncLabel]
	return coms

def setVariableMemoryAddress(varName, inMethod):
	if inMethod and methods.isIn(varName, inMethod):
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod),"STORE R3, R1"]
	elif inMethod and any([x.split(".")[0]==varName for x in methods.methods[inMethod]]):
		varsNeede = [setVariableMemoryAddress(x, inMethod) for x in methods.methods[inMethod] if x.split(".")[0]==varName]
		return varsNeede
	else:
		return ["STORE "+str(varsInMemory.index(varName))+", R1"]

def getVariableMemoryAddress(varName, inMethod):
	if inMethod and methods.isIn(varName, inMethod):
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod),"LOAD R1, R3"]
	elif inMethod and any([x.split(".")[0]==varName for x in methods.methods[inMethod]]):
		#varsNeede = [getVariableMemoryAddress(x, inMethod) for x in methods.methods[inMethod] if x.split(".")[0]==varName]
		#if methods.getType(varName, inMethod)=="array":
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod)]#varsNeede
	else:
		return ["LOAD R1, "+str(varsInMemory.index(varName))]


def funcDef(x, inMethod):
	functionName = "._function_"+x.decl.name
	functionSkip = "._function_skip_"+x.decl.name
	arguments = x.decl.type.args

	methods.addMethod(x.decl.name)

	args = []
	if arguments!=None:
		args += ["POP R1"]

		for arg in reversed(arguments.params):
			if type(arg)==c_ast.Decl:
				_,w = declare(arg, x.decl.name)
				for n in w:
					args += ["POP R2", "SUB R3, "+mpR+", "+methods.get(n, x.decl.name), "STORE R3, R2"]
			else:
				print(arg)
				raise NotImplementedError("")
		args += ["PSH R1"]

	body = compound(x.body, x.decl.name)

	numVars = str(len(methods.methods[x.decl.name]))


	for x in reversed(range(len(body))):
		if body[x]=="RET":
			body.insert(x,"SUB "+mpR+", "+mpR+", "+numVars)

	coms = ["BRA "+functionSkip, functionName, "ADD "+mpR+", "+mpR+", "+numVars]+args+body+["SUB "+mpR+", "+mpR+", "+numVars,"RET", functionSkip]
	return coms


def declare(c, inMethod):
	varsWeDeclare = []
	if type(c.type)==c_ast.TypeDecl:
		if type(c.type.type)==c_ast.Struct:
			print("STRUCT NAME POINTER REWRITE")
			quit()
			
			structdefinition = structs[c.type.type.name]

			for x in structdefinition:
				if "const" in c.quals:
					constants.append(c.name+"."+x[0])

				varsWeDeclare.append(c.name+"."+x[0])
				if inMethod:
					methods.append(c.name+"."+x[0], inMethod, "Struct")
				else:
					varsInMemory.append(c.name+"."+x[0])

			code = []
			if c.init is not None:
				codeExpr = expression(c.init, inMethod)
				for x in range(len(structdefinition)):
					varName = c.name+"."+structdefinition[x][0]
					code += codeExpr[x]+setVariableMemoryAddress(varName, inMethod)
			return code, varsWeDeclare

		elif type(c.type.type) == c_ast.IdentifierType and c.type.type.names[0]=="char":
			if "const" in c.quals:
				constants.append(c.name)

			varsWeDeclare.append(c.name)
			if inMethod:
				methods.append(c.name, inMethod, "char")
			else:
				varsInMemory.append(c.name)
			if c.init is not None:
				return expression(c.init, inMethod)+setVariableMemoryAddress(c.name, inMethod), varsWeDeclare

		elif type(c.type.type) == c_ast.IdentifierType and c.type.type.names[0]=="int":
			if "const" in c.quals:
				constants.append(c.name)

			varsWeDeclare.append(c.name)
			if inMethod:
				methods.append(c.name, inMethod, "int")
			else:
				varsInMemory.append(c.name)
			if c.init is not None:
				return expression(c.init, inMethod)+setVariableMemoryAddress(c.name, inMethod), varsWeDeclare
		else:
			print(c)
			raise NotImplementedError()
	elif type(c.type)==c_ast.ArrayDecl:
		arrayName = c.type.type.declname

		code = []
		if c.init or c.type.dim:
			if type(c.init)==c_ast.Constant and c.init.type=="string":
				initLen = len(list(c.init.value.replace('"',"").replace("\\n","\n").replace("\\b","\b")))+1
				arrayLen = initLen
				if urclEx:
					if not inMethod:
						code.append("strLoad "+str(len(varsInMemory))+", "+c.init.value)
						c.init = None


			elif type(c.type.dim)==c_ast.ID and (c.type.dim.name not in constants):
				print("CANT DYNAMICALLY ALLOCATE ARRAY SIZE RIGHT NOW AND IT WOULD BE SUPER EXPENSIVE")
				print("Just use malloc 4HEad")
				quit()
			elif type(c.type.dim)==c_ast.Constant or (c.type.dim.name in constants):
				initLen = len(c.type.dim.value)
				arrayLen = int(c.type.dim.value)



			
			if "const" in c.quals:
				for x in reversed(range(arrayLen)):
					constants.append(arrayName+"."+str(x))
					varsWeDeclare.append(arrayName+"."+str(x))
			if inMethod:
				for x in reversed(range(arrayLen)):
					methods.append(arrayName+"."+str(x), inMethod, "int")
					varsWeDeclare.append(arrayName+"."+str(x))
			else:
				for x in range(arrayLen):
					varsInMemory.append(arrayName+"."+str(x))
					varsWeDeclare.append(arrayName+"."+str(x))

			if "const" in c.quals:
				constants.append(arrayName)
			varsWeDeclare.append(arrayName)
			if inMethod:
				methods.append(arrayName, inMethod, "ptr_int")
				code += ["SUB R3, "+mpR+", "+methods.get(arrayName+".0", inMethod), "SUB R2, "+mpR+", "+methods.get(arrayName, inMethod), "STORE R2, R3"]
			else:
				varsInMemory.append(arrayName)
				code += ["IMM R3, "+str(varsInMemory.index(arrayName+".0")), "IMM R2, "+str(varsInMemory.index(arrayName)), "STORE R2, R3"]

			
			if c.init:
				if type(c.init)==c_ast.Constant and c.init.type=="string":
					v = c.init.value.replace('"','').replace("\\n","\n").replace("\\b","\b")
					code += ["IMM R1, 0"]+setVariableMemoryAddress(arrayName+"."+str(initLen-1), inMethod)
	
					for x in reversed(range(initLen-1)):
						a = v[x]
						if a=="\n": a = "10"
						elif a=="\b": a = "8"
						else: a = "'"+a+"'"
						code += ["IMM R1, "+a]+setVariableMemoryAddress(arrayName+"."+str(x), inMethod)
	
				else:
					codeExpr = expression(c.init, inMethod)
					for x in reversed(range(initLen)):
						code += codeExpr[x]+setVariableMemoryAddress(arrayName+"."+str(x), inMethod)

		#if "const" in c.quals:
		#	constants.append(arrayName)
		#varsWeDeclare.append(arrayName)
		#if inMethod:
		#	methods.append(arrayName, inMethod, "array")
		#else:
		#	varsInMemory.append(arrayName)


		return code, varsWeDeclare

	elif type(c.type)==c_ast.Struct:
		c = c.type
		
		structs[c.name] = []
		for x in c.decls:
			if type(x.type)==c_ast.TypeDecl:
				d = (x.name,x.type.type.names[0])
			elif type(x.type)==c_ast.PtrDecl:
				d = (x.name,x.type.type.type.name)
			else:
				print(c)
				raise NotImplementedError()

			structs[c.name].append(d)

	elif type(c.type)==c_ast.PtrDecl:
		if "const" in c.quals:
			constants.append(c.name)

		varsWeDeclare.append(c.name)
		if inMethod:
			methods.append(c.name, inMethod, "PtrDecl"+"_"+c.type.type.type.names[0])
		else:
			varsInMemory.append(c.name)

		if c.init is not None:
			if inMethod and methods.isIn(c.name, inMethod):
				return expression(c.init, inMethod)+["SUB R2, "+mpR+", "+methods.get(c.name, inMethod), "STORE R2, R1"], varsWeDeclare
			else:
				return expression(c.init, inMethod)+["STORE "+str(varsInMemory.index(c.name))+", R1"], varsWeDeclare


	else:
		print(c)
		raise NotImplementedError()
	
	return [], varsWeDeclare
	



def expression(expr, inMethod):
	if type(expr) is c_ast.FuncCall:
			return funcCall(expr, inMethod)

	elif type(expr) is c_ast.ExprList:
		coms = []
		for g in expr.exprs:
			coms += expression(g, inMethod)
		return coms
	elif type(expr)==c_ast.BinaryOp:
		return binaryOp(expr, inMethod)
	elif type(expr)==c_ast.Constant:
		if expr.type=="char":
			val = "10" if expr.value=="'\\n'" else ("8" if expr.value=="'\\b'" else expr.value)
			return ["IMM R1, "+val]
		else:
			if expr.value.startswith("0x") or expr.value.startswith("0b"):
				val = int(expr.value, 0)
			else:
				val = expr.value
	
			if expr.type=="int":
				return ["IMM R1, "+str(val)]
			else:
				print(expr)
				raise NotImplementedError("")

	elif type(expr)==c_ast.InitList:
		coms = []
		for x in expr.exprs:
			coms += [expression(x, inMethod)]
		return coms
	elif type(expr)==c_ast.ID:
		return getVariableMemoryAddress(expr.name, inMethod)
	elif type(expr)==c_ast.StructRef:
		if expr.type=="->":
			print(methods.methods)
			print(expr)
			raise NotImplementedError("")
			return getVariableMemoryAddress(expr.name.name+"."+expr.field.name, inMethod)
		elif expr.type==".":
			return getVariableMemoryAddress(expr.name.name+"."+expr.field.name, inMethod)
		else:
			print(expr)
			raise NotImplementedError("")
	elif type(expr)==c_ast.UnaryOp:
		return unaryOp(expr, inMethod, False)
	elif type(expr)==c_ast.ArrayRef:
		if methods.isIn(expr.name.name, inMethod):
			return expression(expr.subscript, inMethod)+["SUB R3, "+mpR+", "+methods.get(expr.name.name, inMethod), "LOAD R3, R3", "ADD R3, R3, R1", "LOAD R1, R3"]
		else:
			return expression(expr.subscript, inMethod)+["LOAD R3, "+str(varsInMemory.index(expr.name.name)), "ADD R3, R3, R1", "LOAD R1, R3"]




		
	else:
		print(expr)
		raise NotImplementedError("")


def binaryOp(binOp, inMethod, lazyTarget = None):
	op = binOp.op
	left = binOp.left
	right = binOp.right


	out = []
	out += expression(left, inMethod)+["MOV R2, R1"]

	r = expression(right, inMethod)+["MOV R3, R1"]
	if type(right) in [c_ast.FuncCall, c_ast.BinaryOp]:
		out += ["PSH R2"]+r+["POP R2"]
	else:
		out += r

	preCalcOps = ["/","+","-","*","%","==","!=","<=",">=","<",">"]
	
	if type(left)==c_ast.Constant and type(right)==c_ast.Constant and op in preCalcOps:
		op = op.replace("/","//")
		result = str(eval((str(left.value)+op+str(right.value))))
		result = result.replace("True","1")
		result = result.replace("False","0")
		
		return ["IMM, R1, "+result]


	if op=="+":
		out.append("ADD R1, R2, R3")
	elif op=="*":
		out.append("MLT R1, R2, R3")
	elif op=="-":
		out.append("SUB R1, R2, R3")
	elif op=="/":
		out.append("DIV R1, R2, R3")
	elif op=="&":
		out.append("AND R1, R2, R3")
	elif op=="|":
		out.append("OR R1, R2, R3")

	elif op=="&&":
		if lazyTarget:
			l = expression(left, inMethod)+["MOV R2, R1", lazyTarget]
			r = expression(right, inMethod)+["MOV R3, R1"]
			out = l+r
		else:
			out.append("SETNE R2, R2, 0")
			out.append("SETNE R3, R3, 0")
			out.append("AND R1, R2, R3")
	elif op=="||":
		if lazyTarget:
			l = expression(left, inMethod)+["MOV R2, R1", lazyTarget]
			r = expression(right, inMethod)+["MOV R3, R1"]
			out = l+r
		else:
			out.append("SETNE R2, R2, 0")
			out.append("SETNE R3, R3, 0")
			out.append("OR R1, R2, R3")
	
	elif op =="==":
		out.append("SETE R1, R2, R3")
	elif op =="!=":
		out.append("SETNE R1, R2, R3")
	elif op ==">":
		out.append("SETG R1, R2, R3")
	elif op =="<":
		out.append("SETL R1, R2, R3")
	elif op ==">=":
		out.append("SETGE R1, R2, R3")
	elif op =="<=":
		out.append("SETLE R1, R2, R3")

	else:
		print(op)
		raise NotImplementedError("")
	return out





















































def peepHoleIMM(asm, only_uncomment):
	modified = False
	reg = None
	val = None
	idx = None

	x = 0
	while x < len(asm):
		comm = [x.replace(",","") for x in asm[x].split(" ")]
		
		if comm[0] in ["IMM","STORE"]+branchingComms:
			x+=1
			continue

		if comm[0]=="IMM":
			print(">", comm)
			modified = False
			reg = comm[1]
			val = comm[2]
			idx = x

		if (len(comm)>1 and comm[1]==reg and comm[0]!="IMM") or comm[0].startswith("."):
			modified = True

		if not modified and (len(comm)>2 and comm[2]==reg):
			if only_uncomment:
				asm[idx] = "//"+asm[idx]
			else:
				del asm[idx]
				x-=1
			comm[2] = val
			asm[x] = comm[0]+" "+", ".join(comm[1:])
			print(comm)

		if not modified and (len(comm)>3 and comm[3]==reg):
			if only_uncomment:
				asm[idx] = "//"+asm[idx]
			else:
				del asm[idx]
				x-=1
			comm[3] = val
			asm[x] = comm[0]+" "+", ".join(comm[1:])
			print(comm)
		x+=1
	return asm



def peepHoleCopy(asm, only_uncomment):
	x = 0
	while x < len(asm):
		testComm = [g.replace(",","") for g in asm[x].split(" ")]
		if len(testComm)>1 and testComm[0] not in ["PSH","POP","OUT","IN"]+branchingComms:
			
			for y in range(x+1, len(asm)):
				comm = [g.replace(",","") for g in asm[y].split(" ")]

				if comm[0] in branchingComms or comm[0].startswith("."):
					break


				if len(comm)>1:
					if asm[y]==asm[x]:
						print(">",testComm)
						#print(asm[x+1:y])
						print("REMOVING:",comm)
	
						if only_uncomment:
							asm[y] = "//"+asm[y]
						else:
							
							del asm[y]
							x -= 1
						break
					elif (comm[0]!="STORE" and any([comm[1]==g for g in testComm[1:]])) or comm[0].startswith("."):
						break
		x+=1
	return asm	


def peepHoleSubAddZero(asm, only_uncomment=False):
	for x in reversed(range(len(asm))):
		comm = [g.replace(",","") for g in asm[x].split(" ")]
		if (comm[0]=="SUB" and comm[-1]=="0") or (comm[0]=="ADD" and (comm[-1]=="0" or comm[-2]=="0")):
			print(">",comm)
			if (comm[3]==comm[1] or comm[2]==comm[1]):
				print("REMOVE LINE")
				if only_uncomment:
					asm[x] = "//"+asm[x]
				del asm[x]
			else:
				print("REPLACEMENT: MOV "+comm[1]+", "+comm[2])
				asm[x] = "MOV "+comm[1]+", "+comm[2]
	return asm


def toASM(ast):
	coms = compound(ast)
	

	coms = ["IMM "+mpR+", "+str(len(varsInMemory))]+programInitComs+["CAL ._function_"+initFunc,"HLT","HLT","HLT","HLT"]+coms

	print("IMM OPTIM:")
	coms = peepHoleIMM(coms, onlyUncommentOptims)
	print("\nSUB/ADD 0 OPTIM:")
	coms = peepHoleSubAddZero(coms, onlyUncommentOptims)
	print("\nDOUBLE USE OPTIM:")
	coms = peepHoleCopy(coms, onlyUncommentOptims)
	
	return coms




out = open("out.urcl","w")
out.write("BITS >= 16\nMINREG 15\nMINRAM 1024\n\n\n")
for com in toASM(ast):
	if com.startswith("._function_skip"):
		out.write(com+"\n\n\n")
	elif com.startswith("BRA ._function_skip"):
		out.write("\n\n"+com+"\n")
	else:
		out.write(com+"\n")



print("\n\nMETHODS AND ITS VARS")
print([(key,value[::-1]) for (key,value) in methods.methods.items()])
print("GLOBAL VARS")
print(varsInMemory)
print("STRUCTS")
print(structs)
print("CONSTANTS")
print(constants)