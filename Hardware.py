import sys
class Console:
	port=0b101
	def __init__(self,):
		pass
	def output(self,cpu,n):
		print(chr(n),end='')
		sys.stdout.flush()