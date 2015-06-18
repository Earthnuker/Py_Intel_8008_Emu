class Stack(object):
	
	def __init__(self,levels,width,memory):
		self.levels=levels*2
		self.width=width
		self.stackmem=memory.mem[:self.levels]
	
	def push(self,value):
		value=value&((1<<self.width)-1)
		for b in int.to_bytes(value,2,'little'):
			self.stackmem.insert(0,b)
		self.stackmem=self.stackmem[:self.levels]
	def pop(self):
		ret=(self.stackmem[0]<<8)+self.stackmem[1]
		del self.stackmem[0]
		del self.stackmem[0]
		self.stackmem.append(0)
		self.stackmem.append(0)
		return ret
