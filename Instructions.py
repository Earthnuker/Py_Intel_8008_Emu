from Register import Register
from collections import OrderedDict
class I(object):
	
	def __init__(self,opcodes,args=('w','r'),size=1):
		for opcode in opcodes:
			if not (all([d in 'sdax01' for d in opcode]) and len(opcode)==8):
				raise RuntimeError('ivalid opcode: {}'.format(opcode))
		self.opcodes=opcodes
		self.args=args
		self.size=size
	
	def __call__(self,function):
		def func(cpu,*args):
			cpu=args[0]
			args=list(args)[1:]
			do_write=lambda *largs:None
			for n,arg in enumerate(zip(args,self.args)):
				arg,mode=arg
				if isinstance(arg,Register):
					if mode=='w':
						do_write=args[n].set
						args[n]=args[n].get()
					elif mode=='i':
						args[n]=args[n].n
					elif mode=='r':
						args[n]=args[n].get()
					continue
				if isinstance(arg,int):
					if mode=='r':
						continue
					if mode=='w':
						raise TypeError('Integer not supported as destination')
			rv=function(cpu,*args)
			do_write(rv)
		func.opcodes=self.opcodes
		func.__name__=function.__name__
		func.args=self.args
		func.size=self.size
		return func
	
	def __len__(self):
		return self.size

def get_input(cpu,port):
	if cpu.verbose:
		print("I:PORT:",port)
	if port in cpu.hw:
		return cpu.hw[port].input(cpu)
	return None
	
def set_output(cpu,port,value):
	if cpu.verbose:
		print("O:PORT:",port,"VALUE:",value)
	if port in cpu.hw:
		cpu.hw[port].output(cpu,value)
	
