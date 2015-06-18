from Assembler import asmsh,asm_file
from CPU import CPU
import cmd,readline

class Shell(cmd.Cmd):
	prompt='8008>'
	initialized=False
	def do_help(self,args):
		rargs='do_'+args
		if args and rargs in dir(self) and hasattr(self.__getattribute__(rargs),'__doc__'):
			if self.__getattribute__(rargs).__doc__:
				for line in self.__getattribute__(rargs).__doc__.splitlines():
					print(line.strip())
		elif args and not rargs in dir(self):
			print('Command "{}" does not exists'.format(args))
		else:
			for cmd in dir(self):
				if cmd.startswith('do_') and hasattr(self.__getattribute__(cmd),'__doc__'):
					if self.__getattribute__(cmd).__doc__:
						print(cmd[3:]+':',self.__getattribute__(cmd).__doc__)
			
	def do_asm(self,args):
		"""Enter Assembling mode"""
		self.lastcmd=''
		try:
			if self.initialized:
				self.cpu.load(code=asmsh())
			else:
				print('CPU not Initialized')
		except Exception as e:
			print(e)

	def do_asm_img(self,args):
		"""Enter Assembling mode (RAM Image Output)"""
		self.lastcmd=''
		try:
			if self.initialized:
				self.cpu.load(code=asmsh(fill=True))
			else:
				print('CPU not Initialized')
		except Exception as e:
			print(e)
	
	def do_asm_file(self,args):
		"""Load Assembler File"""
		file=args
		fill=True
		if len(args)>1:
			fill=args[1]	
		if self.initialized:
			self.cpu.load(code=asm_file(file,fill))
		else:
			print('CPU not Initialized')
		
	def do_init(self,args):
		"""Initialize the CPU"""
		verbose=bool(args)
		self.cpu=CPU(verbose)
		self.initialized=True
	
	def do_load(self,args):
		"""Load Assembled Program into RAM"""
		if len(args):
			file=args.split()[0]
			if self.initialized:
				print("Loading file {}".format(file))
				self.cpu.load(file)
			else:
				print('CPU not Initialized')
	
	def do_exit(self,args):
		"""Exit"""
		exit(0)
		
	def do_EOF(self,args):
		exit(0)
	
	def do_rr(self,args):
		"""print values of Registers"""
		if self.initialized:
			if args in self.cpu.registers:
				print(self.cpu.registers[args])
			else:
				for r,v in self.cpu.registers.items():
					print(r,v)
		else:
			print('CPU not Initialized')
	
	def do_wr(self,args):
		"""write value to Registers"""
		value,reg='',''
		if len(args.split())==2:
			reg,value=args.split()
		if value.isnumeric and reg in self.cpu.registers:
			if self.initialized:
				try:
					self.cpu.registers[reg][0]=int(value)
				except Exception as e:
					print(e)
			else:
				print('CPU not Initialized')
	
	def do_dumpmem(self,args):
		"""Dump Memory"""
		m_base=0
		m_len=0
		if len(args.split())>=2:
			m_base=int(args.split()[0])
			m_len=int(args.split()[1])
		elif args:
			m_len=int(args.split()[0])
		else:
			print('missing Argument "length"')
		if self.initialized:
			self.cpu.memory.dump(m_base,m_len)
		else:
			print('CPU not Initialized')
	
	def do_go(self,args):
		"""Execute Assembled Code"""
		if self.initialized:
			while 1:
				if self.cpu.verbose:
					self.cpu.dumpregs()
					print("Flags:",self.cpu.flags)
					print("Memory:")
					self.cpu.memory.dump(length=8,width=32)
					print('-'*10)
				if not self.cpu():
					break
		else:
			print('CPU not Initialized')
	
	def do_bp(self,arg):
		if self.initialized:
			self.cpu.breakpoints.append(int(arg.split()[0]))
		else:
			print('CPU not Initialized')
Shell().cmdloop()
