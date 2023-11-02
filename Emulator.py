"""Emulator.py -> Updated Control Unit or Schön Core Alpha Pro v.0.1.0 Python emulator

Works with binary words defined as a list of ints, example:
[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
Registers are defined as lists of words, and all types of registers are defined together in a list of registers,
but referencing them they're defined as [index,type]

Major functions:

initialize_rom() -> initializes Read Only Memory by reading file given at "rom/fn.txt" and writes the data to rom_data
reg(rw, index, reg_type, value=None, preset=None) -> Handles register read/write
rar(rw, index, reg_type, value=None) -> Handles register associated register

alu() -> executes arithmetic and logic operations based on flags set and registers

cls(r=0, g=0, b=0) -> clears registers and flags
execute(set_list, ena_list, gui=False, reg_a=[0,0], reg_b=[0,0], reg_c=[0,0]) -> Executes actions based on set/enable flags and registers
single_instruction(r=0, gui=False, print_line_nr=False, force_show_exceptions=False) -> Runs a single instruction
run(filename, gui=False, print_line_nr=False, force_show_exceptions=False,time_runtime=False) -> Function to call for running a schonexe5 file
"""

#Import libraries
import BaseCPUInfo				#Basic CPU information
import math
import BasicMath as bm				#Basic math library
import GateLevel as g
import importlib as il
import time
import logging as lgn			#Logging for custom exceptions
from enum import Enum

lgn.basicConfig(format="%(levelname)s: %(message)s", level=lgn.DEBUG)

lgn.debug("Imported libraries.")

#Basic CPU info variables
bw = BaseCPUInfo.bit_width

bf = BaseCPUInfo.base_folder
pf = BaseCPUInfo.programs_folder
exeff = BaseCPUInfo.executable_files_folder

file_extension_name = ".schonexe1"

#All types of memory storage units, including ram and registers
rom_data = []

bz = bm.dtb(0) #Binary zero

def initialize_rom(Filename: str):
	"""initialize_rom() -> initializes Read Only Memory by reading file given at "rom/fn.txt" and writes the data to rom_data
	"""
	rom_fh = open(bf + exeff + Filename + file_extension_name, "r")
	global rom_data 
	rom_data = rom_fh.readlines()
	rom_fh.close()
	
	for i, line in enumerate(rom_data):
		q = line.strip()
		rom_data[i] = [int(j) for j in q]

#RAM emulated through huge list
ramv = [
	bz for i in range(1024)	#Random Access Memory, emulated 1024, but is capable of 4.294.967.296
]

class ReadWrite(Enum):
	READ = 0
	WRITE = 1

class RegType(Enum):	#Register types enum
	GENERALPURPOSE = 0
	ALU = 1
	STACK = 2
	PROTECTED = 3

class ProtReg(Enum):	#Protected register enum
	PROGRAMCOUNTER = 0
	ENABLELIST = 1
	SETLIST = 2
	AOR = 3
	FLAGS = 4
	CONTROLUNITINPUT = 5
	ROMADDRESS = 6
	RAMADDRESS = 7
	REGINTERMEDIATE = 8

class ALUConfig(Enum):
	PROGRAMCOUNTERINCREMENT = 0
	ALUFUNCTION = 1
	ENABLEAOR = 2
	SETAOR = 3
	INCREMENT = 3
	DECREMENT = 4
	SPECIALFUNCTION = 6
	SETFLAGS = 7

class EmulatorRuntimeError(Enum):
	ALUFAILED = "ALU: Unknown error."
	ALUNOTINITIATED = "ALU: Couldn't initiate."
	ILLEGALFUNCTION = "Offset: Illegal function called."

#Internal registers emulated as list of lists
regs = [
	[bz for i in range(32)],	#General Purpose Registers
	[bz for i in range(32)],	#Arithmetic/Logic Unit Registers
	[bz for i in range(32)],	#Stack Pointers
	[bz for i in range( 8)],	#Special Purpose Internal CU Register
]

reg_offs = [bz for i in range(2)]

buffer = bz

#Functions to manage buffer, registers and other memory storage units
def buf(rw, list=bz):
	global buffer 
	if rw == 0:
		return buffer 
	
	buffer = list

def rom(rw, index, list = [] ):
	global rom_data
	if rw == 1:
		return 
	
	global rom_data
	
	return rom_data[index]

