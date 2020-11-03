
fileToConvert = "hw.bf"
dataPtrRegsiter = "R1"


operations = ["<",">",".",",","+","-","[","]"]
coms = [f"IMM {dataPtrRegsiter}, 0", f"STORE {dataPtrRegsiter}, R0"]

ops = [x for x in open(fileToConvert,"r").read() if x in operations]

nJumps = 0

maxAddress = -1
currAddres = 0

jumpsAdd = []

for op in ops:
	if op==">":
		currAddres += 1
		coms += ["//>",f"STORE {dataPtrRegsiter}, R2", f"INC {dataPtrRegsiter}, {dataPtrRegsiter}", f"LOAD R2, {dataPtrRegsiter}"]
		if currAddres>maxAddress:
			maxAddress = currAddres
	elif op=="<":
		currAddres -= 1
		coms += ["//<",f"STORE {dataPtrRegsiter}, R2", f"DEC {dataPtrRegsiter}, {dataPtrRegsiter}", f"LOAD R2, {dataPtrRegsiter}"]
	elif op==".":
		coms += ["//.", f"OUT 3, R2"]
	elif op=="+":
		coms += ["//+",f"INC R2, R2", "AND R2, R2, 255"]
	elif op=="-":
		coms += ["//-",f"DEC R2, R2", "AND R2, R2, 255"]
	elif op=="[":
		nJumps += 1
		jumpsAdd.append(nJumps)
		coms += ["//[",f"MOV R3, R2", f"BRZ .target_forwards_{jumpsAdd[-1]}", f".target_backwards_{jumpsAdd[-1]}"]
		
	elif op=="]":
		coms += ["//]",f"MOV R3, R2", f"BNZ .target_backwards_{jumpsAdd[-1]}", f".target_forwards_{jumpsAdd[-1]}"]
		jumpsAdd = jumpsAdd[:-1]

	#elif op==",":
	#	coms += [IN R1, 3""]



#for x in reversed(range(len(coms))):
#	if coms[x].startswith("LOAD") and coms[x-1].startswith("STORE"):
#		del coms[x]
#		del coms[x-1]
#
setToZero = []
for x in range(maxAddress):
	setToZero += [f"IMM R1, {x}", "STORE R1, R0"]

coms = setToZero+coms
print(jumpsAdd, maxAddress, nJumps)

with open("out.urcl","w") as f:
	for c in coms:
		f.write(c+"\n")

	f.write("HLT\n")
