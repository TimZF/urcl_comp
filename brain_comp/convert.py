fileToConvert = "hw.bf"
doesTheCPUHaveMoreThen8Bit = True



operations = ["<",">",".",",","+","-","[","]"]
coms = [f"IMM R1, 0", f"STORE R1, R0"]

ops = [x for x in open(fileToConvert,"r").read() if x in operations]

nJumps = 0

maxAddress = -1
currAddres = 0

jumpsAdd = []

for op in ops:
	if op==">":
		currAddres += 1
		coms += [f"STORE R1, R2", f"INC R1, R1", f"LOAD R2, R1"]
		if currAddres>maxAddress:
			maxAddress = currAddres
	elif op=="<":
		currAddres -= 1
		coms += [f"STORE R1, R2", f"DEC R1, R1", f"LOAD R2, R1"]
	elif op==".":
		coms += [ f"OUT 3, R2"]
	elif op=="+":
		coms += [f"INC R2, R2"]
		if doesTheCPUHaveMoreThen8Bit:
			coms += ["AND R2, R2, 255"]
	elif op=="-":
		coms += [f"DEC R2, R2"]
		if doesTheCPUHaveMoreThen8Bit:
			coms += ["AND R2, R2, 255"]
	elif op=="[":
		nJumps += 1
		jumpsAdd.append(nJumps)
		coms += [f"MOV R3, R2", f"BRZ .target_forwards_{jumpsAdd[-1]}", f".target_backwards_{jumpsAdd[-1]}"]
		
	elif op=="]":
		coms += [f"MOV R3, R2", f"BNZ .target_backwards_{jumpsAdd[-1]}", f".target_forwards_{jumpsAdd[-1]}"]
		jumpsAdd = jumpsAdd[:-1]

	#elif op==",":
	#	coms += [IN R1, 3""]


setToZero = []
for x in range(maxAddress):
	setToZero += [f"IMM R1, {x}", "STORE R1, R0"]

coms = setToZero+coms
print(jumpsAdd, maxAddress, nJumps)

with open("out.urcl","w") as f:
	a = (">=8" if doesTheCPUHaveMoreThen8Bit else "8")
	f.write(f"BITS {a}\nMINREG 3\nMINRAM {maxAddress+1}\n\n")
	for c in coms:
		f.write(c+"\n")

	f.write("HLT\n")
