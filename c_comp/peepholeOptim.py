branchingComms = ["CAL","RET","BRA","BRC","BNC","BRZ","BNZ","BRN","BRP","BRL","BRG","BRE","BNE","BOD","BEV","BLE","BGE"]



def collectVars(currScope):
	return currScope.vars+sum([collectVars(x) for x in currScope.children], [])


def regOptim(asm, scopeTree, usableRegs):
	currScope = scopeTree
	regOptim = False
	optimScope = None
	placements = {}

	idx = 0
	while idx<len(asm):
		if asm[idx].startswith("#pragma reg"):
			regOptim = True
			del asm[idx]
			idx -= 1

		elif asm[idx].startswith("ENTERSCOPE_"):
			found = False
			for child in currScope.children:
				if child.name==asm[idx][11:]:
					currScope = child
					found = True
			if not found:
				raise Exception(f"SCOPE {asm[idx][11:]} NOT FOUND EXCEPTION! AVAILABLE SCOPES:{currScope}")


			varsInScope = collectVars(currScope)#sum([x.vars for x in currScope.children], [])+currScope.vars


			if regOptim and optimScope==None:
				if len(varsInScope)<len(usableRegs):
					optimScope = currScope
					placements = {}
					for x in range(len(varsInScope)):
						placements[varsInScope[x]] = usableRegs[x]
					print(f"OPTIMIZED REG PLACEMENT FOR {currScope.name}")
					print(placements)
				else:
					print("WARNING: tried to use reg pragma but to many local variables")

		elif asm[idx].startswith("LEAVESCOPE_"):
			
			n2Leave = int(asm[idx][11:])
			for gg in range(n2Leave):
				if optimScope!=None and currScope.name==optimScope.name:
					regOptim = False
					optimScope = None
				currScope = currScope.parent

		elif regOptim:
			if asm[idx].startswith("SUB R3, R15, ") and "!" in asm[idx]:
				var = asm[idx].split("!")[-1]
				if var in placements:
					replacementReg = placements[var]
					del asm[idx] 
					if asm[idx].startswith("LOAD"):
						asm[idx] = f"MOV {asm[idx].split(' ')[1]} {replacementReg}"
					if asm[idx].startswith("STORE"):
						asm[idx] = f"MOV {replacementReg}, {asm[idx].split(',')[-1].strip()}"
		
			elif asm[idx].startswith("CAL"):
				currScope
				regs = list(placements.values())
				for reg in regs:
					asm.insert(idx, f"PSH {reg}")

				for reg in reversed(regs):
					asm.insert(idx+len(regs)+1, f"POP {reg}")
				idx += len(reg)+4
		idx+=1

	return asm


















def peepHoleBS_SH(asm, only_uncomment):
	x = 0

	while x<len(asm):
		if asm[x]=="IMM R1, 1" and asm[x+1]=="MOV R3, R1" and asm[x+2]=="BSL R1, R2, R3":
			print("> REPLACE BSL R1, R2, R3")
			asm[x] = "LSH R1, R2"
			if only_uncomment:
				asm[x+1] = "//"+asm[x+1]
				asm[x+2] = "//"+asm[x+2]
			else:
				del asm[x+1]
				del asm[x+1]
			x-=3
		elif asm[x]=="IMM R1, 1" and asm[x+1]=="MOV R3, R1" and asm[x+2]=="BSR R1, R2, R3":
			print("> REPLACE BSR R1, R2, R3")
			asm[x] = "RSH R1, R2"
			if only_uncomment:
				asm[x+1] = "//"+asm[x+1]
				asm[x+2] = "//"+asm[x+2]
			else:
				del asm[x+1]
				del asm[x+1]
			x-=3
		x+=1

	return asm
	#quit()




