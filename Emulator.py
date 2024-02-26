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
	
	global rom_data 
	rom_data = []
	rom_fh = open(bf + exeff + Filename + file_extension_name, "r")
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

#Internal registers emulated as list of lists
regs = [
	[bz for i in range(32)],	#General Purpose Registers
	[bz for i in range(32)],	#Arithmetic/Logic Unit Registers
	[bz for i in range(32)],	#Stack Pointers
	[bz for i in range(10)],	#Special Purpose Internal CU Register
]

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

class ALUReturnStates(Enum):
	NoError = 0
	SuspendingCentralProcessingExit = 1
	UndefinedError = 2
	InvalidFunction = 3
	InvalidType = 3
	InvalidComparison = 4

class ALUType(Enum):
	int = 0
	float = 1
	char = 2
	string = 3
	bool = 4
	array = 5
	list = 6

class ALUIntFunction(Enum):
	add = 0
	sub = 1
	mul = 2
	div = 3
	land = 4
	lor = 5
	lxor = 6
	lnot = 7
	comp = 15

class ALUFloatFunction(Enum):
	add = 0
	sub = 1
	mul = 2
	div = 3
	intdiv = 4
	comp = 15

class ALUCharFunction(Enum):
	read = 0
	write = 1
	comp = 15

class ALUStringFunction(Enum):
	char_append = 0
	string_append = 1
	char_read = 2
	char_write = 3
	comp = 15

class ALUBoolFunction(Enum):
	read = 0
	write = 1
	comp = 15

class ALUArrayFunction(Enum):
	declare_size = 0
	declare_item_length = 1
	read_element = 2
	write_element = 3

class ExecuteReturnStates(Enum):
	NoError = 0
	ALUError = 1
	UnknownError = 2

class SingleInstructionReturnStates(Enum):
	NoErrorContinue = 0
	NoErrorExit = 1
	UnknownError = 2
	InvalidFunction = 3

class RuntimeVariables(Enum):
	FUNCTIONVARIABLE = 0
	LOGICALALU = 1
	VARIABLEA = 2
	VARIABLEB = 3
	REGISTERA = 4
	REGISTERB = 5
	REGISTERC = 6

class EmulatorRuntimeError(Enum):
	ALUFAILED = "ALU: Unknown error"
	ALUNOTINITIATED = "ALU: Couldn't initiate"
	ILLEGALFUNCTION = "Offset: Illegal function called"

class SuspendCentralUnitStates(Enum):
	not_applicable = -1
	alu_array_execution = 0
	alu_list_execution = 1

class binary_input_indecies(Enum):
	MainFunction = 0
	IsALU = 4
	VariableA = 5
	VariableB = 9
	RegisterA = 11
	RegisterB = 18
	RegisterC = 25

class binary_input_lengths(Enum):
	MainFunction = 4
	IsALU = 1
	VariableA = 4
	VariableB = 2
	RegisterA = 7
	RegisterB = 7
	RegisterC = 7

suspend_central_unit_processing = False
suspend_central_unit_state = SuspendCentralUnitStates.not_applicable.value

#Functions to manage buffer, registers and other memory storage units
def buf(rw, list=bz):
	global buffer 
	if rw == 0:
		return buffer 
	
	buffer = list

def ZeroWord():
	return [0 for i in range(bw)]

def rom(rw, index):
	global rom_data
	if rw == 1:
		return 
	
	global rom_data
	
	return rom_data[index]

def ram(rw, index, value=None):
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
		try:
			return ramv[index]
		except IndexError:
			lgn.critical("Error: RAM address invalid %s" % (index))
			raise IndexError
	try:
		ramv[index] = value
	except IndexError:
		lgn.critical("Error: RAM address invalid %s" % (index))
		raise IndexError
	return