def ram(rw, index, value=None, preset=None):
	"""ram(rw, index, value=None, preset=None) -> Handles Random Access Memory read/write
	Parameters:
	
	rw: if True write else read
	index: index of register
	value: value to write to register
	preset: if True it overrides value to write to register
	
	Returns: binary word
	"""
	global ramv
	
	if isinstance(rw, ReadWrite)
		rw = rw.value
	
	if rw == 0:
		return ramv[index]
	if isinstance(preset,type(None)) == False:
		ramv[index] = preset
		return 
	ramv[index] = value
	return

def reg(rw, index, reg_type, value=None, preset=None):
	"""reg(rw, index, reg_type, value=None, preset=None) -> Handles register read/write
	Parameters:
	
	rw: if True write else read
	index: index of register
	reg_type: type of register
	value: value to write to register
	preset: if True it overrides value to write to register
	
	Returns: binary word
	"""
	global regs
	if isinstance(rw, ReadWrite):		#Read write enum
		rw = rw.value
	if isinstance(reg_type, RegType):	#Register type enum
		reg_type = reg_type.value
	if isinstance(index, ProtReg):		#Protected register enum
		index = index.value
	if rw == 0:
		return regs[reg_type][index]
	if not isinstance(preset,type(None)):
		regs[reg_type][index] = preset
		return 
	regs[reg_type][index] = value
	return

#Further basic CPU info variables
ena_list = reg(0, ProtReg.ENABLELIST, RegType.PROTECTED, bz)
set_list = reg(0, ProtReg.SETLIST, RegType.PROTECTED, bz)

#----------------------------------------------------------
#Update ALU test for improved testing
#Test ALU
# try:
	
	# lgn.debug("ALU tested.")
# except Exception:
	# lgn.critical(EmulatorRuntimeError.ALUNOTINITIATED.value)
	# return -1

#Setup ALU
################################################
#Need update!
################################################
def alu():		#//Update for new ALU
	"""alu() -> executes arithmetic and logic operations based on flags set and registers
	Returns: return code: 1 for function completed succesfully or passes any errors
	"""
	global reg
	spec_func_var = reg(ReadWrite.READ, ProtReg.ALUSPECIALFUNCTION, RegType.PROTECTED)
	ena_list = reg(ReadWrite.READ, ProtReg.ENABLELIST, RegType.PROTECTED)
	set_list = reg(ReadWrite.READ, ProtReg.SETLIST, RegType.PROTECTED)
	ln = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	num_a = buf(0)
	
	if ena_list[ALUConfig.PROGRAMCOUNTERINCREMENT] == 0:
		num_b = reg(0, 0, 1)
	else:
		num_b = bm.dtb(1)
	
	func = reg(ReadWrite.READ, ALUConfig.ALUFUNCTION, RegType.ALU)
	tmp = [0 for i in range(4)]
	for i in range(4):
		tmp[i] = func[i]
	func = bm.blts(tmp)
	tmp_a = bm.btd(num_a)
	tmp_b = bm.btd(num_b)
	co = 0
	if tmp_a > tmp_b:
		comp = [1,0,0]
	elif tmp_a == tmp_b:
		comp = [0,1,0]
	else:
		comp = [0,0,1]
	q = []
	if func == "0000":		#Addition
		q, co = g.la(num_a, num_b)
	elif func == "1000":	#Subraction
		q, co = g.ls(num_a, num_b)
	elif func == "0100":	#Multiplication
		q = g.mul(num_a, num_b)
	elif func == "1100":	#Divivision
		q = g.div(num_a, num_b)
	elif func == "0010":	#Logical and
		q = g.al(num_a, num_b)
	elif func == "1010":	#Logical or
		q = g.ol(num_a, num_b)
	elif func == "0110":	#Logical exclusive or
		q = g.xl(num_a, num_b)
	elif func == "1110":	#Logical not
		q = g.nl(num_a)
	elif func == "0001":	#Logical shift
		if bm.btd(spec_func_var) == 1:
			q, co = shift(num_b, bm.btd(num_a), 0)
		else:
			q, co = shift(num_b, bm.btd(num_a))
	elif func == "1111":	#Compare
		q = num_b
	else:					#Error
		lgn.critical("ALU: Invalid function call at line %s" % (bm.btd(ln)+1))
		raise Exception
	
	comp.append(co)
	reg(ReadWrite.WRITE, ProtReg.AOR, RegType.PROTECTED, q)
	if set_list[ALUConfig.SETFLAGS] == 1:
		reg(ReadWrite.WRITE, ProtReg.FLAGS, RegType.PROTECTED, comp)
	lgn.debug("ALU succesfully run.")
	return 1

#Setup Processor