def peepHoleIMM(asm, only_uncomment):
	modified = False
	reg = None
	val = None
	idx = None

	x = 0
	while x < len(asm):
		comm = [x.replace(",","") for x in asm[x].split(" ")]
		
		if comm[0] in ["STORE"]+branchingComms:
			x+=1
			continue

		if comm[0]=="IMM":
			print(">", comm)
			modified = False
			reg = comm[1]
			val = comm[2]
			idx = x


		elif (len(comm)>1 and comm[1]==reg) or comm[0].startswith("."):
			modified = True

		elif not modified and (comm[0]=="MOV" and comm[2]==reg):
			if only_uncomment:
				asm[idx] = "//"+asm[idx]
			else:
				del asm[idx]
				x-=1
			comm[2] = val
			asm[x] = "IMM"+" "+", ".join(comm[1:])
			print(comm)

		elif not modified and (len(comm)>2 and comm[2]==reg):
			if only_uncomment:
				asm[idx] = "//"+asm[idx]
			else:
				del asm[idx]
				x-=1
			comm[2] = val
			asm[x] = comm[0]+" "+", ".join(comm[1:])
			print(comm)

		elif not modified and (len(comm)>3 and comm[3]==reg):
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
		if len(testComm)>1 and testComm[0] not in ["PSH","POP","OUT","IN","LOAD","STORE"]+branchingComms:
			
			for y in range(x+1, len(asm)):
				comm = [g.replace(",","") for g in asm[y].split(" ")]

				if comm[0] in branchingComms or comm[0].startswith(".") or comm[0].startswith("//") or comm[0].startswith("\n//"):
					break


				if len(comm)>1:
					if asm[y]==asm[x]:
						print(">",testComm)
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





def peepHoleDoubleLoad(asm, only_uncomment):
	x = 0

	loadingAddress = ""
	storingAddress = ""

	while x < len(asm):
		testComm = [g.replace(",","") for g in asm[x].split(" ")]
		if testComm[0]=="LOAD":
			if len(loadingAddress)==0:
				loadingAddress = testComm[2]
				storingAddress = testComm[1]
			elif loadingAddress==testComm[2]:
				print("REPLACE")
				print(">", testComm)
				asm[x] = "MOV "+testComm[1]+", "+storingAddress
				loadingAddress = ""
				storingAddress = ""

		elif testComm[0] in ["PSH","POP","OUT","IN","STORE"]+branchingComms or (len(testComm)>1 and (testComm[1]==loadingAddress or testComm[1]==storingAddress)):
			loadingAddress = ""
			storingAddress = ""

		x+=1
	return asm	



def peepHoleSubAddZeroOne(asm, only_uncomment):
	for x in reversed(range(len(asm))):
		comm = [g.replace(",","") for g in asm[x].split(" ")]
		if (comm[0]=="SUB" and comm[-1]=="0") or (comm[0]=="ADD" and (comm[-1]=="0" or comm[-2]=="0")):
			print(">",comm)
			if (comm[3]==comm[1] or comm[2]==comm[1]):
				print("REMOVE LINE")
				if only_uncomment:
					asm[x] = "//"+asm[x]
				else:
					del asm[x]
			else:
				print("REPLACEMENT: MOV "+comm[1]+", "+comm[2])
				asm[x] = "MOV "+comm[1]+", "+comm[2]


		if (comm[0]=="SUB" and comm[-1]=="1") or (comm[0]=="ADD" and (comm[-1]=="1" or comm[-2]=="1")):
			print(">",comm)
			if comm[0]=="SUB":
				print("REPLACEMENT: DEC "+comm[1]+", "+comm[2])
				asm[x] = "DEC "+comm[1]+", "+comm[2]
			else:
				print("REPLACEMENT: INC "+comm[1]+", "+comm[2])
				asm[x] = "INC "+comm[1]+", "+comm[2]
	return asm



def peepHoleUselessMove(asm, only_uncomment):
	for x in reversed(range(len(asm))):
		comm = [g.replace(",","") for g in asm[x].split(" ")]
		if comm[0]=="MOV" and comm[1]==comm[2]:
			print(">",comm)
			if only_uncomment:
				asm[x] = "//"+asm[x]
			else:
				del asm[x]
	x = 0
	while x<len(asm):
		comm = [g.replace(",","") for g in asm[x].split(" ")]
		#(comm[1]=="R1" or comm[1]=="R2")
		if comm[0]=="MOV" and (comm[1]=="R1" or comm[1]=="R2" or comm[1]=="R3") and comm[2][0]=="R" and not (comm[2]=="R1" or comm[2]=="R2" or comm[2]=="R3"):
			del asm[x]
			y = x
			orig = comm[1]
			new = comm[2]

			optimized = False
			while y<len(asm):
				commT = [g.replace(",","") for g in asm[y].split(" ")]
				if commT[0] in ["STORE","PUSH"] and commT[1]==orig:
					asm[y] = f"{commT[0]} "+", ".join([new]+commT[2:]) 
					print(commT,asm[y])
					optimized = True
					y = x-1
				if len(commT)==3 and commT[2]==orig:
					asm[y] = f"{commT[0]} {commT[1]}, {new}"
					print(commT,asm[y])
					optimized = True
					y = x-1
				elif len(commT)==4 and commT[3]==orig:
					asm[y] = f"{commT[0]} {commT[1]}, {commT[2]}, {new}"
					print(commT,asm[y])
					optimized = True
					y = x-1
				elif len(commT)==4 and commT[2]==orig:
					asm[y] = f"{commT[0]} {commT[1]}, {new}, {commT[3]}"
					print(commT,asm[y])
					optimized = True
					y = x-1

				if (len(commT)>=2 and commT[1]==orig) or commT[0] in branchingComms:
					break
				y+=1
			if optimized:
				x -= 1

		x += 1
	return asm



