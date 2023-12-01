"""Emulator.py -> Updated Control Unit or Schön Core Alpha Pro v.0.1.0 Python emulator

Works with binary words defined as a list of ints, example:
[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
Registers are defined as lists of words, and all types of registers are defined together in a list of registers,
but referencing them they're defined as [index,type]

Major functions:

initialize_rom() -> initializes Read Only Memory by reading file and writes the data to rom_data
reg(rw, index, reg_type, value=None, preset=None) -> Handles register read/write

alu() -> executes arithmetic and logic operations based on flags set and registers

cls(r=0, g=0, b=0) -> clears registers and flags
execute(set_list, ena_list, gui=False, reg_a=[0,0], reg_b=[0,0], reg_c=[0,0]) -> Executes actions based on set/enable flags and registers
single_instruction(r=0, gui=False, print_line_nr=False, force_show_exceptions=False) -> Runs a single instruction
run(filename, gui=False, print_line_nr=False, force_show_exceptions=False,time_runtime=False) -> Function to call for running a schonexe5 file
"""

#Import libraries
import BaseCPUInfo				#Basic CPU information
import math
import BasicMath as bm			#Basic math library
import GateLevel as g			#Gatelevel functions for binary operations
import importlib as il
import time
import logging as lgn			#Logging for custom exceptions
from enum import Enum			#Enum for elimination of magic numbers

#Initiating logging
LOGLEVEL = lgn.WARNING
lgn.basicConfig(format="%(levelname)s: %(message)s", level=lgn.DEBUG)
lgn.getLogger().setLevel(LOGLEVEL)

#Basic CPU info variables
bw = BaseCPUInfo.bit_width
bf = BaseCPUInfo.base_folder
pf = BaseCPUInfo.programs_folder
exeff = BaseCPUInfo.executable_files_folder

#File extention name for the format
file_extension_name = ".schonexe1"

#Initiating runtime variables
rom_data = []
bz = bm.dtb(0) #Binary zero

def initialize_rom(Filename: str):
	"""initialize_rom() -> initializes Read Only Memory by reading file given at "rom/fn.txt" and writes the data to rom_data
	"""
	rom_fh = open(bf + exeff + Filename + file_extension_name, "r")
	global rom_data 
	rom_data = []
	rom_data_temp = rom_fh.readlines()
	rom_fh.close()
	
	for i, line in enumerate(rom_data_temp):
		temp = []
		for j, e in enumerate(line):
			if e == "1":
				temp.append(1)
			elif e == "\n":
				pass
			else:
				temp.append(0)
		rom_data.append(temp)
	return 1

#RAM emulated through huge list
ramv = [
	bz for i in range(1024)	#Random Access Memory, emulated 1024, but is capable of 4.294.967.296
]

#Classes for enums for elimination of magic numbers
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
	STACKPOINTER = 9

class ALUConfig(Enum):
	PROGRAMCOUNTERINCREMENT = 0
	ALUFUNCTION = 1
	ENABLEAOR = 2
	SETAOR = 3
	INCREMENT = 3
	DECREMENT = 4
	SPECIALFUNCTION = 6
	SETFLAGS = 10
	BREGISTER = 8

class RuntimeVariables(Enum):
	FUNCTIONVARIABLE = 0
	LOGICALALU = 1
	VARIABLEA = 2
	VARIABLEB = 3
	REGISTERA = 4
	REGISTERB = 5
	REGISTERC = 6

class EmulatorRuntimeError(Enum):
	ALUFAILED = "ALU: Unknown error."
	ALUNOTINITIATED = "ALU: Couldn't initiate."
	ILLEGALFUNCTION = "Offset: Illegal function called."

#Internal registers emulated as list of lists
regs = [
	[bz for i in range(32)],	#General Purpose Registers
	[bz for i in range(32)],	#Arithmetic/Logic Unit Registers
	[bz for i in range(32)],	#Stack Pointers
	[bz for i in range(10)],	#Special Purpose Internal CU Register
]

#Functions to manage buffer, registers and other memory storage units
def buf(rw, list=bz):
	global buffer 
	if rw == 0:
		return buffer 
	
	buffer = list

def rom(rw, index):
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
	
	if isinstance(rw, ReadWrite):
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
	if isinstance(reg_type, ALUConfig):
		reg_type = reg_type.value
	if isinstance(index, ProtReg):		#Protected register enum
		index = index.value
	if isinstance(index, ALUConfig):
		index = index.value
	
	if rw == 0:
		# lgn.debug("Reg: READ: %s:%s, %s" % (reg_type, index, bm.blts(regs[reg_type][index])))
		return regs[reg_type][index]
	if not isinstance(value[0], int):
		lgn.critical("Register: Invalid type of register assignement.")
		raise Exception
	# lgn.debug("Reg: WRITE: %s:%s, %s" % (reg_type, index, bm.blts(value)))
	regs[reg_type][index] = value

