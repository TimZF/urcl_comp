from pycparser import c_parser, c_ast, preprocess_file
import peepholeOptim

fileToCompile = "stackOverflow.c"
mpR = "R15"
initFunc = "main"
debugComments = True
onlyUncommentOptims = False
#harvardArchitecture = True #need to implement offset


urclEx = True





varsInMemory = []
constants = []

programInitComs = []

builtInMethods = {}


skipId = 0 
structs = {}
ptrToStruct = {}
dataStrings = []





class MethodsVarHolder():
	def __init__(self):
		self.methods = {}
		self.types = {}
		self.arraysMethods = {}

	def addMethod(self, method):
		self.methods[method] = []

	def append(self, varName, inMethod, typee):
		if type(inMethod)==list:
			inMethod = inMethod[-1]
		if inMethod:
			if varName in self.methods[inMethod]:
				raise NotImplementedError(f"VARIABLE {varName} ALREADY DEFINED IN THIS SCOPE {inMethod}")
			self.methods[inMethod].append(varName)
		self.types[inMethod+"."+varName] = typee

	def getType(self, varName, inMethod):
		return self.types[inMethod+"."+varName]

	def isIn(self, var, inMethod):
		if type(inMethod)==list:
			return any([var in self.methods[x] for x in inMethod])
		return (var in self.methods[inMethod])

	def get(self, var, inMethod):
		if type(inMethod)==list:
			return [str(self.methods[x].index(var)) for x in inMethod if self.isIn(var, x)][-1]
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
		return [add+f"for({debugADD(command.init,True)}); {debugADD(command.cond,True)}; {debugADD(command.next,True)})"]

	if type(command)==c_ast.If:
		return [add+"if("+debugADD(command.cond,True)+")"]

	if type(command)==c_ast.Return:
		return [add+"Return "+"".join(debugADD(command.expr))]

	if type(command)==c_ast.Typedef:
		return ["define type:"+command.name+" = "+"".join(debugADD(command.type))]

	if type(command)==c_ast.FuncCall:
		if sub:
			return add+"FuncCall "+command.name.name+"("+debugADD(command.args, True)+")"
		return [add+"FuncCall "+command.name.name+"("+debugADD(command.args, True)+")"]


	if type(command)==c_ast.DeclList:
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
		return f"({''.join(debugADD(command.left, True))} {command.op} {''.join(debugADD(command.right, True))})"

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

	if type(command)==c_ast.Struct:
		return ["//define struct:"+command.name]

	if type(command)==c_ast.StructRef:
		return "StructRef:"+command.name.name+command.type+command.field.name

	if type(command)==c_ast.Compound:
		return ["\n//{"+"".join([str(debugADD(x,True)) for x in command.block_items])+"}"]
		print(command)

		quit()


	if command==None:
		return ""
	if type(command)==c_ast.Typename:
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
		elif type(x) is c_ast.Compound:
			coms += create_compund(x, inMethod)
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
	elif x.op=="~":
		coms += ["NOT R1, R1"]
	elif x.op=="p++":
		coms += ["INC R1, R1"]
	elif x.op=="p--":
		coms += ["DEC R1, R1"]
	elif x.op=="&":
		coms = coms[:-1]
		coms += ["MOV R1, R3"]
		#coms = ["SUB R1, "+mpR+", "+methods.get(name, inMethod)]
	elif x.op=="*":
		coms = coms
		coms += ["LOAD R1, R1"]
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
			coms += ["BRZ "+skipToo]
			#if x.op==">":
			#	coms += ["BRZ "+skipToo, "BRN "+skipToo]
			#elif x.op=="<":
			#	coms += ["BRP "+skipToo, "BRZ "+skipToo]
			#elif x.op==">=":
			#	coms += ["BRN "+skipToo]
			#elif x.op=="<=":
			#	coms += ["BRP "+skipToo]
			#elif x.op=="==":
			#	coms += ["BNZ "+skipToo]
			#elif x.op=="!=":
			#	coms += ["BRZ "+skipToo]
			#else:
			#	print(x)
			#	raise NotImplementedError("")
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
			if x.lvalue.type=="->":
				strRef = x.lvalue
				structDef = structs[ptrToStruct[strRef.name.name]]
				fieldOffset = [x for x in range(len(structDef)) if structDef[x][0]==strRef.field.name][0]
				se = getVariableMemoryPtr(strRef.name.name, inMethod)+["LOAD R3, R3","SUB R3, R3, "+str(fieldOffset), "STORE R3, R1"]

			elif x.lvalue.type==".":
				se = setVariableMemoryAddress(x.lvalue.name.name+"."+x.lvalue.field.name, inMethod)
			else:
				print(x.lvalue)
				raise NotImplementedError("")
			

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
			if type(x.lvalue)==c_ast.UnaryOp and x.lvalue.op=="*":
				se = ["PSH R1"]+expression(x.lvalue.expr, inMethod)+["POP R2", "STORE R1, R2"]
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
		varsNeede = []
		for x in methods.methods[inMethod]:
			if x.split(".")[0]==varName:
				varsNeede += setVariableMemoryAddress(x, inMethod)

		return varsNeede
	else:

		return ["STORE "+str(varsInMemory.index(varName))+", R1"]