def peepHoleIncMove(asm, only_uncomment):
	#INC R1, R6
	#MOV R6, R1
	x = 0
	while x<len(asm):
		if asm[x].startswith("INC R1, ") and asm[x+1].startswith("MOV "):
			comm = [g.replace(",","") for g in asm[x].split(" ")]
			commNext = [g.replace(",","") for g in asm[x+1].split(" ")]

			asm[x] = f"INC {commNext[1]}, {comm[-1]}"
			if only_uncomment:
				asm[x+1] = "//"+asm[x+1]
			else:
				del asm[x+1]
			

		x+=1

	return asm




def peepHoleRemoveUnusedMethods(asm, only_uncomment, initFunc):
	methodsThatGetCalled = [initFunc]
	methods = {}



	for x in range(len(asm)):
		comm = [g.replace(",","") for g in asm[x].split(" ")]
		if comm[0]=="BRA" and comm[1].startswith("._function_skip_"):
			methods[comm[1].replace("._function_skip_", "")] = [x]
		if comm[0].startswith("._function_skip_"):
			methods[comm[0].replace("._function_skip_", "")].append(x)

	

	x = 0
	while x<len(methodsThatGetCalled):
		rangy = methods[methodsThatGetCalled[x]]
		for c in range(rangy[0],rangy[1]+1):
			comm = [g.replace(",","") for g in asm[c].split(" ")]
			if comm[0]=="CAL":
				func = comm[1].replace("._function_", "")
				if func not in methodsThatGetCalled:
					methodsThatGetCalled.append(func)
		x+=1
	print("FUNCTIONS THAT GET ACTUALLY CALLED:")
	print(methodsThatGetCalled,"\n")

	for method,rangy in methods.items():
		if method not in methodsThatGetCalled:
			print("REMOVING")
			print(">",method,"in range", rangy)
			x = rangy[0]
			for off in range(rangy[1]+1-rangy[0]):
				if only_uncomment:
					asm[x+off] = "//"+asm[x+off]
				else:
					del asm[x]

			if not only_uncomment:
				off = rangy[1]+1-rangy[0]
				for func in methods.keys():
					methods[func][0] -= off
					methods[func][1] -= off

	return asm






def optimize(coms, only_uncomment, initFunc, runs=1):
	print("\nRemove Unused Methods OPTIM:")
	coms = peepHoleRemoveUnusedMethods(coms, only_uncomment, initFunc)

	for x in range(runs):
		print("\n========OPTIMIZE RUN "+str(x)+"========")
		print("\nINC OPTIM")
		coms = peepHoleIncMove(coms, only_uncomment)
		print("\nIMM OPTIM:")
		coms = peepHoleIMM(coms, only_uncomment)
		print("\nDOUBLE USE OPTIM:")
		#coms = peepHoleCopy(coms, only_uncomment)
	
	
		print("\nSUB/ADD 0 OPTIM:")
		coms = peepHoleSubAddZeroOne(coms, only_uncomment)
		print("\nSHIFT OPTIM:")
		coms = peepHoleBS_SH(coms, only_uncomment)
	
		
		print("\nDoubleLoading OPTIM:")
		coms = peepHoleDoubleLoad(coms, only_uncomment)

		print("\nUselessMove OPTIM:")
		coms = peepHoleUselessMove(coms, only_uncomment)

	return coms