#Further basic CPU info variables
ena_list = reg(0, ProtReg.ENABLELIST, RegType.PROTECTED, bz)
set_list = reg(0, ProtReg.SETLIST, RegType.PROTECTED, bz)
buffer = bm.dtb(0)

#Setup ALU
################################################
#Need update!
################################################
def alu():		#//Update for new ALU
	"""alu() -> executes arithmetic and logic operations based on flags set and registers
	Returns: return code: 1 for function completed succesfully or passes any errors
	"""
	
	global reg
	spec_func_var = reg(ReadWrite.READ, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED)
	ena_list = reg(ReadWrite.READ, ProtReg.ENABLELIST, RegType.PROTECTED)
	set_list = reg(ReadWrite.READ, ProtReg.SETLIST, RegType.PROTECTED)
	spec_func = reg(ReadWrite.READ, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED)
	ln = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	num_a = buf(0)
	lgn.debug("ALU: ALU A Register: %s" % (bm.user_btd(num_a)))
	
	if ena_list[ALUConfig.PROGRAMCOUNTERINCREMENT.value] or ena_list[ALUConfig.INCREMENT.value] or ena_list[ALUConfig.DECREMENT.value]:
		num_b = bm.dtb(1)
	else:
		num_b = reg(ReadWrite.READ, ALUConfig.BREGISTER, RegType.ALU)
	
	func = reg(ReadWrite.READ, ALUConfig.ALUFUNCTION, RegType.ALU)
	tmp = [0 for i in range(4)]
	for i in range(4):
		if func[i] == 1:
			tmp[i] = 1
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
	if spec_func[0] == 1:
		lgn.debug("ALU: FLOAT.")
		if func == "0000":
			q, co = g.ula(num_a, num_b)
		elif func == "1000":	#Subraction
			q, co = g.uls(num_a, num_b)
		elif func == "0100":	#Multiplication
			q = g.umul(num_a, num_b)
		elif func == "1100":	#Divivision
			try:
				q = g.udiv(num_a, num_b)
			except ZeroDivisionError:
				lgn.critical("ALU: Error: Can't divide by zero at line %s. (%s/%s)" % (bm.btd(ln), bm.user_btd(num_a), bm.user_btd(num_b)))
				raise ZeroDivisionError
			except Exception:
				lgn.critical("ALU: Error: Unknown error.")
				raise Exception
		else:					#Error
			lgn.critical("ALU: Invalid function call at line %s" % (bm.btd(ln)))
			lgn.info("ALU: Function: %s" % (bm.blts(func)))
			raise Exception
	else:
		if func == "0000" and ena_list[ALUConfig.DECREMENT.value] == 0 or ena_list[ALUConfig.INCREMENT.value]:	#Addition
			q, co = g.la(num_a, num_b)
		elif func == "1000" or ena_list[ALUConfig.DECREMENT.value]:	#Subraction
			q, co = g.ls(num_a, num_b)
		elif func == "0100":	#Multiplication
			q = g.mul(num_a, num_b)
		elif func == "1100":	#Divivision
			try:
				q = g.div(num_a, num_b)
			except ZeroDivisionError:
				lgn.critical("ALU: Error: Can't divide by zero.")
				lgn.info("Zero division at line %s." % (bm.btd(ln)))
				raise ZeroDivisionError
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
			lgn.info("ALU: CMP")
			q = num_b
			lgn.info("ALU: %s cmp %s" % (bm.btd(num_a), bm.btd(num_b)))
			lgn.info("CMP: %s" % (bm.blts(comp)))
		else:					#Error
			lgn.critical("ALU: Invalid function call at line %s" % (bm.btd(ln)))
			raise Exception
	
	comp.append(co)
	lgn.info("ALU: %s" % (comp))
	reg(ReadWrite.WRITE, ProtReg.AOR, RegType.PROTECTED, q)
	lgn.debug("AOR: %s" % (bm.user_btd(q)))
	if set_list[ALUConfig.SETFLAGS.value]:
		reg(ReadWrite.WRITE, ProtReg.FLAGS, RegType.PROTECTED, comp)
	return 1

