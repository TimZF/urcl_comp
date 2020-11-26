branchingComms = ["CAL","RET","BRA","BRC","BNC","BRZ","BNZ","BRN","BRP","BRL","BRG","BRE","BNE","BOD","BEV","BLE","BGE"]

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
		print("\nIMM OPTIM:")
		coms = peepHoleIMM(coms, only_uncomment)
		print("\nDOUBLE USE OPTIM:")
		coms = peepHoleCopy(coms, only_uncomment)
	
	
		print("\nSUB/ADD 0 OPTIM:")
		coms = peepHoleSubAddZeroOne(coms, only_uncomment)
		print("\nSHIFT OPTIM:")
		coms = peepHoleBS_SH(coms, only_uncomment)
	
		
		print("\nDoubleLoading OPTIM:")
		coms = peepHoleDoubleLoad(coms, only_uncomment)

		print("\nUselessMove OPTIM:")
		coms = peepHoleUselessMove(coms, only_uncomment)

	return coms