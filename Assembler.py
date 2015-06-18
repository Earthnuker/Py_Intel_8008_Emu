import sys,os
from CPU import *
cpu=CPU()
def assemble(code,fill=True):
	org=None
	jmpdict={}
	for ln,omn in enumerate(code.split('\n'),1):
		mn=omn[:].strip()
		if mn.startswith('org 0x'):
			org=int(mn.split(' ')[1],16)
			continue
		elif mn.startswith('org '):
			org=int(mn.split(' ')[1])
			continue
		elif org==None:
			org=cpu.stackwidth
		if org:
			caddr=org+2
			org=False
		if mn.startswith(':_'):
			mn=mn[1:]
			if mn not in jmpdict:
				jmpdict[mn]=caddr
				continue
			else:
				raise RuntimeError('Duplicate label: {} (line {})'.format(mn,ln))
		mn=mn.split(';',1)[0].split(' ')[0]
		if mn:
			caddr+=cpu.opcode_names[mn].size
	print('Labels:')
	for n,a in jmpdict.items():
		print('{} -> 0x{:04X}'.format(n,a))
	print('Opcodes')
	out=b''
	del caddr
	org=None
	for ln,omn in enumerate(code.split('\n'),1):
		mn=omn[:].strip()
		if ';' in mn:
			mn=mn.split(';',1)[0]
		if mn.startswith(':_'):
			continue
		if not mn:
			continue
		if mn.startswith('org 0x'):
			org=int(mn.split(' ')[1],16)
			continue
		elif mn.startswith('org '):
			org=int(mn.split(' ')[1])
			continue
		elif org==None:
			org=cpu.stackwidth
		if org:
			out=int.to_bytes(org+1,2,'little')+b'\x00'*(org)+out
			caddr=org+2
			org=False
		print(mn,'->',end=" ")
		dst=None
		src=None
		args=''
		if ' ' in mn:
			mn,args=mn.split(' ')
		if ',' in args:
			dst,src=args.split(',')
		else:
			dst=args
			src=args
		try:
			opc=cpu.opcode_names[mn]
		except KeyError:
			raise RuntimeError('Invalid Instruction "{}" (line {})'.format(mn,ln))
		opcb=opc.opcodes[0]
		
		if src in cpu.registers:
			src=cpu.registers[src].binv
			if 'sss' in opcb and len(src)==3:
				opcb=opcb.replace('sss',src)
		elif src:
			if src.startswith('0x'):
				src=int(src,16)
			elif src.startswith('0b'):
				src=int(src,2)
			elif src.isnumeric():
				src=int(src)
			elif src in jmpdict:
				src=jmpdict[src]
			elif src[0]=="'" and src[-1]=="'":
				src=ord(src[1:-1])
		
		if dst in cpu.registers:
			dst=cpu.registers[dst].binv
			if 'ddd' in opcb and len(dst)==3:
				opcb=opcb.replace('ddd',dst)
		elif dst:
			if dst.startswith('0x'):
				dst=int(dst,16)
			elif dst.startswith('0b'):
				dst=int(dst,2)
			elif dst.isnumeric():
				dst=int(dst)
			elif dst in jmpdict:
				dst=jmpdict[dst]
			elif dst[0]=="'" and dst[-1]=="'":
				dst=ord(dst)
		
		if 'x' in opcb:
			opcb=opcb.replace('x','0')
		if 'a' in opcb:
			opcb=opcb.replace('a'*opcb.count('a'),('{:0'+str(opcb.count('a'))+'b}').format(dst))
		
		print(' '.join(map(str,filter(bool,(opcb,dst,src)))),end=" => ")
		
		opcb=bytes([int(opcb,2)])
		if opc.size>1:
			if isinstance(dst,int):
				dst=int.to_bytes(dst,opc.size-1,'little')
				opcb+=dst
			elif isinstance(src,int):
				src=int.to_bytes(src,opc.size-1,'little')
				opcb+=src
		print('[{:04X}]'.format(caddr),' '.join(map(lambda x:'{:02X}'.format(x),opcb)))
		if len(opcb)!=opc.size:
			if len(opcb)<opc.size:
				error='Missing Operand'
				raise RuntimeError('Error while Assembling instruction "{}": {} (line {})'.format(omn,error,ln))
			raise RuntimeError('Error while Assembling instruction "{}" (line {})'.format(omn,ln))
		out+=opcb
		caddr+=len(opcb)
	if fill:
		out=out.ljust(cpu.memsize,b'\x00')
	if len(out)>cpu.memsize:
		raise RuntimeError('Assembled code is too large to fit into RAM')
	org=int.from_bytes(out[:2],'little')
	print('ORG:',org)
	return out
def asmsh(fill=False):
	inp=[]
	while 1:
		if fill:
			r=input('asm_img>')
		else:
			r=input('asm>')
		if r and r!='w':
			inp.append(r)
		else:
			code=assemble('\n'.join(inp),fill=fill)
			return code
def asm_file(file,fill=True):
	try:
		with open(file,'r') as infile:
			return assemble(infile.read(),fill=fill)
	except Exception as e:
		print(e)
		return b''
if __name__=='__main__':
	with open(sys.argv[1]+'.bin','wb') as of:
		of.write(asm_file(sys.argv[1]))