def reg(rw, index, reg_type, value=None):
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
	# if isinstance(value, float):
	# 	value = bm.user_dtb(value)
	if not isinstance(value[0], int):
		try:
			value = bm.btd(value)
		except Exception:
			lgn.critical("Register: Invalid type of register assignement. (%s)" % (value))
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
def alu(instruction_variables=None):		#//Update for new ALU
	"""alu() -> executes arithmetic and logic operations based on flags set and registers
	Returns: return code: 1 for function completed succesfully or passes any errors
	"""
	
	if instruction_variables is None:
		instruction_variables = [[0 for i in range(32)] for j in range(8)]

	global reg
	global suspend_central_unit_processing
	global suspend_central_unit_state
	
	#Get inputs
	ena_list = reg(ReadWrite.READ, ProtReg.ENABLELIST, RegType.PROTECTED)
	set_list = reg(ReadWrite.READ, ProtReg.SETLIST, RegType.PROTECTED)
	ln = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	func = bm.btd(reg(ReadWrite.READ, ALUConfig.ALUFUNCTION, RegType.ALU)[0:4])
	if instruction_variables[RuntimeVariables.LOGICALALU.value][0]:
		lgn.debug("ALU: Compute function!")
		type = bm.btd(instruction_variables[RuntimeVariables.VARIABLEA.value])
	else:
		type = 0
	
	lgn.debug("ALU: Type: %s, function: %s" % (type, func))

	#Get input B or 1 for increment or decrement
	if ena_list[ALUConfig.PROGRAMCOUNTERINCREMENT.value] or ena_list[ALUConfig.INCREMENT.value] or ena_list[ALUConfig.DECREMENT.value]:
		num_b = bm.dtb(1)
	else:
		num_b = reg(ReadWrite.READ, ALUConfig.BREGISTER, RegType.ALU)
	
	num_a = buf(0)
	lgn.debug("ALU: ALU A Register: %s | %s" % (bm.user_btd(num_a), bm.btd(num_a)))
	
	comp = [0,0,0]

	q = []
	co = 0
	
	#Compute computation
	if type == ALUType.int.value:
		if func == ALUIntFunction.add.value and ena_list[ALUConfig.DECREMENT.value] != 1:
			q = bm.dtb(bm.btd(num_a) + bm.btd(num_b))
		elif func == ALUIntFunction.sub.value or ena_list[ALUConfig.DECREMENT.value]:
			q = bm.dtb(bm.btd(num_a) - bm.btd(num_b))
		elif func == ALUIntFunction.mul.value:
			q = bm.dtb(bm.btd(num_a) * bm.btd(num_b))
		elif func == ALUIntFunction.div.value:
			q = bm.dtb(bm.btd(num_a) / bm.btd(num_b))
			lgn.debug("ALU: int div, q: %s" % (q))
		elif func == ALUIntFunction.land.value:
			q = bm.dtb(g.a(num_a, num_b))
		elif func == ALUIntFunction.lor.value:
			q = bm.dtb(g.o(num_a, num_b))
		elif func == ALUIntFunction.lxor.value:
			q = bm.dtb(g.x(num_a, num_b))
		elif func == ALUIntFunction.lnot.value:
			q = bm.dtb(g.n(num_a))
		elif func == ALUIntFunction.comp.value:
			q = num_a
			decimal_a = bm.btd(num_a)
			decimal_b = bm.btd(num_b)
			if decimal_a > decimal_b:
				comp = [1,0,0]
			elif decimal_a == decimal_b:
				comp = [0,1,0]
			elif decimal_a < decimal_b:
				comp = [0,0,1]
		else:
			lgn.critical("Error: Invalid int function.")
			return ALUReturnStates.InvalidFunction
	elif type == ALUType.float.value:
		if func == ALUFloatFunction.add.value:
			q = bm.user_dtb(bm.user_btd(num_a) + bm.user_btd(num_b))
		elif func == ALUFloatFunction.sub.value:
			q = bm.user_dtb(bm.user_btd(num_a) - bm.user_btd(num_b))
		elif func == ALUFloatFunction.mul.value:
			q = bm.user_dtb(bm.user_btd(num_a) * bm.user_btd(num_b))
		elif func == ALUFloatFunction.div.value:
			q = bm.user_dtb(bm.user_btd(num_a) / bm.user_btd(num_b))
		elif func == ALUFloatFunction.intdiv.value:
			q = bm.user_dtb(math.floor(bm.user_btd(num_a) / bm.user_btd(num_b)))
		elif func == ALUFloatFunction.comp.value:
			q = num_a
			comparison = bm.float_compare(num_a, num_b)
			if comparison == bm.FloatComparisonStates.greater_than:
				comp = [1,0,0]
			elif comparison == bm.FloatComparisonStates.equals:
				comp = [0,1,0]
			elif comparison == bm.FloatComparisonStates.less_than:
				comp = [0,0,1]
			elif comparison == bm.FloatComparisonStates.invalid_comparison:
				lgn.critical("Error: Invalid comparison")
				return ALUReturnStates.InvalidComparison
		else:
			lgn.CRITICAL("Error: Invalid float function at line %s" % (bm.btd(ln)))
			return ALUReturnStates.InvalidFunction
	elif type == ALUType.char.value:
		if func == ALUCharFunction.read.value:
			q = bm.char_read(num_a, num_b)
		elif func == ALUCharFunction.write.value:
			index = instruction_variables[RuntimeVariables.VARIABLEA.value] + instruction_variables[RuntimeVariables.VARIABLEB.value]
			q = bm.char_Write(num_a, num_b, index)
		elif func == ALUCharFunction.comp.value:
			q = num_a
		else:
			lgn.CRITICAL("Error: invalid char function at line %s" % (bm.btd(ln)))
			return ALUReturnStates.InvalidFunction
	elif type == ALUType.string.value:
		if func == ALUStringFunction.char_append.value:
			q = bm.string_char_append(num_a, num_b)
		elif func == ALUStringFunction.string_append.value:
			q = bm.string_string_append(num_a, num_b)
		elif func == ALUStringFunction.char_read.value:
			q = bm.string_char_read(num_a, num_b)
		elif func == ALUStringFunction.char_write.value:
			index = instruction_variables[RuntimeVariables.VARIABLEA.value] + instruction_variables[RuntimeVariables.VARIABLEB.value]
			q = bm.string_char_write(num_a, num_b, index)
		elif func == ALUStringFunction.comp.value:
			q = num_a
		else:
			lgn.CRITICAL("Error: invalid string function at line %s" % (bm.btd(ln)))
			return ALUReturnStates.InvalidFunction
	elif type == ALUType.bool.value:
		if func == ALUBoolFunction.read.value:
			q = bm.bool_read(num_a, num_b)
		elif func == ALUBoolFunction.write.value:
			q = bm.bool_write(num_a, num_b, instruction_variables[RuntimeVariables.VARIABLEA][0])
		elif func == ALUBoolFunction.comp.value:
			q = num_a
		else:
			lgn.CRITICAL("Error: invalid bool function at line %s" % (bm.btd(ln)))
			return ALUReturnStates.InvalidFunction
	elif type == ALUType.array.value:
		lgn.critical("Error: Array not implemented yet.")
		return ALUReturnStates.InvalidFunction
		# suspend_central_unit_state = SuspendCentralUnitStates.alu_array_execution
		# if func in ALUArrayFunction:
		# 	return ALUReturnStates.SuspendingCentralProcessingExit
		# else:
		# 	lgn.CRITICAL("Error: invalid array function at line %s" % (bm.btd(ln)))
		# 	return ALUReturnStates.InvalidFunction
	elif type == ALUType.list.value:
		lgn.critical("Error: List not implemented yet.")
		return ALUReturnStates.InvalidFunction
	else:
		lgn.CRITICAL("Error: invalid ALU type at line %s: %s" % (ln, func))
		return ALUReturnStates.InvalidType

	#Manage output
	comp.append(co)
	lgn.info("ALU: %s" % (comp))
	reg(ReadWrite.WRITE, ProtReg.AOR, RegType.PROTECTED, q)
	lgn.debug("AOR: %s, %s" % (bm.user_btd(q), bm.btd(q)))
	if set_list[ALUConfig.SETFLAGS.value]:
		reg(ReadWrite.WRITE, ProtReg.FLAGS, RegType.PROTECTED, comp)
	
	return ALUReturnStates.NoError