def getVariableMemoryAddress(varName, inMethod):
	if inMethod and methods.isIn(varName, inMethod):
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod),"LOAD R1, R3"]
	elif inMethod and any([x.split(".")[0]==varName for x in methods.methods[inMethod]]):
		#varsNeede = [getVariableMemoryAddress(x, inMethod) for x in methods.methods[inMethod] if x.split(".")[0]==varName]
		#if methods.getType(varName, inMethod)=="array":
		if methods.isIn(varName+".0", inMethod):
			return ["SUB R3, "+mpR+", "+methods.get(varName+".0", inMethod)]
		else:
			raise NotImplementedError()
		
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod)]#varsNeede
	else:
		return ["LOAD R1, "+str(varsInMemory.index(varName))]

def getVariableMemoryPtr(varName, inMethod):
	if inMethod and methods.isIn(varName, inMethod):
		return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod)]
	#elif inMethod and any([x.split(".")[0]==varName for x in methods.methods[inMethod]]):
	#	return ["SUB R3, "+mpR+", "+methods.get(varName, inMethod)]
	else:
		return ["IMM R3, "+str(varsInMemory.index(varName))]


def create_compund(x, inMethod):
	namy = inMethod+"_compund_"+str(skipId)

	methods.addMethod(namy)

	body = compound(x.block_items, [inMethod,namy])

	numVars = str(len(methods.methods[namy]))

	coms = ["ADD "+mpR+", "+mpR+", "+numVars]+body+["SUB "+mpR+", "+mpR+", "+numVars+"\n\n"]
	return coms

	




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
			code = []
			structdefinition = structs[c.type.type.name]

			#if inMethod:
			#	methods.append(c.name, inMethod, "StructPointer")
			#else:
			#	varsWeDeclare.append(c.name)

			if type(c)==c_ast.PtrDecl:
				name = c.type.declname
				init = None
				ptrToStruct[c.type.declname] = c.type.type.name
			else:
				ptrToStruct[c.name] = c.type.type.name
				name = c.name
				init = c.init

			if type(c)==c_ast.PtrDecl:
				varsWeDeclare.append(name)
				if "const" in c.quals:
					constants.append(name)
				elif inMethod:
					methods.append(name, inMethod, "Struct")
				else:
					varsInMemory.append(name)
				if init is not None:
					raise NotImplementedError("Cant init structs directly right now")

			else:
				for x in structdefinition:
					varsWeDeclare.append(name+"."+x[0])
					if "const" in c.quals:
						constants.append(name+"."+x[0])
					elif inMethod:
						methods.append(name+"."+x[0], inMethod, "Struct")
					else:
						varsInMemory.append(name+"."+x[0])
				
				if init is not None:
					codeExpr = expression(init, inMethod)
					for x in range(len(structdefinition)):
						varName = name+"."+structdefinition[x][0]
						code += codeExpr[x]+setVariableMemoryAddress(varName, inMethod)
			return code, varsWeDeclare

		elif type(c.type.type) == c_ast.IdentifierType and c.type.type.names[0]=="char":
			if type(c)==c_ast.PtrDecl:
				name = c.type.declname
				init = None
			else:
				name = c.name
				init = c.init


			if "const" in c.quals:
				constants.append(name)

			varsWeDeclare.append(name)
			if inMethod:
				methods.append(name, inMethod, "char")
			else:
				varsInMemory.append(c.type.declname)
			if init is not None:
				return expression(init, inMethod)+setVariableMemoryAddress(name, inMethod), varsWeDeclare

		elif type(c.type.type) == c_ast.IdentifierType and c.type.type.names[0]=="int":
			if type(c)==c_ast.PtrDecl:
				name = c.type.declname
				init = None
			else:
				name = c.name
				init = c.init

			if "const" in c.quals:
				constants.append(name)
			varsWeDeclare.append(name)
			if inMethod:
				methods.append(name, inMethod, "int")
			else:
				varsInMemory.append(name)
			if init is not None:
				return expression(init, inMethod)+setVariableMemoryAddress(name, inMethod), varsWeDeclare
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
				print("Just use malloc 4HEad")
				quit()
			elif type(c.type.dim)==c_ast.Constant or (c.type.dim.name in constants):
				initLen = int(c.type.dim.value)
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
#
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
				d = (x.name,x.type.type.type.names[0])
			else:
				print(c)
				raise NotImplementedError()

			structs[c.name].append(d)

	elif type(c.type)==c_ast.PtrDecl:

		#varsWeDeclare.append(c.name)
		#if "const" in c.quals:
		#	constants.append(c.name)
		#elif inMethod:
		#	methods.append(c.name, inMethod, "PtrDecl")
		#else:
		#	varsInMemory.append(c.name)

		code,vwd = declare(c.type, inMethod)

		
		if c.init is not None:
			if inMethod and methods.isIn(c.name, inMethod):
				return code+expression(c.init, inMethod)+["SUB R2, "+mpR+", "+methods.get(c.name, inMethod), "STORE R2, R1"], varsWeDeclare+vwd
			else:
				return code+expression(c.init, inMethod)+["STORE "+str(varsInMemory.index(c.name))+", R1"], varsWeDeclare+vwd
		else:
			return code, vwd

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
			structDef = structs[ptrToStruct[expr.name.name]]

			fieldOffset = [x for x in range(len(structDef)) if structDef[x][0]==expr.field.name]
			if len(fieldOffset)==0:
				raise NameError(f"The struct: {expr.name.name} does not have a field: {expr.field.name}" )

			coms = getVariableMemoryAddress(expr.name.name, inMethod)+["ADD R3, R1, "+str(fieldOffset[0]), "LOAD R1, R3"]
			return coms
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

	preCalcOps = ["/","+","-","*","%","==","!=","<=",">=","<",">"]

	if type(left)==c_ast.Constant and type(right)==c_ast.Constant and op in preCalcOps:
		op = op.replace("/","//").replace("!","not ")
		result = str(eval((str(left.value)+op+str(right.value))))
		result = result.replace("True","1")
		result = result.replace("False","0")
		return ["IMM R1, "+result]

	out = []
	

	out += expression(left, inMethod)+["MOV R2, R1"]

	r = expression(right, inMethod)+["MOV R3, R1"]
	if type(right) in [c_ast.FuncCall, c_ast.BinaryOp]:
		out += ["PSH R2"]+r+["POP R2"]
	else:
		out += r




	if op=="+":
		out.append(f"ADD R1, R2, R3")
	elif op=="*":
		out.append(f"MLT R1, R2, R3")
	elif op=="-":
		out.append(f"SUB R1, R2, R3")
	elif op=="/":
		out.append(f"DIV R1, R2, R3")
	elif op=="&":
		out.append(f"AND R1, R2, R3")
	elif op=="|":
		out.append(f"OR R1, R2, R3")
	elif op=="<<":
		out.append(f"BSL R1, R2, R3")
	elif op==">>":
		out.append(f"BSR R1, R2, R3")


	elif op=="&&":
		if lazyTarget:
			l = expression(left, inMethod)+["MOV R2, R1", lazyTarget]
			r = expression(right, inMethod)+["MOV R3, R1"]
			out = l+r
		else:
			out.append("SETNE R2, R3, 0")
			out.append("SETNE R2, R3, 0")
			out.append("AND R1, R2, R3")
	elif op=="||":
		#if lazyTarget:
		#	l = expression(left, inMethod)+["MOV R2, R1", lazyTarget]
		#	r = expression(right, inMethod)+["MOV R3, R1"]
		#	out = l+r
		#else:
		out.append("SETNE R2, R3, 0")
		out.append("SETNE R2, R3, 0")
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























def toASM(ast):
	coms = compound(ast)
	

	coms = ["IMM "+mpR+", "+str(len(varsInMemory))]+programInitComs+["CAL ._function_"+initFunc,"HLT","HLT","HLT","HLT"]+coms

	coms = peepholeOptim.optimize(coms, onlyUncommentOptims, initFunc)


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