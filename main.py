import sys,os
from CPU import *
from Hardware import Console
cpu=CPU(verbose=0)
cpu.hw_attach(Console())
cpu.load(sys.argv[1])
inp="c"
#sys.stdout=open(os.devnull,'w')
while True:
	if cpu.verbose:
		cpu.dumpregs()
		print("Flags:",cpu.flags)
		print("Memory:")
		cpu.memory.dump(length=8,width=32)
		print('-'*10)
	if inp!="c":
		inp=input(">")
	if not cpu():
		break