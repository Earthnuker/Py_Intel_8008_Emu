from Register import Register
from Memory import Memory
from Stack import Stack
from Instructions import Instructions
class CPU(object):
	
	def __init__(self,verbose=False):
		self.verbose=verbose
		self.bits=8
		self.memsize=1<<14
		self.stackwidth=14
		self.lis=1
		self.inst_bin=None
		self.halted=False
		self.hw={}
		if self.verbose:print("Init Regs...")
		self.registers={}
		for n,rn in enumerate(['A','B','C','D','E','L','M']):
			self.registers[rn]=Register(rn,self.bits,n)
		self.registers['H']=Register('H',6)
		self.registers['PC']=Register('PC',14)
		self.flags=0
		self.flags=dict(zip('CZSP',(0,0,0,0))) #sign zero parity carry
		if self.verbose:print("Init Mem...")
		self.memory=Memory(self.memsize)
		if self.verbose:print("Init Stack...")
		self.stack=Stack(7,self.stackwidth,self.memory)
		if self.verbose:print('Init Instructions...')
		Instructions(self)
		if self.verbose:print('Init Breakpoints...')
		self.breakpoints=[]
		
	def __call__(self):
		self.set_ip(int.from_bytes(self.memory[:2],'little')) # read PC from Stack
		self.inc_ip(self.lis) #Increment PC
		self.memory[0]=self.get_ip()&0xff # Write PC Back to top of Stack
		self.memory[1]=(self.get_ip()&0xff00)>>8 # Write PC Back to top of Stack
		self.memory[2:self.stack.levels+2]=self.stack.stackmem # write Stack to memory
		self.registers['M'][0]=self.memory[(self.registers['H'][0]<<self.bits)+self.registers['L'][0]] #Update M Register
		self.memory[(self.registers['H'][0]<<self.bits)+self.registers['L'][0]]=self.registers['M'][0] # Write back M register
		self.inst_byte=self.memory[self.registers['PC'][0]] # Read Instruction Byte
		self.inst_bin='{:08b}'.format(self.inst_byte) # Convert to binary to do Mask-Matching
		self.lis=self.exec_inst(self.inst_bin)
		if self.registers['PC'][0] in self.breakpoints:
			return False
		return not self.halted
	
	def hw_attach(self,hw):
		if self.verbose:
			print('Init {} @ Port {} ...'.format(hw.__class__.__name__,hw.port))
		self.hw[hw.port]=hw
		return
	
	def exec_inst(self,inst_bin):
		opcs=[]
		opc=None
		bin_to_reg={}
		for rn,rb in self.registers.items():
			if rb.binv:
				bin_to_reg[rb.binv]=rn
		for opcodes in self.opcodes:
			for opcode in opcodes:
				if all(map(lambda x,y:((x==y)==(x in '01' and y in '01')) ,inst_bin,opcode)):
					opts={}
					for k,v in list(filter(lambda x:bool(x),((y,x) if y in 'sdax' else '' for x,y in zip(inst_bin,opcode)))):
						if k!='x':
							if k not in opts:
								opts[k]=v
							else:
								opts[k]+=v
					inst=list(filter(lambda x: opcode in x,list(self.opcodes.keys())))[0]
					if opc==None:
						opc=[self.opcodes[inst].__name__,opts]
		if self.verbose:
			print(opc,inst_bin)
		if opc:
			opc[0]=self.opcode_names[opc[0]]
			for k in opc[1]:
				if opc[1][k] in bin_to_reg:
					opc[1][k]=self.registers[bin_to_reg[opc[1][k]]]
			inst=opc[0]
			args=opc[1]
			data=[]
			if inst.size!=1:
				for n in range(1,inst.size):
					data.append(self.memory[self.registers['PC'][0]+n])
			if self.verbose:
				print(inst.__name__,args,data)
			if 's' in args and 'd' in args:
				if inst.size==1:
					inst(self,args['d'],args['s'])
				else:
					inst(self,args['d'],args['s'],*data)
			if 'd' in args and not 's' in args:
				if inst.size==1:
					inst(self,args['d'])
				else:
					inst(self,args['d'],*data)
			if 's' in args and not 'd' in args:
				if inst.size==1:
					inst(self,args['s'])
				else:
					inst(self,args['s'],*data)
			if 'a' in args:
				if inst.size==1:
					inst(self,args['a'])
				else:
					inst(self,args['a'],*data)
			if not args:
				if inst.size==1:
					inst(self)
				else:
					inst(self,*data)
		elif self.inst_byte in (0x22,0x32,0x2a,0x38,0x39,0x3a): # undefine opcodes
			pass
		else:
			raise RuntimeWarning("Instruction not found: {} ({},{:X})".format(self.inst_byte,inst_bin,self.inst_byte))
		#for n in range(1,inst.size):
		#	self.registers['PC'][0]+=1
		return inst.size
						
	def set_ip(self,ip):
		self.registers['PC'][0]=ip
		self.memory.mem[0]=ip&0xff
		self.memory.mem[1]=(ip&0xff00)>>8
	
	def get_ip(self):
		return self.registers['PC'][0]
	
	def inc_ip(self,value):
		self.registers['PC'][0]=self.registers['PC'][0]+value
		
	def dumpregs(self):
		for rn in sorted(self.registers):
			print(self.registers[rn])
	
	def clf(self):
		self.flags=dict(zip('SZPC',(0,0,0,0))) #sign zero parity carry
	
	def load(self,filename=None,code=None,address=0):
		if self.verbose:print("Load Programm...")
		if filename and not code:
			try:
				with open(filename,'rb') as inf:
					code=inf.read()
			except Exception as e:
				print(e)
				return
		if not code:
			raise RuntimeError('No Loadeble Code supplied!')
		if len(code)>self.memsize:
			raise RuntimeError('Assembled code is too large to fit into RAM')
		for p,b in enumerate(code):
			if p<(self.stackwidth+2):
				address=0
			self.memory[p+address]=b
		self.set_ip(int.from_bytes(self.memory[:2],'little'))
		self.memory[0]=self.get_ip()&0xff # Write PC Back to top of Stack
		self.memory[1]=(self.get_ip()&0xff00)>>8 # Write PC Back to top of Stack
		self.memory[2:self.stack.levels+2]=self.stack.stackmem
		
	def update_flags(self,v1,v2):
		o=v1-v2
		ro=o&((1<<self.bits)-1)
		self.flags['S']=int(o<0)
		self.flags['Z']=int(ro==0)
		self.flags['P']=sum(map(int,'{:b}'.format(ro)))%2
		self.flags['C']=int(ro!=o)
	
		