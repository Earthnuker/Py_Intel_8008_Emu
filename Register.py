class Register(object):
	def __init__(self,name,bits,binv=''):
		self.name=name
		self.value=0
		self.bits=bits
		self.maxv=(1<<bits)-1
		if binv!='':
			self.n=binv
			binv='{:03b}'.format(binv)
		self.binv=binv
	
	def __repr__(self):
		return 'Register {} ({}): {} Bits, Current Value: [U:{},S:{}]'.format(self.name,self.binv,self.bits,self[0],self[1])
	
	def __getitem__(self,signed):
		if signed not in [0,1]:
			raise IndexError("Index needs to be 0 (unsigned) or 1 (signed)")
		self.value=self.value&self.maxv
		if signed:
			rv = self.value - (int(bool(self.value&(1<<(self.bits-1))))<<self.bits) #simulate overflow
		else:
			rv = self.value
		return rv
	
	def __setitem__(self,signed,val):
		if signed not in [0,1]:
			raise IndexError("Index needs to be 0 (unsigned) or 1 (signed)")
		val=val&self.maxv
		sign=0
		if signed:
			sign=int(val<0)
			val=(sign<<self.bits-1)+abs(abs(val) - ( sign<<self.bits -1 ))
		self.value=val
	
	def __op__(self,op,other=None):
		if other:
			if isinstance(other,type(self)):
				rv=__import__("operator").__dict__[op](self.value,other.value)
			elif isinstance(other,int):
				rv=__import__("operator").__dict__[op](self.value,other)
			else:
				raise NotImplementedError
		else:
			rv=__import__("operator").__dict__[op](self.value)
		if isinstance(rv,bool):
			return rv
		ret=type(self)(self.name,self.bits)
		ret.value=rv&self.maxv
		return ret
	
	def get(self):
		return self.__getitem__(0)
	
	def set(self,value):
		self.__setitem__(0,value)
	
	def __add__(self,other):return self.__op__('add',other)
	def __sub__(self,other):return self.__op__('sub',other)
	def __mul__(self,other):return self.__op__('mul',other)
	def __and__(self,other):return self.__op__('and_',other)
	def __or__(self,other):return self.__op__('or_',other)
	def __xor__(self,other):return self.__op__('xor',other)
	def __rshift__(self,other):return self.__op__('rshift',other)
	def __lshift__(self,other):return self.__op__('lshift',other)
	def __invert__(self):return self.__op__('invert')
	