#----------------------------------------------------------
#Update ALU test for improved testing
#Test ALU
def test_alu():
	try:
		lgn.debug("ALU: Testing integrity of ALU.")
		buf(1, bm.user_dtb(5))
		reg(ReadWrite.WRITE, ALUConfig.BREGISTER, RegType.ALU, bm.user_dtb(3))
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, bm.dtb(0, 4))
		reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, bm.dtb(1, 1))
		alu_r = alu()
		if alu_r == ALUReturnStates.NoError:
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
		buf(1, ZeroWord())
	if r == 1:
		ramv = [
			ZeroWord() for i in range(1024)
		]
	if g == 1:
		for i, _ in enumerate(regs):
			for j, _ in enumerate(regs[i]):
				regs[i][j] = ZeroWord()

def pr(lst, gui=False):#Print function
	advanced_show = False
	if gui == True:
		print(str(bm.blts(lst, False, True)))
	elif gui == "not":
		print(str(bm.btd(lst)))
	elif gui == "bin":
		print(bm.btbs(lst))
	else:
		if advanced_show:
			print("Output: %s | %s" % (str(bm.user_btd(lst)), str(bm.user_btc(lst))))
		else:
			print("Output: %s" % (bm.user_btc(lst)))

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
		[	#REG Swap-----------------------------------
			[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#REG Clone
			[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
		],
		[	#STACK PUSH UP------------------------------10
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK POP UP
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
		[	#STACK PUSH DOWN
			[0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK POP DOWN
			[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#STACK POINT TO AT REGISTER (Required for weird variables usage)15
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
		],
		[	#STACK GET POINTER							
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
		],
		[	#CONDITIONAL--------------------------------
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#INTERRUPT                           
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#CALL FUNCTION------------------------------20
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
		[	#GPIO At Immediate Register Read------------
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Read	
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],	#
		],
		[	#GPIO At Immediate Register Write    
			[1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],	#
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],	#
		],
		[	#GPIO At Address At Immediate Register Write25
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
		[	#STACK PUSH UP
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#STACK POP UP
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
		[	#STACK PUSH DOWN
			[0,0,0,0,1,0,0,0,0,0,0,0,1,0,0],
			[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
		],
		[	#STACK POP DOWN
			[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],
			[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
			[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
		],
		[	#STACK POINT TO AT REGISTER(Required for weird variables usage)
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

SuspendCentralUnitDefinitions = [

	[	#Set pins

		[	#ALU Array execution

			[	#declare size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],	
			[	#declare object size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#read
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#write
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
		],
		[	#ALU List execution

			[	#get size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],	
			[	#push
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#pop
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
		],

	],
	[	#Enable pins

		[	#ALU Array execution

			[	#declare size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#declare object size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#read
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#write
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],

		],
		[	#ALU List execution

			[	#get size
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#push
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],
			[	#pop
				[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
			],

		],

	],

]

#Set Set Pins
#pci, pc, abr, cb, aor, rama, ramd, roma, gpioa, gpiod, flg, pid, reg_a, reg_b, reg_c, cui, sp, ism, if
def set(list):		
	"""set(list) -> Function to set set pins
	"""
	reg(ReadWrite.WRITE, ProtReg.SETLIST, RegType.PROTECTED, list)

#Set Enable Pins
#pci, pc, aor, inc, decrement, ramd, romd, pid, gpi, reg_a, reg_b, reg_c, sp, ism, if
def enable(list):	
	"""enable(list) -> Function to set enable pins
	"""	
	reg(ReadWrite.WRITE, ProtReg.ENABLELIST, RegType.PROTECTED, list)

def sr(lst, comp, var_a=[0]):	#Should Run?
	for i, e in enumerate(lst):
		if g.a(comp[i], lst[i]) == 1:
			return g.x(0,var_a[0])
	return g.x(1,var_a[0])

#----------------------------------------------
#Update for new function definitions!
def ofs(func, instruction_vars):	#Offset
	
	# lgn.debug("OFS: Instruction Variables: %s" % (instruction_vars))
	if instruction_vars[RuntimeVariables.LOGICALALU.value][0] == 1:
		return 1, 1
	
	#ftch, alu, rom, ram, reg, stck, conbrnch, intrpt, callretrn
	#-----------------------------------------------------------------
	ofs_array		= [2,4,8,10,18,20,22]
	ofs_use_var_a	= [0,1,0,1,0,0,0,1]
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

def dump_rom():
	global rom_data
	lgn.debug("ROM: Dumping ROM:")
	for i, line in enumerate(rom_data):
		lgn.debug("%s: %s" % (i, bm.blts(line)))

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
	
	#Attempt to get registers
	try:
		reg_a = variables[RuntimeVariables.REGISTERA.value]
		reg_b = variables[RuntimeVariables.REGISTERB.value]
		reg_c = variables[RuntimeVariables.REGISTERC.value]
		
		reg_a = [bm.btd(reg_a[2:]),bm.btd(reg_a[:2])]
		reg_b = [bm.btd(reg_b[2:]),bm.btd(reg_b[:2])]
		reg_c = [bm.btd(reg_c[2:]),bm.btd(reg_c[:2])]
	except Exception:
		lgn.debug("Attempt at registers incomplete")
	
	#Enable actions:
	if ena_list[1]:		#pc
		var = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	if ena_list[2]:		#aor 
		var = reg(ReadWrite.READ, ProtReg.AOR, RegType.PROTECTED)
	if ena_list[5]:		#ramd 
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		var = ram(ReadWrite.READ, bm.btd(tmp), "RAMD ENABLE EXECUTE()")
		lgn.debug("RAMD: %s READS %s | %s" % (bm.btd(tmp), bm.btd(var), bm.user_btd(var)))
	if ena_list[6]:		#romd 
		tmp = reg(ReadWrite.READ, ProtReg.ROMADDRESS, RegType.PROTECTED)
		try:
			var = rom(0, bm.btd(tmp))
			lgn.debug("Execute: Read ROM: %s | %s" % (bm.blts(var), bm.user_btd(var)))
		except IndexError:
			temp = reg(ReadWrite.READ, ProtReg.ROMADDRESS, RegType.PROTECTED)
			lgn.critical("ROM: Error: Invalid program counter: %s" % (bm.btd(temp)))
			raise IndexError
	if ena_list[7]:		#Register intermediate data
		var = reg(ReadWrite.READ, ProtReg.REGINTERMEDIATE, RegType.PROTECTED)
	if ena_list[8]:		#gpi 
		var = bm.user_dtb(float(input("Number: ")))
	if ena_list[9]:		#rega 
		var = reg(ReadWrite.READ, reg_a[0], reg_a[1])
		lgn.debug("Execute: Read REGA: %s:%s = %s | %s" % (reg_a[0], reg_a[1], bm.btd(var), bm.user_btd(var)))
	if ena_list[10]:	#regb 
		lgn.debug("Execute: Read REGB: %s:%s" % (reg_b[0], reg_b[1]))
		var = reg(ReadWrite.READ, reg_b[0], reg_b[1])
	if ena_list[11]:	#regc
		var = reg(ReadWrite.READ, reg_c[0], reg_c[1])
	if ena_list[12]:	#stack pointer
		var = reg(ReadWrite.READ, ProtReg.STACKPOINTER, RegType.PROTECTED)
		lgn.debug("Using Stack Pointer: %s" % (bm.btd(var)))
	
	buf(1,var)
	
	#Set actions:
	if set_list[1]:		#pc
		reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, var)
	if set_list[2]:		#abr
		temp = buf(0)
		lgn.debug("Execute: ALU B Register: %s" % (bm.user_btd(temp)))
		reg(ReadWrite.WRITE, ALUConfig.BREGISTER, RegType.ALU, var)
	if set_list[3]:		#conditional branch
		comparison = reg(ReadWrite.READ, ProtReg.FLAGS, RegType.PROTECTED)
		if isinstance(variables[2], type(None)):
			lgn.critical("Execute: Comparison variable not given.")
			raise TypeError
		lgn.info("CB: %s, %s" % (bm.blts(comparison[0:4]), bm.blts(variables[2])))
		if variables[3][0] == 1 or bm.btd(g.al(comparison[0:4], variables[2])) == 0:
			lgn.info("Conditional Branch: BRANCHED.")
			reg(ReadWrite.WRITE, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED, var)
	if set_list[4]:		#aor
		lgn.debug("ALU: Instruction Variables: %s" % (variables))
		alu_r = alu(variables)
		if alu_r != ALUReturnStates.NoError:
			lgn.critical("%s, %s." % (str(EmulatorRuntimeError.ALUFAILED.value), str(alu_r)))
			return ExecuteReturnStates.ALUError
	if set_list[5]:		#rama
		lgn.debug("RAM Address Write: %s" % (bm.btd(var)))
		reg(ReadWrite.WRITE, ProtReg.RAMADDRESS, RegType.PROTECTED, var)
	if set_list[6]:		#ramd
		tmp = reg(ReadWrite.READ, ProtReg.RAMADDRESS, RegType.PROTECTED)
		lgn.debug("RAMD Write: %s -> %s | %s" % (bm.btd(tmp), bm.btd(var), bm.user_btd(var)))
		ram(ReadWrite.WRITE, bm.btd(tmp), var)
	if set_list[7]:		#roma
		reg(ReadWrite.WRITE, ProtReg.ROMADDRESS, RegType.PROTECTED, var)
	if set_list[8]:		#gpoa
		lgn.info("Set GPIO Address: %s" % (bm.btd(var)))
	if set_list[9]:		#gpod
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
		lgn.debug("Execute: set reg_c: %s" % (var))
		reg(ReadWrite.WRITE, reg_c[0], reg_c[1], var)
	if set_list[15]:	#cui
		reg(ReadWrite.WRITE, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED, var)
	if set_list[16]:	#sp
		lgn.debug("Stack pointer WRITE: %s" % (bm.btd(var)))
		reg(ReadWrite.WRITE, ProtReg.STACKPOINTER, RegType.PROTECTED, var)
	if set_list[0]:		#PC Increment
		pci()
	
	return ExecuteReturnStates.NoError

#Run Single Instruction
def single_instruction(reset=0, gui=False, 
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
	global suspend_central_unit_processing
	global suspend_central_unit_state
	
	#Handle reset
	if reset != 0:	#Reset
		cls(1,1,1)
		lgn.debug("Cleared registers")
		return SingleInstructionReturnStates.NoErrorContinue
	
	#Get program counter, mainly for debugging
	ln = reg(ReadWrite.READ, ProtReg.PROGRAMCOUNTER, RegType.PROTECTED)
	lgn.info("SingleRun: Program Counter: %s" % (bm.btd(ln)))
	
	#fetch next instruction 
	for i, _ in enumerate(FunctionDefinitions[0][0]):
		lgn.debug("FETCH: %s" % (i))
		execute(FunctionDefinitions[0][0][i], FunctionDefinitions[1][0][i])
	inp = reg(ReadWrite.READ, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED)
	
	lgn.debug("SingleRun: Fetched instruction!")

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
		return SingleInstructionReturnStates.NoErrorExit
	
	lgn.debug("SignleRun: No Exit Signal!")

	#get input variables
	#Where the different variables start in input space
	var_ofs = [
				binary_input_indecies.MainFunction.value,
				binary_input_indecies.IsALU.value,
				binary_input_indecies.VariableA.value,
				binary_input_indecies.VariableB.value,
				binary_input_indecies.RegisterA.value,
				binary_input_indecies.RegisterB.value,
				binary_input_indecies.RegisterC.value,
				]

	var_lengs = [
				binary_input_lengths.MainFunction.value,
				binary_input_lengths.IsALU.value,
				binary_input_lengths.VariableA.value,
				binary_input_lengths.VariableB.value,
				binary_input_lengths.RegisterA.value,
				binary_input_lengths.RegisterB.value,
				binary_input_lengths.RegisterC.value,
			  ]
	
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
	
	#Get offset from function list and meta information for debugging
	_ofs, meta_func = ofs(bm.btd(instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value]), instruction_vars)
	if _ofs == EmulatorRuntimeError.ILLEGALFUNCTION:
		return SingleInstructionReturnStates.InvalidFunction
	
	lgn.debug("SingleRun: Got Offset and Meta Function!")

	#Make registers ready for execution
	lgn.debug("SingleInstruction: MetaFunction: %s, ofs: %s" % (FunctionDefinitionMetaInfo[meta_func], _ofs))
	if instruction_vars[RuntimeVariables.LOGICALALU.value][0] == 1:	#If it is an alu operation
		lgn.info("SingleInstruction: ALU Function: %s" % (bm.blts(instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value])))
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, instruction_vars[RuntimeVariables.FUNCTIONVARIABLE.value])
		reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, instruction_vars[RuntimeVariables.VARIABLEB.value])
		lgn.debug("SingleRun: Set ALU variables!")
	else:															#If it is a function operation
		reg(ReadWrite.WRITE, ALUConfig.ALUFUNCTION, RegType.ALU, bm.dtb(0, 4))
		reg(ReadWrite.WRITE, ALUConfig.SPECIALFUNCTION, RegType.PROTECTED, bm.dtb(2))
		lgn.debug("SingleRun: Set Function variables!")
	
	#Execute operation
	if suspend_central_unit_processing:
		if suspend_central_unit_state != SuspendCentralUnitStates.not_applicable.value:
			for i, _ in enumerate(SuspendCentralUnitDefinitions[0][suspend_central_unit_state.value]):
				lgn.debug("SUSPENDED RUN: %s" % (i))
				execute(SuspendCentralUnitDefinitions[0][suspend_central_unit_state.value][i],
						SuspendCentralUnitDefinitions[0][suspend_central_unit_state.value][i],
						gui, instruction_vars
			)
			suspend_central_unit_state = SuspendCentralUnitStates.not_applicable.value
			return SingleInstructionReturnStates.NoErrorContinue
	
	lgn.debug("SingleRun: No Suspended Execution!")

	for i, _ in enumerate(FunctionDefinitions[0][_ofs]):
		lgn.debug("RUN: %s" % (i))
		er = execute(FunctionDefinitions[0][_ofs][i], 
					FunctionDefinitions[1][_ofs][i], 
					gui, instruction_vars)

		if er != ExecuteReturnStates.NoError:
			lgn.warning("Execute not successful!")
			return SingleInstructionReturnStates.UnknownError
	
	#Return 0 for indication of no errors encountered
	return SingleInstructionReturnStates.NoErrorContinue

def run(filename, gui=True, 
		force_show_exceptions=False,time_runtime=False,
		DumpROM=True):
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
	
	#Handle logger
	lgn.getLogger().setLevel(LOGLEVEL)

	test_alu()
	
	#Reset CPU and initialise for execution
	reg(ReadWrite.WRITE, ProtReg.CONTROLUNITINPUT, RegType.PROTECTED, bz)
	single_instruction(reset=1)
	t = initialize_rom(filename)
	if t != 1:
		lgn.critical("Run: ROM couldn't be initialised properly.")
	if time_runtime:
		start_time = time.time()
	
	if DumpROM:
		dump_rom()
	
	#Execute program 
	while True:
		q = single_instruction(0, gui, force_show_exceptions)
		if q == SingleInstructionReturnStates.NoErrorExit:		#EXIT_SIGNAL
			if time_runtime:
				end_time = time.time()
				lgn.debug("elapsed time: %s" % (end_time-start_time))
				return [1, end_time-start_time]
			lgn.debug("Run: Program returned with exit code 1.")
			return 1
		elif q == SingleInstructionReturnStates.InvalidFunction:	#Error signal
			lgn.critical("Error: %s.run(): return code InvalidFunction, runtime stopped" % (__file__))
			raise Exception
		elif q == SingleInstructionReturnStates.UnknownError:	#Unknown error
			lgn.critical(q)
			raise Exception