class Instructions:
	#opcode bits: s: src, d: dst ,a: addr, x: don't care
	def __init__(self,cpu):
		self.insts=list(filter(lambda x: not (x.startswith('_')), dir(self)))
		self.insts.remove('hlt')
		self.insts.insert(0,'hlt')
		cpu.opcodes=OrderedDict()
		cpu.opcode_names=OrderedDict()
		for inst in self.insts:
			inst=self.__getattribute__(inst)
			cpu.opcodes[inst.opcodes]=inst
			cpu.opcode_names[inst.__name__]=inst
		if len(set(cpu.opcodes))!=len(set(self.insts)):
			raise RuntimeError('Duplicate Opcode detected')
		self.cpu=cpu
		
	@I(('0000000x','11111111'),())
	def hlt(cpu):
		cpu.halted=True
		
	@I(('0100sss1',),('r',))
	def inp(cpu,r1):
		port=r1
		cpu.registers['A'][0]=get_input(cpu,port)
	
	@I(('0111sss1',),('r',))
	def out(cpu,r1):
		value=cpu.registers['A'][0]
		port=r1
		set_output(cpu,port,value)
	
	@I(('01xxx100',),(),3)
	def jmp(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		cpu.set_ip(addr+2)
	
	@I(('01000000',),(),3)
	def jnc(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if not cpu.flags['C']:
			cpu.set_ip(addr)
		
	@I(('01001000',),(),3)
	def jnz(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if not cpu.flags['Z']:
			cpu.set_ip(addr)
	
	@I(('01010000',),(),3)
	def jp(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if not cpu.flags['S']:
			cpu.set_ip(addr)
	
	@I(('01011000',),(),3)
	def jpo(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if cpu.flags['P']:
			cpu.set_ip(addr)
	
	@I(('01100000',),(),3)
	def jc(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if cpu.flags['C']:
			cpu.set_ip(addr)
	
	@I(('01101000',),(),3)
	def jz(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if cpu.flags['Z']:
			cpu.set_ip(addr)
	
	@I(('01110000',),(),3)
	def jm(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if cpu.flags['S']:
			cpu.set_ip(addr)
	
	@I(('01111000',),(),3)
	def jpe(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-5
		if not cpu.flags['P']:
			cpu.set_ip(addr)
	
	
	@I(('01xxx110',),(),3)
	def call(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		cpu.stack.push(cpu.get_ip())
		cpu.set_ip(addr)
	
	
	@I(('01000010',),(),3)
	def cnc(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if not cpu.flags['C']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01001010',),(),3)
	def cnz(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if not cpu.flags['Z']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01010010',),(),3)
	def cp(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if not cpu.flags['S']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01011010',),(),3)
	def cpo(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if cpu.flags['P']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01100010',),(),3)
	def cc(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if cpu.flags['C']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	
	@I(('01101010',),(),3)
	def cz(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if cpu.flags['Z']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01110010',),(),3)
	def cm(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if cpu.flags['S']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
	
	@I(('01111010',),(),3)
	def cpe(cpu,*data):
		addr=(int.from_bytes(data,'little')&((1<<14)-1))-3
		if not cpu.flags['P']:
			cpu.stack.push(cpu.get_ip())
			cpu.set_ip(addr)
			
	@I(('00xxx111',),(),1)
	def ret(cpu):
		addr=cpu.stack.pop()+2
		cpu.set_ip(addr)
	
	@I(('00000011',),(),1)
	def rnc(cpu):
		if not cpu.flags['C']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('00001011',),(),1)
	def rnz(cpu):
		if not cpu.flags['Z']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('00010011',),(),1)
	def rp(cpu):
		if not cpu.flags['S']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('01011011',),(),1)
	def rpo(cpu):
		if cpu.flags['P']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('00100011',),(),1)
	def rc(cpu):
		if not cpu.flags['C']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('00101011',),(),1)
	def rz(cpu):
		if cpu.flags['Z']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
			
	@I(('00110011',),(),1)
	def rm(cpu):
		if cpu.flags['S']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
			
	@I(('00111011',),(),1)
	def rpe(cpu):
		if not cpu.flags['P']:
			addr=cpu.stack.pop()+2
			cpu.set_ip(addr)
	
	@I(('00aaa101',),('i',))
	def rst(cpu,r1):
		addr=(r1&((1<<3)-1))<<3
		cpu.stack.push(cpu.get_ip())
		cpu.set_ip(addr)
	
	@I(('00ddd110',),('w',),2)
	def mvi(cpu,r1,*data):
		return data[0]
	
	@I(('11dddsss',))
	def mov(cpu,r1,r2):
		return r2
	
	@I(('00ddd000',),('w',))
	def inc(cpu,r1):
		return r1+1
	
	@I(('00ddd001',),('w',))
	def dec(cpu,r1):
		return r1-1
	
	@I(('10000sss',),('r',))
	def add(cpu,r1):
		cpu.registers['A'][0]+=r1
	
	@I(('00000100',),(),2)
	def adi(cpu,*data):
		cpu.registers['A'][0]+=data[0]
		
	@I(('10001sss',),('r',))
	def adc(cpu,r1):
		cpu.registers['A'][0]+=r1[0]+cpu.flags['C']
	
	@I(('00001100',),(),2)
	def aci(cpu,*data):
		cpu.registers['A'][0]+=data[0]+cpu.flags['C']
		
	@I(('10010sss',),('r',))
	def sub(cpu,r1):
		cpu.registers['A'][0]-=r1
	
	@I(('00010100',),(),2)
	def sui(cpu,*data):
		cpu.registers['A'][0]-=data[0]
		
	@I(('10011sss',),('r',))
	def sbb(cpu,r1):
		cpu.registers['A'][0]-=r1[0]+cpu.flags['C']
	
	@I(('00011100',),('r',),2)
	def sbi(cpu,*data):
		cpu.registers['A'][0]-=data[0]+cpu.flags['C']
		
	@I(('10100sss',),('r',))
	def ana(cpu,r1):
		cpu.registers['A'][0]&=r1
	
	@I(('00100100',),('r',),2)
	def ani(cpu,*data):
		cpu.registers['A'][0]&=data[0]
		
	@I(('10101sss',),('r',))
	def xra(cpu,r1):
		cpu.registers['A'][0]^=r1
	
	@I(('00101100',),('r',),2)
	def xri(cpu,*data):
		cpu.registers['A'][0]^=data[0]
		
	@I(('10110sss',),('r',))
	def ora(cpu,r1):
		cpu.registers['A'][0]|=r1
	
	@I(('00110100',),('r',),2)
	def ori(cpu,*data):
		cpu.registers['A'][0]|=data[0]
			
	@I(('10111sss',),('r',))
	def cmp(cpu,r1):
		cpu.update_flags(cpu.registers['A'][0],r1)
	
	@I(('00111100',),('r',),2)
	def cpi(cpu,*data):
		cpu.update_flags(cpu.registers['A'][0],data[0])
	
	@I(('00000010',),())
	def rlc(cpu):
		tip=cpu.registers['A'][0]&(1<<cpu.bits-1)
		cpu.registers['A'][0]=(cpu.registers['A'][0]<<1)+int(bool(tip))

	@I(('00001010',),())
	def rrc(cpu):
		tail=cpu.registers['A'][0]&1
		cpu.registers['A'][0]=(cpu.registers['A'][0]>>1)+(int(bool(tail))<<(cpu.bits-1))

	@I(('00010010',),())
	def ral(cpu):
		new_carry=int(bool(cpu.registers['A'][0]&(1<<cpu.bits-1)))
		old_carry=cpu.flags['C']
		cpu.registers['A'][0]=(cpu.registers['A'][0]<<1)+int(bool(old_carry))
		cpu.flags['C']=new_carry

	@I(('00011010',),())
	def rar(cpu):
		new_carry=cpu.registers['A'][0]&1
		old_carry=cpu.flags['C']
		cpu.registers['A'][0]=(cpu.registers['A'][0]>>1)+(int(bool(old_carry))<<(cpu.bits-1))
		cpu.flags['C']=new_carry
	#TODO Recheck Opcodes