FunctionDefinitionMetaInfo = [

	"FETCH",	#Special non-user accessible
	"ROM",		#Starting for indexing
	"RAM",
	"REG",
	"STACK",
	"CONDITIONALBRANCH",
	"INTERRUPT",
	"CALLRETURNFUNCTION",

]

alu_descr_meta = [

	"ADD",
	"SUB",
	"MUL"
	"DIV",
	"AND",
	"OR",
	"XOR",
	"NOT",
	"SFT",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"CMP",

]

alu_descr = [
	[
		[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		[0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0]
	],
	[
		[0,0,0,0,0,0,0,1,0,0,0,0],
		[0,0,0,0,0,0,1,0,0,0,0,0],
		[0,1,0,0,0,0,0,0,0,0,0,0]
	]
]

next_address = [
	[
		[0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	],
	[
		[1,0,1,0,0,0,0,0,0,0,0,0],
		[0,1,0,0,0,0,0,0,0,0,0,0]
	]
]

set_address = [
	[
		[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	],
	[
		[0,0,0,0,1,0,0,0,0,0,0,0]
	]
]

#Clear Registers
def cls(r=0, g=0, b=0):
	if b == 1:
		buf(1, bz)
	if r == 1:
		ramv = [
			bz for i in range(1024)
		]
	if g == 1:
		for i, _ in enumerate(regs):
			for j, _ in enumerate(regs[i]):
				regs[i][j] = bz
		clear_reg_offs()

def clear_reg_offs():
	global reg_offs
	reg_offs = [[0 for i in range(32)] for i in range(2)]

def pr(lst, gui=False):#Print function
	if gui == True:
		print(str(bm.blts(lst, False, True)))
	elif gui == "not":
		print(str(bm.btd(lst)))
	elif gui == "bin":
		print(bm.btbs(lst))
	else:
		print("Output: " + str(bm.btd(lst)))

#Defining the functions pin outputs
FunctionDefinitions = [
	
	[		#Set pins
		[	#Fetch-------------------
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
		],
		[	#ROM Immediate-----------
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#ROM At Address At Immediate
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Immediate READ
			[1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate READ
			[1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Immediate WRITE
			[1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate WRITE
			[1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#REG Swap----------------
			[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#REG Clone
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#STACK PUSH--------------
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK POP
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK POINT TO AT REGISTER
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK GET POINTER
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#CONDITIONAL-------------
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#INTERRUPT
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#CALL FUNCTION-----------
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#PC
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#RegA
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#Initiate branch
			[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Branch to @ next word
		],
		[	#RETURN FUNCTION
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Pop from stack
			[0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#PC
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#RegA
		],
		[	#GPIO--------------------
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#
		],
	],
	
	[		#Enable pins
		[	#Fetch
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
		],
		[	#ROM Immediate
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
		],
		[	#ROM At Address At Immediate
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[1,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Immediate READ
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate READ
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Immediate WRITE
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate WRITE
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#REG Swap
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
			[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
		],
		[	#REG Clone
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#STACK PUSH
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#STACK POP
			[0,0,0,0,1,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#STACK POINT TO AT REGISTER
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#STACK GET POINTER
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#CONDITIONAL
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
		],
		[	#INTERRUPT
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#CALL FUNCTION
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],	#Push to stack
			[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#PC
			[0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],	#RegA
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Initiate branch
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],	#Branch to @ next word
		],
		[	#RETURN FUNCTION
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],	#Pop from stack
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],	#PC
			[0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],	#RegA
		],
		[	#GPIO
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],	#
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],	#
			[0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],	#
		],
	],
]

#Set Set Pins
#pci, pc, cb, aor, rama, ramd, roma, gpioa, gpiod, flg, pid, reg_a, reg_b, reg_c, cui, sp, ism, if
def set(list):		
	reg(ReadWrite.WRITE, ProtReg.SETLIST, RegType.PROTECTED, list)

#Set Enable Pins
#pci, pc, aor, inc, decrement, ramd, romd, pid, gpi, reg_a, reg_b, reg_c, sp, ism, if
def enable(list):		
	reg(ReadWrite.WRITE, ProtReg.ENABLELIST, RegType.PROTECTED, list)

def sr(lst, comp, var_a=[0]):	#Should Run?
	for i, e in enumerate(lst):
		if g.a(comp[i], lst[i]) == 1:
			return g.x(0,var_a[0])
	return g.x(1,var_a[0])

def ofs(func, var_a, var_b, var_c, var_d):	#Offset
	
	try:
		#ftch, rom, ram, reg, stck, conbrnch, intrpt, callretrn
		#-----------------------------------------------------------------
		#Update for new function definitions
		ofs_array		= [0, 2,11,23,28,32]
		ofs_use_var_a	= [0, 0, 1, 1, 1, 1]
		ofs_use_var_b	= [1, 1, 0, 0, 1, 0]
		ofs_use_var_c	= [0, 0, 0, 0, 0, 0]
		ofs_use_var_d	= [0, 1, 1, 1, 0, 0]
		
		ofs_two_parts	= [3, 6, 9,12,15,18,21]
		
		tl = []
		if ofs_use_var_d[func]:
			tl = bm.bla(tl, var_d)
		if ofs_use_var_c[func]:
			tl = bm.bla(tl, var_c)
		if ofs_use_var_b[func]:
			tl = bm.bla(tl, var_b)
		if ofs_use_var_a[func]:
			tl = bm.bla(tl, var_a)
		
		#Debbing info for offset
		lgn.debug("Function: %s, offset: %s" % (t_func_descr_meta[func], bm.blts(tl)))
		dtl = bm.btd(tl)
		
		i = ofs_array[func]
		while i < ofs_array[func] + dtl:
			if i in ofs_two_parts:
				dtl += 1
			i += 1
		
		return ofs_array[func] + dtl
		
	except Exception:
		lgn.critical("OFS: Invalid parameters for offset, func:{function}, var_a:{vara}, var_b:{varb}, var_c:{vard}".format(function = func, vara = var_a, varb = var_b, vard = var_d))
		return EmulatorRuntimeError.ILLEGALFUNCTION

def sa(bool):				#Set Address
	if not bool:
		return 
		
	iint = 0
	for i, _ in enumerate(set_address):
		execute(set_address[0][i], set_address[1][i], bm.btd(reg_a))

def dump_rom():
	global rom_data
	print("\nDUMP ROM:")
	for i, line in enumerate(rom_data):
		print("%s: %s" % (i, bm.blts(line)))
	print("\n")

#Define actions dictated by set/enable pins
def execute(set_list, ena_list, gui=False, 
			reg_a=[0,0], reg_b=[0,0], reg_c=[0,0],
			var_e=None):
	"""execute(set_list, ena_list, gui=False, reg_a=[0,0], reg_b=[0,0], reg_c=[0,0]) -> Executes actions based on set/enable flags and registers
	Parameters:
	
	set_list: List of flags to set
	ena_list: List of flags to enable
	gui: True: output as little endian binary digits, 
		 "not": Converts to int then prints output
		 "bin": outputs as big endian binary digits 
		 else: converts to int then prints("Output: " + int)
	reg_a/reg_b/reg_c: registers indentified by [index, type]
	"""
	global reg_offs
	global buf
	set(set_list)
	enable(ena_list)
	var = bz
	
	#Enable actions:
	if ena_list[0]:		#Increment program counter
		
	if ena_list[1]:		#pc
		var = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	if ena_list[1]:		#aor 
		var = reg(ReadWrite.READ, ALUConfig.ENABLEAOR, RegType.ALU)
	if ena_list[5]:		#ramd 
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		var = ram(ReadWrite.READ, bm.btd(tmp), "RAMD ENABLE EXECUTE()")
	if ena_list[6]:		#romd 
		tmp = reg(ReadWrite.READ, ProtReg.ROMADDRESS, RegType.PROTECTED)
		var = rom(0, bm.btd(tmp))
	if ena_list[7]:		#Register intermediate data
		var = reg(ReadWrite.READ, ProtReg.REGINTERMEDIATE, RegType.PROTECTED)
	if ena_list[5]:		#gpi 
		var = bm.dtb(int(input("Number: ")))
	if ena_list[6]:		#rega 
		var = reg(ReadWrite.READ, reg_a[0]+reg_offs[0][reg_a[0]], reg_a[1])
	if ena_list[7]:		#regb 
		var = reg(ReadWrite.READ, reg_b[0]+reg_offs[1][reg_b[0]], reg_b[1])
	if ena_list[8]:		#regc
		var = reg(ReadWrite.READ, reg_c[0], reg_c[1])
	if ena_list[9]:		#rara
		var = rar(ReadWrite.READ, reg_b[0]+reg_offs[1][reg_b[0]], reg_b[1])
	if ena_list[10]:	#ena_temp_reg
		var = reg(ReadWrite.READ, reg_a[0]+reg_offs[0][reg_a[0]], 4)
	if ena_list[11]:	#stack pop/push
		var = stack(0, reg_a[0], reg_a[1], reg_c[0])
	
	buf(1,var)
	# print("\nBUFFER:%s\n" % (bm.blts(var)))
	
	#Set actions:
	if set_list[0] == 1:	#pc
		reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, var)
	if set_list[1] == 1:	#aor
		alu_r = alu()
		if alu_r != 1:
			lgn.warning(EmulatorRuntimeError.ALUFAILED.value)
			raise Exception
	if set_list[2] == 1:	#rama
		reg(ReadWrite.WRITE, ProtReg.RAMADDRESS, RegType.PROTECTED, var)
	if set_list[3] == 1:	#ramd
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		ram(ReadWrite.WRITE, bm.btd(tmp), var)
	if set_list[4] == 1:	#roma
		reg(ReadWrite.WRITE, ProtReg.ROMADDRESS, RegType.PROTECTED, var)
	if set_list[5] == 1:	#gpoa
		pr(var, gui)
	if set_list[6] == 1:	#gpod
		print("")
		print("OUTPUT: " + str(bm.btd(var)))
	if set_list[7] == 1:	#flg
		pass
	if set_list[8] == 1:	#airb
		reg(ReadWrite.WRITE, 0, 1, var)
	if set_list[9] == 1:	#rega
		reg(ReadWrite.WRITE, reg_a[0]+reg_offs[0][reg_a[0]], reg_a[1], var)
	if set_list[10] == 1:	#regb
		reg(ReadWrite.WRITE, reg_b[0]+reg_offs[1][reg_b[0]], reg_b[1], var)
	if set_list[11] == 1:	#regc
		reg(ReadWrite.WRITE, reg_c[0], reg_c[1], var)
	if set_list[12] == 1:	#cui
		reg(ReadWrite.WRITE, 5, 4, var)
	if set_list[13] == 1:	#rarb
		rar(ReadWrite.WRITE, reg_b[0], reg_b[1], var)
	if set_list[14] == 1:	#incr_rega
		reg_offs[0][reg_a[0]] += 1
	if set_list[15] == 1:	#incr_regb
		reg_offs[1][0] += 1
	if set_list[16] == 1:	#set_temp_reg
		reg(ReadWrite.WRITE, 7, 4, buf)
	if set_list[17] == 1:	#stack pop/push
		stack(1, reg_a[0], reg_a[1], var_e)

#Run Single Instruction
def single_instruction(reset=0, gui=False, 
					   print_line_nr=False, 
					   force_show_exceptions=False):
	"""single_instruction(r=0,gui=False, print_line_nr=False, force_show_exceptions=False) -> Runs a single instruction
	Parameters:
	
	r: Reset registers and flags
	gui: True: output as little endian binary digits, 
		 "not": Converts to int then prints output
		 "bin": outputs as big endian binary digits 
		 else: converts to int then prints("Output: " + int)
	print_line_nr: if True prints binary line numbers to terminal
	force_show_exceptions: Quirks in how it handles variables might create exceptions which can be shown for debugging reasons
	
	Returns: error code: -1 for error, 0 for instruction completed but continue and 1 for completed and exit
	"""
	global reg
	
	#Handle reset
	if reset == 1:	#Reset
		cls(1,1,1)
		if force_show_exceptions:
			lgn.debug("Cleared registers")
		return 0
	
	#Get program counter, mainly for debugging
	ln = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	
	# reg(ReadWrite.WRITE, ALUConfig., RegType.ALU, bz)
	
	#fetch next instruction 
	for i, _ in enumerate(FunctionDefinitions[0]):
		execute(FunctionDefinitions[0][0][i], FunctionDefinitions[1][0][i])
	clear_reg_offs()
	inp = reg(ReadWrite.READ, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED)
	
	if print_line_nr:
		lgn.debug("Program Counter: %s, %s" % (bm.btd(ln), bm.blts(inp)))
	
	#if input is all 1s, exit with return code 1
	exit_signal = True
	for i in inp:
		if i == 0:
			exit_signal = False
			break
	if exit_signal:
		if force_show_exceptions:
			lgn.debug("EXIT_SIGNAL.")
		return 1
		
	comp = reg(ReadWrite.READ, ProtReg.AOR, RegType.PROTECTED)
	
	#get input variables
	#Where the different variables start in input space
	var_ofs = [0, 5, 6, 7, 7, 9, 11, 18, 25]
	
	#Length of variables 
	var_lengs = [4,1,1,4,2,2,7,7,7]
	
	#Unpack instruction to variables
	instruction_vars = [
		[[inp[i + var_ofs[j]]] for i in range(var_lengs[j])] for _, j in enumerate(var_lengs)
	]
	
	
	
	# if inp[4] == 0:
		# print(bm.blts(inp))
		# print("ln: %s: %s\n" % (bm.btd(ln), t_func_descr_meta[bm.btd(func)]))
	
	#logic 
	if inp[4] == 1:		#if the function is an alu operation
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, func)
		reg(ReadWrite.WRITE, ProtReg.ALUSPECIALFUNCTION, RegType.PROTECTED, var_a)
		for i, _ in enumerate(alu_descr[0]):
			execute(alu_descr[0][i], 
					alu_descr[1][i], 
					gui, reg_a, reg_b, reg_c)
		clear_reg_offs()
		if force_show_exceptions:
			lgn.debug("ALU function done.")
		return 0
	
	#else if the function is a logical operation
	if func_def[bm.btd(func)] != 1:
		#try:	
		_ofs = ofs(bm.btd(func), vab, vbb, vcb, vdb)
		if _ofs == EmulatorRuntimeError.ILLEGALFUNCTION:
			return -1
		
		for i, _ in enumerate(t_func_descr[0][_ofs]):
			execute(t_func_descr[0][_ofs][i], 
					t_func_descr[1][_ofs][i], 
					gui, reg_a, reg_b, reg_c, var_e)
		clear_reg_offs()
		return 0
	
	#else if the function is an irar statement
	if var_b[0] == 1:
		for i, _ in enumerate(t_func_descr[0][1]):
			execute(t_func_descr[0][1][i], 
					t_func_descr[1][1][i], 
					gui, reg_a, reg_b)
		clear_reg_offs()
		
		for i, _ in enumerate(set_irar_address[0]):
			execute(set_irar_address[0][i], 
					set_irar_address[1][i], 
					gui, reg_a)
		clear_reg_offs()
		
		return 0
	
	#Else if the function is as if statement
	for i, _ in enumerate(t_func_descr[0][0]):
		execute(t_func_descr[0][0][i], 
				t_func_descr[1][0][i], 
				gui, reg_a, reg_b)
	clear_reg_offs()
	comp = reg(ReadWrite.READ, ProtReg.FLAGS, RegType.ALU)
	
	
	if sr(var_c, comp) or var_a[0]:
		for i, _ in enumerate(set_address[0]):
			execute(set_address[0][i], 
					set_address[1][i], 
					gui, reg_a)
		clear_reg_offs()
		return 0
	
	return 0

def run(filename, gui=False, print_line_nr=False, 
		force_show_exceptions=False,time_runtime=False):
	"""run(filename, gui=False, print_line_nr=False, force_show_exceptions=False,time_runtime=False) -> Runs executable program from filename
	Parameters:
	
	filename: name of the file to be run
	gui: True: output as little endian binary digits, 
		 "not": Converts to int then prints output
		 "bin": outputs as big endian binary digits 
		 else: converts to int then prints("Output: " + int)
	
	print_line_nr: if True prints binary line numbers to terminal
	force_show_exceptions: Quirks in how it handles variables might create exceptions which can be shown for debugging reasons
	time_runtime: if True prints runtime length based on time.time()
	
	Returns: error code: -1 for error, 0 for instruction completed but continue and 1 for completed and exit
	"""
	
	#Open and read file for execution 
	file_path = bf + exeff + filename + file_extension_name
	try:
		with open(file_path, "r") as temp_fh:	
			lines = temp_fh.readlines()
			temp_fh.close()
	except FileNotFoundError:
		lgn.critical("%s.run(): Couldn't open file %s." % (__file__, file_path))
		return -1
	
	#Setup cpu sattelite files for executions 
	reg(ReadWrite.WRITE, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED, bz)
	single_instruction(reset=1)
	initialize_rom(filename)
	if time_runtime:
		start_time = time.time()
	
	#Execute program 
	while True:
		q = single_instruction(0, gui, print_line_nr, force_show_exceptions)
		if isinstance(q, int):
			if q == 1:
				if time_runtime:
					end_time = time.time()
					print("elapsed time: %s" % (end_time-start_time))
					return [1, end_time-start_time]
				return 1
			elif q == -1:
				lgn.critical("Error: %s.run(): return code -1, runtime stopped" % (__file__))
				raise Exception
			elif q != 0:
				lgn.warning(q)
				print(q)