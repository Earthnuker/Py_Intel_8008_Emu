from binascii import hexlify as tohex
import random
class Memory(object):
	
	def __init__(self,memsize):
		self.size=memsize
		self.mem=bytearray(memsize)
	
	def __getitem__(self,item):
		return self.mem[item]
		
	def __setitem__(self,item,value):
		self.mem[item]=value
		
	def dump(self,addr=0x0,length=None,width=16):
		addr*=width
		if length: length=addr+length*width
		else: length=None
		dmp=str(tohex(self.mem[addr:length]),'ascii')
		odmp=["Memory:\n"]
		odmp_p=""
		for addr,n in enumerate(dmp,(addr*2)+2*width):
			odmp_p+=n
			if len(odmp_p)==width*2:
				odmp_p="0x{:04x}: [{}]".format(1+addr//2-width*2,odmp_p)
				print(odmp_p)
				odmp_p=""
		return