#----------------------------------------------------------
#Update ALU test for improved testing
#Test ALU
try:
	buf(1, bm.user_dtb(5))
	reg(ReadWrite.WRITE, ALUConfig.BREGISTER, RegType.ALU, bm.user_dtb(3))
	reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, bm.dtb(0, 4))
	reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, bm.dtb(1, 1))
	alu_r = alu()
	if alu_r == 1:
		lgn.debug("ALU tested.")
	else:
		lgn.critical("ALU: Unknown Error.")
except Exception:
	lgn.critical(EmulatorRuntimeError.ALUNOTINITIATED.value)
	raise RuntimeError

def pci():
	ena_list = reg(ReadWrite.READ, ProtReg.ENABLELIST, RegType.PROTECTED)
	set_list = reg(ReadWrite.READ, ProtReg.SETLIST, RegType.PROTECTED)
	
	incremented_pc = bm.dtb(0)
	
	if ena_list[0]:
		pc = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
		WordOne = bm.dtb(1)
		incremented_pc = g.la(pc, WordOne)[0]
	
	if set_list[0]:
		reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, incremented_pc)

#Setup Processor
FunctionDefinitionMetaInfo = [
	"FETCH",	#Special non-user accessible
	"ALU",
	"ROM",		#Starting for indexing
	"RAM",
	"REG",
	"STACK",
	"CONDITIONALBRANCH",
	"CALLRETURNFUNCTION",
	"GPIO",
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

def pr(lst, gui=False):#Print function
	if gui == True:
		print(str(bm.blts(lst, False, True)))
	elif gui == "not":
		print(str(bm.btd(lst)))
	elif gui == "bin":
		print(bm.btbs(lst))
	else:
		print("Output: " + str(bm.user_btd(lst)))

#Defining the functions pin outputs
FunctionDefinitions = [
	
	[		#Set pins
		[	#Fetch-------------------             0
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
		],
		[	#ALU definition
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
		],
		[	#ROM At Immediate--------------------
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#ROM At Address At Immediate
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Immediate READ---------------
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate READ     5
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#RAM At Immediate WRITE
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate WRITE
			[1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#REG Swap----------------------------
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#REG Clone
			[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#STACK PUSH--------------------------10
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK POP
			[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#STACK POINT TO AT REGISTER
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK GET POINTER
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#CONDITIONAL-------------------------
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#INTERRUPT                           15
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#CALL FUNCTION-----------------------
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#RegA
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#Initiate branch
			[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Branch to @ next word
		],
		[	#RETURN FUNCTION
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Pop from stack
			[0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#PC
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#Push to stack
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#RegA
		],
		[	#GPIO At Immediate Register Read-----
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Read
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Immediate Register Write    20
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Write
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],	#
		],
	],
	
	[		#Enable pins
		[	#Fetch
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
		],
		[	#ALU
			[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
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
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate READ
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		],
		[	#RAM At Immediate WRITE
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#RAM At Address At Immediate WRITE
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
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
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
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
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],	#
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
		[	#GPIO At Immediate Register Read
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Read
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Immediate Register Write
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Write
			[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
	],
]

#Set Set Pins
#pci, pc, abr, cb, aor, rama, ramd, roma, gpioa, gpiod, flg, pid, reg_a, reg_b, reg_c, cui, sp, ism, if
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

#----------------------------------------------
#Update for new function definitions!
def ofs(func, instruction_vars):	#Offset
	
	if instruction_vars[RuntimeVariables.LOGICALALU.value][0] == 1:
		return 1, 1
	
	#ftch, alu, rom, ram, reg, stck, conbrnch, intrpt, callretrn
	#-----------------------------------------------------------------
	ofs_array		= [2, 4,8,10,14,16,18]
	ofs_use_var_a	= [0,1,0,0,0,0,0,1]
	ofs_use_var_b	= [1,0,1,1,0,0,1,0]
	
	tl = []
	try:
		if ofs_use_var_b[func]:
			tl = bm.bla(tl, instruction_vars[RuntimeVariables.VARIABLEA.value])
	except IndexError:
		ProgramCounter = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
		lgn.critical("Offset: Error: Program Counter: %s: Invalid function number." % (bm.btd(ProgramCounter)))
		return EmulatorRuntimeError.ILLEGALFUNCTION, -1
	if ofs_use_var_a[func]:
		tl = bm.bla(tl, instruction_vars[RuntimeVariables.VARIABLEB.value])
	
	dtl = bm.btd(tl)
	return ofs_array[func] + dtl, func+2

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
			variables=None):
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
	global buf
	set(set_list)
	enable(ena_list)
	var = bz
	
	try:
		reg_a = variables[RuntimeVariables.REGISTERA.value]
		reg_b = variables[RuntimeVariables.REGISTERB.value]
		reg_c = variables[RuntimeVariables.REGISTERC.value]
		
		reg_a = [bm.btd(reg_a[2:]),bm.btd(reg_a[:2])]
		reg_b = [bm.btd(reg_b[2:]),bm.btd(reg_b[:2])]
		reg_c = [bm.btd(reg_c[2:]),bm.btd(reg_c[:2])]
	except Exception:
		pass
	
	#Enable actions:
	# if ena_list[0]:		#pci
		# pci()
	if ena_list[1]:		#pc
		var = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	if ena_list[2]:		#aor 
		var = reg(ReadWrite.READ, ProtReg.AOR, RegType.PROTECTED)
	if ena_list[3]:		#Increment
		alu()
	if ena_list[4]:		#Decrement
		alu()
	if ena_list[5]:		#ramd 
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		var = ram(ReadWrite.READ, bm.btd(tmp), "RAMD ENABLE EXECUTE()")
		lgn.debug("RAMD: %s READS %s" % (bm.btd(tmp), bm.blts(var)))
	if ena_list[6]:		#romd 
		tmp = reg(ReadWrite.READ, ProtReg.ROMADDRESS, RegType.PROTECTED)
		try:
			var = rom(0, bm.btd(tmp))
		except IndexError:
			temp = reg(ReadWrite.READ, ProtReg.ROMADDRESS, RegType.PROTECTED)
			lgn.critical("ROM: Error: Invalid program counter: %s" % (bm.btd(temp)))
			raise IndexError
	if ena_list[7]:		#Register intermediate data
		var = reg(ReadWrite.READ, ProtReg.REGINTERMEDIATE, RegType.PROTECTED)
	if ena_list[8]:		#gpi 
		var = bm.user_dtb(float(input("Number: ")))
	if ena_list[9]:		#rega 
		lgn.debug("Execute: REGA: %s:%s" % (reg_a[0], reg_a[1]))
		var = reg(ReadWrite.READ, reg_a[0], reg_a[1])
	if ena_list[10]:	#regb 
		lgn.debug("Execute: REGB: %s:%s" % (reg_b[0], reg_b[1]))
		var = reg(ReadWrite.READ, reg_b[0], reg_b[1])
	if ena_list[11]:	#regc
		var = reg(ReadWrite.READ, reg_c[0], reg_c[1])
	if ena_list[12]:	#stack pointer
		var = reg(ReadWrite.READ, ProtReg.STACKPOINTER, RegType.PROTECTED)
	
	buf(1,var)
	# lgn.debug("BUFFER:%s" % (bm.blts(var)))
	
	#Set actions:
	if set_list[1]:	#pc
		reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, var)
	if set_list[2]:	#abr
		temp = buf(0)
		lgn.debug("Execute: ALU B Register: %s" % (bm.user_btd(temp)))
		reg(ReadWrite.WRITE, ALUConfig.BREGISTER, RegType.ALU, var)
	if set_list[3]:	#conditional branch
		comparison = reg(ReadWrite.READ, ProtReg.FLAGS, RegType.PROTECTED)
		if isinstance(variables[2], type(None)):
			lgn.critical("Execute: Comparison variable not given.")
			raise TypeError
		lgn.info("CB: %s, %s" % (bm.blts(comparison[0:4]), bm.blts(variables[2])))
		if variables[3][0] == 1 or bm.btd(g.al(comparison[0:4], variables[2])) == 0:
			lgn.info("Conditional Branch: BRANCHED.")
			reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, var)
	if set_list[4]:	#aor
		alu_r = alu()
		if alu_r != 1:
			lgn.warning(EmulatorRuntimeError.ALUFAILED.value)
			raise Exception
	if set_list[5]:	#rama
		reg(ReadWrite.WRITE, ProtReg.RAMADDRESS, RegType.PROTECTED, var)
	if set_list[6]:	#ramd
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		lgn.debug("RAMD: %s -> %s" % (bm.btd(tmp), bm.user_btd(var)))
		ram(ReadWrite.WRITE, bm.btd(tmp), var)
	if set_list[7]:	#roma
		reg(ReadWrite.WRITE, ProtReg.ROMADDRESS, RegType.PROTECTED, var)
	if set_list[8]:	#gpoa
		lgn.info("Set GPIO Address: %s" % (bm.btd(var)))
	if set_list[9]:	#gpod
		pr(var, gui)
	if set_list[11]:	#pid
		temp = reg(ReadWrite.READ, reg_a[0], reg_a[1])
		lgn.debug("RID: %s:%s -> %s" % (reg_b[0], reg_b[1], bm.btd(temp)))
		reg(ReadWrite.WRITE, ProtReg.REGINTERMEDIATE, RegType.PROTECTED, var)
	if set_list[12]:	#rega
		temp_pc = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
		lgn.debug("SET: %s:%s = %s @ PC: %s" % (reg_a[0], reg_a[1], bm.btd(var), bm.btd(temp_pc)))
		lgn.debug("ENABLELIST: %s\nSETLIST: %s" % (bm.blts(ena_list), bm.blts(set_list)))
		reg(ReadWrite.WRITE, reg_a[0], reg_a[1], var)
	if set_list[13]:	#regb
		reg(ReadWrite.WRITE, reg_b[0], reg_b[1], var)
	if set_list[14]:	#regc
		reg(ReadWrite.WRITE, reg_c[0], reg_c[1], var)
	if set_list[15]:	#cui
		reg(ReadWrite.WRITE, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED, var)
	if set_list[16]:	#sp
		lgn.debug("Stack pointer WRITE: %s" % (bm.btd(var)))
		reg(ReadWrite.WRITE, ProtReg.STACKPOINTER, RegType.PROTECTED, var)
	if set_list[0]:
		pci()

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
	lgn.info("SingleRun: Program Counter: %s" % (bm.btd(ln)))
	
	#fetch next instruction 
	for i, _ in enumerate(FunctionDefinitions[0][0]):
	inp = reg(ReadWrite.READ, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED)
	
	#if input is all 1s, exit with return code 1
	exit_signal = True
	for i, e in enumerate(inp):
		if not isinstance(inp[i], int):
			lgn.critical("SingleInstruction: Error: Invalid instruction.")
			raise Exception
		if inp[i] != 1:
			exit_signal = False
			break
	if exit_signal:
		if force_show_exceptions:
			lgn.debug("EXIT_SIGNAL.")
		return 1
		
	comp = reg(ReadWrite.READ, ProtReg.AOR, RegType.PROTECTED)
	
	#get input variables
	#Where the different variables start in input space
	var_ofs = [0,4,5,9,11,18,25]
	
	#Length of variables 
	var_lengs = [4,1,4,2,7,7,7]
	
	#Unpack instruction to variables
	instruction_vars = []
	for i, e in enumerate(var_lengs):
		t = []
		for j in range(e):
			if inp[var_ofs[i] + j]:
				t.append(1)
			else:
				t.append(0)
		instruction_vars.append(t)
	
	if force_show_exceptions:
		for i, var in enumerate(instruction_vars):
			lgn.info("%s: %s" % (RuntimeVariables(i).name, bm.blts(var)))
	
	_ofs, meta_func = ofs(bm.btd(instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value]), instruction_vars)
	if _ofs == EmulatorRuntimeError.ILLEGALFUNCTION:
		return -1
	
	lgn.debug("SingleInstruction: MetaFunction: %s, ofs: %s" % (FunctionDefinitionMetaInfo[meta_func], _ofs))
	# lgn.debug("SingleInstruction: Runtime variables: \n%s" % (instruction_vars))
	if instruction_vars[RuntimeVariables.LOGICALALU.value][0] == 1:
		lgn.info("SingleInstruction: ALU Function: %s" % (instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value]))
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value])
		reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, instruction_vars[RuntimeVariables.VARIABLEB.value])
	else:
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, bm.dtb(0, 4))
		reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, bm.dtb(2))
	for i, _ in enumerate(FunctionDefinitions[0][_ofs]):
		lgn.debug("RUN: %s" % (i))
		execute(FunctionDefinitions[0][_ofs][i], 
				FunctionDefinitions[1][_ofs][i], 
				gui, instruction_vars)
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
	
	lgn.getLogger().setLevel(LOGLEVEL)
	
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
	t = initialize_rom(filename)
	if t != 1:
		lgn.critical("Run: ROM couldn't be initialised properly.")
	if time_runtime:
		start_time = time.time()
	
	#Execute program 
	while True:
		q = single_instruction(0, gui, print_line_nr, force_show_exceptions)
		if isinstance(q, int):
			if q == 1:
				if time_runtime:
					end_time = time.time()
					lgb.debug("elapsed time: %s" % (end_time-start_time))
					return [1, end_time-start_time]
				lgn.debug("Run: Program returned with exit code 1.")
				return 1
			elif q == -1:
				lgn.critical("Error: %s.run(): return code -1, runtime stopped" % (__file__))
				raise Exception
			elif q != 0:
				lgn.warning(q)
				print(q)