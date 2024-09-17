"""Assembler.py -> Updated assembler for Schön Core Alpha v.0.1.0

My own proprietary low level language for my CPU Schön Core Alpha v.0.1.0
Major non-user functions:

HandleSEI(bool, line, filename, used_in_escape) -> Handles if statements
getBinLine(lines, line, marks) -> Handles line indexing for assembled file
GetSEIClosingStatement(if_marks, ts) -> Handles if statement orders, able to handle nested if statements and if elif else statements
FindMarks(lines) -> Handles marks for absolute line ignorant jumping
GetVariableOrder(MainType: int, FuncNum: int, BVL: list, BVI: list, ReorderDict: dict) -> Handles variable ordering for easier conversion between assembly and machine instruction

Major user functions:

Assemble(filename: str, dest_name: str) -> Function to call for assembly of filename to dest_name, dest_name automatically apllies ".schonexe" postfix

"""

#Import libraries
import BaseCPUInfo
import importlib as il 
import math 
import BasicMath as bm
import logging as lgn			#Logging for custom exceptions
from enum import Enum			#Enum for elimination of magic numbers

#Initiating logging
LOGLEVEL = lgn.DEBUG
lgn.basicConfig(format="%(levelname)s: %(message)s", level=lgn.DEBUG)
lgn.getLogger().setLevel(LOGLEVEL)

#Get Basic Info about Simulated CPU and Folders
bw = BaseCPUInfo.bit_width
bf = BaseCPUInfo.base_folder
pf = BaseCPUInfo.programs_folder
exeff = BaseCPUInfo.executable_files_folder

class CustomException(Exception):
	pass

class IfNames(Enum):
	If = "branch"

class StandardFunctions(Enum):
	rom = "rom"
	ram = "ram"
	register = "reg"
	stack = "stack"
	interrupt = "interrupt"
	general_io = "io"
	call_subroutine = "call"

class ALUFunctions(Enum):
	alu_function = "compute"

class AbstractFunctions(Enum):
	mark = "mark"
	_else = "else"
	_elif = "elif"
	_pass = "pass"
	_def = "def"

class FunctionNames(Enum):
	If = IfNames
	Standard = StandardFunctions
	ALU = ALUFunctions
	Abstract = AbstractFunctions

class VariableTypes(Enum):
	integer = "int"
	float = "float"
	character = "char"
	string = "string"
	boolean = "bool"
	array = "array"
	list = "list"

alu_types = [

	"int",
	"float",
	"char",
	"string",
	"bool",
	"array",
	"list",

]

function_names = [
	[	"branch" ],
	[	"rom", "ram", "reg", "stack", "interrupt", "io", "call"],
	[	"compute" ],
	[	"mark",	"else",	"elif",	"pass", "def"],
]

branch_special_cases = [
	"pointer",
	"conditional",
]

sei = [ "{", "}", ]					#Start end indicator
tfn = [ "to", "from", ]				#To from names
#General purpose, alu, stack pointers, interrupt, special purpose
regs = ["gpr","alur","stk","spr"]	#Register names in order
define = "def"						#Keyword to define a function
eof = "eof"							#EOF indicator name

function_params = [
	[	#Setup special parameters, at the moment only if is implemeted, thus only the if operators
		[	["jump", ">", "==", ">=", "<", "!=", "<=", "weird", "co", ">c", "==c", ">=c", "<c", "!=c", "<=c"], ["pass"] ],
	],
	[	#Setup general function parameters, True=types of regs, False=to/from, None=nan (copy user input in general), "pass"=stop checking for parameters
		[	[True], [None], ["int","float","char","string","bool"], ["pass"] ],	#rom
		[	[False], [None], [True], [None], ["pass"] ],						#ram
		[	[True], [None], ["swap", "clone"], [True], [None],["pass"] ],		#reg
		[	["push","pop", "set", "get"],[True], [None], ["up", "down"] ],		#stack
		[	[True], [None], ["pass"] ],											#interrupt
		[	[False], [None], [True], [None],["pass"] ],							#io
		[	[None], [False], [None], ["pass"] ],													#call/return function
	],
	[	#Setup special device parameters (e.g. ALU)
		[	[True], [None], ["add","sub","mul","div","intdiv","or","xor","not","shift","","","","","","","compare"],[True],[None],[True],[None],["int", "float", "char", "string", "bool", "array", "list"], ["pass"] ],
	],
	[
		[	[None] ],
		[	["pass"] ],
		[	[True], [None], [">", "==", ">=", "<", "!=", "<=", "weird", "co", ">c", "==c", ">=c", "<c", "!=c", "<=c", "jump",], [True], [None] ],
		[	["pass"] ],
	],
]
#Amount of variables expected
function_var_amount = [
	[
		1
	],
	[
		3,
		3,
		5,
		3,
		2,
		4,
	],
	[
		[ 9 ],
	],
]

var_excp = [
	[	#Functions that need no variables
		sei[0],sei[1],eof,function_names[3][1],
	],
	[	#Functions that need only first variables
		# function_names[1][5],
		function_names[0][0],
		function_names[3][0],
		function_names[3][2],
		define
	],
]
#Get function parameter index
def GetParameterIndex( indx=[0,0,0], var="" ):
	temp_par = function_params[indx[0]][indx[1]][indx[2]][0]
	if temp_par == True:
		return regs.index( var )
	elif temp_par == False:
		return tfn.index( var )
	elif temp_par == None:
		return int( var )
	elif temp_par == "pass":
		return "pass"
	else:
		try:
			return function_params[indx[0]][indx[1]][indx[2]].index( var )
		except:
			return temp_par.index( var )
#Write to file exception
wtf_excp = [
	sei[0],
	sei[1],
	function_names[3][0],
	define,
	"",
]

#Function to manage if statements
def HandleSEI( line, lines, used_in_escape ):
	if used_in_escape == 1 and sei[1] in lines[line]:
		return False
	return True

def GetFunctionIndex(func_var):
	if func_var in function_names[1]:	#Check in function_names[1]
		return function_names[1].index( func_var )
	elif func_var in function_names[2]:	#Check in function_names[2]
		return function_names[2].index( func_var )
	else:								#Unknown function variable
		raise NameError

def getBinLine( lines, line_end, marks ):
	"""getBinLine(lines: list, line: int, marks: dict) -> Handles line indexing for assembled file
	Parameters:
	
	lines: list of lines to handle
	line: number of the line to compute to
	marks: dict of marks and if marks to take into consideration
	
	Returns: int of the binary line number post assembled
	"""
	
	#Length of binary lines for unusual lengths
	BinaryLenghts = {
		function_names[1][0]: 2,	#rom
		function_names[1][1]: 2,	#ram
		function_names[1][5]: 2,	#io
		function_names[3][0]: 0,	#mark
		function_names[3][1]: 1,	#else
		function_names[3][2]: 3,	#elif
		sei[1]: 0,
	}
	
	BinaryLineNumber = 0
	
	for i in range( line_end ):
		Line = lines[i].split()
		Function = Line.pop( 0 )
		if Function in BinaryLenghts:
			BinaryLineNumber += BinaryLenghts[Function]
		elif Function in marks:
			BinaryLineNumber += 2
		else:
			BinaryLineNumber += 1
	
	return BinaryLineNumber
	
#Function to manage if statement order
def GetSEIClosingStatement( marks, MarkIndex, IsIf=False ):
	if IsIf==False:
		#If there is zero marks left
		if len( marks[MarkIndex] ) == 0:
			return str( MarkIndex )
		
		MarkIndex = int( MarkIndex )
		for j, _ in enumerate( marks ):
			t = marks[str(MarkIndex-j)]
			if len( t ) == 0:
				return str( MarkIndex-j )
			
			iint = 1
			for i, _ in enumerate( t ):
				if t[str(i)]["0"] == 0:
					break
				elif iint == len( t ):
					return str( MarkIndex-j )
				iint += 1
		return "0"
	
	if len( marks[MarkIndex] ) == 0:
		return str( MarkIndex )
	
	MarkIndex = int( MarkIndex )
	for j, _ in enumerate( marks ):
		t = marks[str(MarkIndex-j)]
		if len( t ) == 0:
			return str( MarkIndex-j )
		
		iint = 1
		for i, _ in enumerate( t ):
			if t[str(i)]["0"] == 0:
				break
			elif iint == len( t ):
				return str( MarkIndex-j )
			iint += 1
	
	return str( 0 )

def FindMarks(lines: list):
	"""FindMarks(lines: list) -> Handles marks for absolute line ignorant jumping
	Parameters:
	
	lines: list of lines to handle
	
	Format of marks found:
	dict of line numbers where marks are found, where the key is the number of mark it is, and the value is the line number it's at
	example: {"0": 5, "1": 9, "2": 15}
	
	Format of if statements found:
	2d dict of information about if statements found, 
	the outer dict contains all if statements, the inner dict is the specific if statement.
	Information about the specific if statement is formatted by 
	
	key "0" is the type of function found,
	if it's:
	0 it's a closing curly bracket
	1 it's an else statement
	2 it's an elif statement
	
	key "1" is the line at which it's found
	
	Returns: dict if marks found, dict of if_marks found
	"""
	
	#Initialize working variables
	marks = dict()
	funcs = dict()
	funcs_names = dict()
	funcs
	if_marks = dict()
	vars = ["","","",""]
	iml = []
	
	#Search through lines
	for ln, line in enumerate(lines):
		func = line.split()
		
		try:
			func_var = func.pop( 0 )
		except AttributeError:
			raise CustomException("Error: ln %s, Schön Assembly does not allow white-space lines." % (ln+1))
		
		#func_snd and func_snd_var is next line's function and variables
		try:
			func_snd = lines[ln+1].split()
			func_snd_var = func_snd.pop( 0 )
		except IndexError:
			func_snd = None
			func_snd_var = None
		
		for i in range( 3 ):
			try:
				vars[i] = func.pop( 0 )
			except IndexError:
				vars[i] = None
		
		#Handle various functions
		if func_var == function_names[3][0]:
			marks[vars[0]] = ln
		elif func_var == define:
			lgn.debug("FindMarks: Found definition of function: %s" % (ln))
			lgn.debug("index: %s" % (len(funcs)))
			funcs[str(len(funcs))] = dict()
			funcs_names[vars[0]] = {"index" : len(funcs)}
		elif func_var == function_names[0][0] and func_snd_var != function_names[3][0] and func_snd_var != function_names[3][1] and vars[0] != "jump":
			if_marks[ str( len( if_marks ) ) ] = dict()
		elif func_var == function_names[3][1]:
			ts = str( len( if_marks ) - 1 )
			ts = GetSEIClosingStatement( if_marks, ts )
			tss = str( len( if_marks[ ts ] ) )
			lines[ln] = function_names[3][1] + " # " + str( ts ) + " " + str( tss )
			if_marks[ ts ][tss] = {'0': 1, '1': ln}
		elif func_var == function_names[3][2]:
			ts = str( len( if_marks ) - 1 )
			ts = GetSEIClosingStatement( if_marks, ts )
			tss = str( len( if_marks[ ts ] ) )
			if vars[1] != None:
				lines[ln] = function_names[3][2] + " " + str( vars[0] ) + " " + str( vars[1] ) + " " + str( vars[2] ) + " # " + str( ts ) + " " + str( tss )
			else:
				lines[ln] = function_names[3][2] + " " + str( vars[0] ) + " # " + str( ts ) + " " + str( tss )
			if_marks[ ts ][tss] = {'0': 2, '1': ln}
		elif func_var == sei[1] and func_snd_var != function_names[3][1] and func_snd_var != function_names[3][2]:
			ts = str( len( if_marks ) - 1 )
			try:
				ts = GetSEIClosingStatement( if_marks, ts )
				tss = str( len( if_marks[ ts ] ) )
			except KeyError:
				lgn.debug("Probably func:")
				lgn.debug("funcs: %s" % (funcs))
				ts = str( len( funcs ) - 1)
				ts = GetSEIClosingStatement( funcs, ts, True )
				tss = str( len( funcs[ts] ) )
				funcs[ ts ][tss] = {'0': 0, '1': ln}
		
		ln += 1
	
	return marks, if_marks, funcs, funcs_names

def GetVariableType( var ):
	if var == "0b" + var[2:]:
		return "bin"
	elif var == "0x" + var[2:]:
		return "hex"
	
	try:
		tuv = int( var )
		return "int"
	except ValueError:
		return "other"

def GetVariableOrder(MainType: int, FuncNum: int, BVL: list, BVI: list, ReorderDict: dict):
	QBVL = []	#Binary variable length
	QBVI = []	#Binary variable index
	
	for i, _ in enumerate(BVL):	#Reorder variables and indecies according to the ReorderDict
		lgn.debug("BVL: i: %s, e: %s" % (i, _))
		QBVL.append(BVL[ReorderDict[MainType][FuncNum][i]])
		QBVI.append(BVI[ReorderDict[MainType][FuncNum][i]])
	
	return QBVL, QBVI

def GetEscapeFromInscape(lines, starting_line, starting_bin_line, il, marks):
	ln_n = starting_line
	il += 1
	rel_ln = 1
	used_in_escape = 1
	bin_ln = starting_bin_line
	
	try:
		temp_unused_var = lines[ln_n + rel_ln]
	except Exception:
		lgn.critical( "Error: ln %s: Expected if inscape, got none" % (str( ln_n + 1 )) )
		return -1
	rel_rel_ln = 1
	
	#If binary lines 
	iblns = {
		function_names[1][0]: 2,
		function_names[1][1]: 2,
		function_names[1][5]: 2,
		function_names[3][0]: 0
	}
	while HandleSEI( ln_n + 1 + rel_rel_ln, lines, used_in_escape ):
		try:
			temp_unused_var = lines[ln_n + rel_ln + rel_rel_ln].split()
			temp_func = temp_unused_var.pop( 0 )
			try:
				temp_temp_unused_var = lines[ln_n + rel_ln + rel_rel_ln + 2].split()
				temp_temp_func = temp_temp_unused_var.pop( 0 )
			except:
				temp_temp_func = ""
			if temp_func in iblns:
				bin_rel_ln += iblns[temp_func]
			elif temp_func == sei[0]:
				used_in_escape += 1
				bin_rel_ln += 1
			elif temp_func == sei[1] and used_in_escape > 1:
				used_in_escape -= 1
			elif temp_func in marks:
				bin_rel_ln += 2
			else:
				bin_rel_ln += 1
			rel_rel_ln += 1
			try:
				temp_unused_var = lines[ln_n + 1 + rel_rel_ln]
			except:
				lgn.critical("If: Error: ln: %s: Expected if escape, got none, 0" % (ln_n + 1))
				return -1, -1
		except:
			lgn.critical("If: Error: ln: %s: Expected if escape, got none, 1" % (ln_n + 1))
			return -1, -1
	if temp_temp_func == function_names[3][1] or temp_temp_func == function_names[3][2]:
		bin_rel_ln += 2

	return bin_ln + 2 + bin_rel_ln, il

def FindSubroutines(lines):
	SubroutineNames = []
	SubroutineBinaryLineIndecies = []

	for ln_n, line in enumerate(lines):

		split_line = line.split()
		func_var = split_line.pop(0)

		try:
			nextLine = lines[ln_n+1].split()
			nextLineFunc = nextLine.pop(0)
		except IndexError:
			pass
	
	return SubroutineNames, SubroutineBinaryLineIndecies

def Assemble( filename: str, dest_name: str ):
	"""Assemble(filename: str, dest_name: str) -> Function to call for assembly of filename to dest_name, dest_name automatically apllies ".schonexe" postfix
	Parameters:
	
	filename: name of file with path relative to the folder of the file unless specified so
	dest_name: name of file for destination, ".schonexe" postfix is automatically applied
	
	Returns: file with name (dest_name).schonexe
	"""
	
	lgn.getLogger().setLevel(LOGLEVEL)
	
	#Open and read file to assemble
	fh = open( bf + pf + filename )
	lines = fh.readlines()
	fh.close()
	fh = open( bf + exeff + dest_name + ".schonexe1", "w+" )
	
	#Basic variable initiation
	ln_n = 0		#Line number
	bin_ln = 0		#Binary line number
	il = 0			#If length
	marks, if_marks, funcs, funcs_names = FindMarks( lines )
	eofln = 0		#End Of File Line
	
	lgn.info("%s%s.py: Schön Core Alpha v.0.1.0 Assembler." % (bf, __name__))
	lgn.info("Assembling: %s" % (bf + pf + filename))
	
	ReorderDict = {											#Dict for reordering variables
	
		0: {	#If statements
		
				0: [0,1,2,3,4,5,6,7],				#Weird problems with more than expected regs copied, hacked to ignore them
		
			},
		1: {	#Standard functions
		
				0: [4,3,0,1,2,5,6,7],	#rom
				1: [1,0,2,3,4,5,6,7],	#ram
				2: [2,3,1,4,5,6,7,0],	#reg
				3: [0,2,3,1,4,5,6,7],	#stack
				4: [0,1,2,3,4,5,6,7],	#interrupt
				5: [0,1,2,3,4,5,6,7],	#io
				
			},
		2: {	#ALU functions
		
				0: [2,3,0,4,5,6,7,1],
		
			},
	
	}
	
	#Static binary variable lengths and placements
	_StaticBinVarLength_ = [ 4, 2, 2, 5, 2, 5, 2, 5 ]
	_StaticBinVarIndex_ = [ 5, 9, 11, 13, 18, 20, 25, 27 ]
	
	#Get eof line
	for i in lines:
		if eof in i:
			break 
		eofln += 1
	
	SubroutineNames, SubroutineLineIndecies = FindSubroutines(lines)

	lgn.debug( "EOL: " + str( eofln ) )
	lgn.debug( "Subroutines: %s" % (SubroutineNames))
	lgn.debug( "IF_MARKS: " )
	lgn.debug( if_marks )

	#Main loop for assembling
	while ln_n < len( lines ):
		lgn.debug("ln_n: %s" % (str(ln_n)))
		line = lines[ln_n].split()
		func_var = line.pop( 0 )

		try:
			sline = lines[ln_n+1].split()
			sfunc_var = sline.pop( 0 )
		except IndexError:
			sfunc_var = None
		
		full_binary_function = [0 for i in range( bw )]
		nextLines = [None,None,None]
		vars = ["" for i in range(10)]
		t = lines[ln_n]
		tt = GetVariableType( t )

		if tt == "bin":
			lines[ln_n] = str( bm.btd([int(i) for i in t[2:]]) )
		elif tt == "hex":
			lines[ln_n] = str( bm.htd( t[2:] ) )
		elif tt == "int":
			pass
		else:
			if func_var not in var_excp[0] and func_var not in marks:
				try:
					vars[0] = line.pop( 0 )
				except IndexError:
					print( "Error: ln " + str(ln_n + 1) + ", Variable one missing" )
					return -1
				vars[2] = ""
				if func_var not in var_excp[1]:
					try:
						vars[1] = line.pop( 0 )
					except IndexError:
						if func_var == function_names[0][0] and vars[0] == jump_name:
							pass
						else:
							print( "Error: ln " + str(ln_n + 1) + ", Variable two missing" )
							return -1
					if func_var in sei:
						vars[2], vars[3] = ("",)*2
					for i in range( 2, 8 ):
						try:
							vars[i] = line.pop( 0 )
						except IndexError:
							break
			iint = 0
			for i in vars:
				try:
					t = vars[iint][2:]
					tt = GetVariableType( vars[iint] )
					if tt == "bin":
						vars[iint] = str( bm.btd([int(i) for i in t]) )
					elif tt == "hex":
						vars[iint] = str( bm.htd(t) )
				except:
					pass
				iint += 1
		
		bin_rel_ln = 0
		
		if func_var == eof:
			full_binary_function = bm.dtb( -1 )
		elif func_var == FunctionNames.If.value.If.value:
			if vars[0] not in branch_special_cases:	#branch
				nextLines[0] = str(vars[1])
			elif vars[0] == branch_special_cases[0]:	#branch pointer
				full_binary_function[8] = 1
				nextLines[0] = str(vars[1])
			elif vars[0] == branch_special_cases[1]:	#conditional
				full_binary_function[7] = 1
				try:
					nextLines[0] = bm.dtb( getBinLine( lines, int( lines[ln_n+1] ), marks ) )
				except:
					lgn.critical("Jump: Error: ln %s: Invalid jump counter" % (ln_n + 1))
					raise Exception
				ln_n += 1
			else:									#IF
				IfEscape, il = GetEscapeFromInscape(lines, ln_n, bin_ln, il, marks)
				
				full_binary_function[0:4] = [0,0,1,0]
				nextLines[0] = bm.dtb( IfEscape )
				
				#Get reference binary variable lenght and indexes
				bvl = _StaticBinVarLength_.copy()
				bvi = _StaticBinVarIndex_.copy()
				
				MainType = None
				for i, _ in enumerate(function_names):
					if func_var in function_names[i]:
						MainType = i
						break
				if MainType == None:
					raise NameError
				
				function_names_index = function_names[MainType].index(func_var)
					
				bvl, bvi = GetVariableOrder(
					MainType, 
					function_names[MainType].index(func_var),
					bvl,
					bvi,
					ReorderDict
				)
				
				bin_vars = []
				for i in range(function_var_amount[MainType][function_names_index]):
					try:
						temp_type = function_params[MainType][function_names_index][i][0]
						if temp_func == "pass":
							break
					except Exception:
						break
					try:
						bin_vars.append(bm.dtb( GetParameterIndex( [MainType,function_names_index,i], vars[i] ), bvl[i] ))
					except Exception:
						lgn.critical("If: Error: ln: %s: Incorrect variable input" % (ln_n + 1))
						raise Exception

				for i, e in enumerate(bin_vars):
					for j, _ in enumerate( e ):
						full_binary_function[bvi[i] + j] = e[j]
		elif func_var in marks:
			full_binary_function[0:4] = [0,0,1,0]
			full_binary_function[5:9] = [1,1,1,0]
			full_binary_function[9:11] = [1,0]
			bin_rel_ln = getBinLine( lines, marks[func_var], marks )
			nextLines[0] = bm.dtb( bin_rel_ln )
		elif func_var == FunctionNames.Standard.value.rom.value:
			full_binary_function[0:4] = [0,0,0,0]
			full_binary_function[12:13] = bm.dtb(regs.index(vars[0]), 2)
			full_binary_function[13:19] = bm.dtb(int(vars[1]), 5)
			try:
				if vars[3] == "float":
					nextLines[0] = bm.user_dtb(float(vars[2]))
				elif vars[3] == "char":
					temporary = lines[ln_n]
					nextLines[0] = bm.user_ctb(bm.unwrap_char(bm.find_char_in_string_line(temporary)))
				elif vars[4] == "char":
					temporary = lines[ln_n]
					nextLines[0] = bm.user_ctb(bm.unwrap_char(bm.find_char_in_string_line(temporary)))
				else:
					nextLines[0] = bm.dtb(int(vars[2]))
			except Exception:
				nextLines[0] = bm.dtb(int(vars[2]))
		elif func_var == FunctionNames.Standard.value.ram.value:
			full_binary_function[0:4] = [1,0,0,0]
			if vars[0] == "to":
				full_binary_function[9:11] = [0,1]
			else:
				full_binary_function[9:11] = [0,0]
			full_binary_function[12:13] = bm.dtb(regs.index(vars[2]), 2)
			full_binary_function[13:19] = bm.dtb(int(vars[3]), 5)
			nextLines[0] = bm.dtb(int(vars[1]))
		elif func_var == FunctionNames.Standard.value.general_io.value:
			full_binary_function[0:4] = [0,1,1,0]
			if vars[0] == "from":
				full_binary_function[5:9] = [0,0,0,0]
			else:
				full_binary_function[5:9] = [0,1,0,0]
			full_binary_function[12:13] = bm.dtb(regs.index(vars[2]), 2)
			full_binary_function[13:19] = bm.dtb(int(vars[3]), 5)
			nextLines[0] = bm.dtb(int(vars[1]))
		elif func_var == FunctionNames.Abstract.value._else.value:
			full_binary_function[5] = 1
			nextLines[0] = None
			t = if_marks[ str( il - 1 ) ]
			for i, _ in enumerate(t):
				if t[str(i)]["0"] == 0:
					nextLines[0] = bm.dtb( getBinLine( lines, t[str(i)]["1"], marks ) )
					break
			if nextLines[0] == None:
				raise CustomException("Error: ln %s: if statement was not encoded right, 0" % (ln_n + 1))
		elif func_var == FunctionNames.Abstract.value._elif.value:
			full_binary_function = [0 for i in range( bw )]
			t_bin_vars[0] = bm.dtb( GetParameterIndex( [0,0,0],vars[0] ) + 1 )
			nextLines[0] = None
			nextLines[1] = [0 for i in range( bw )]
			for i in range( 4 ):
				nextLines[1][i+5] = t_bin_vars[0][i]
			nextLines[2] = None
			t = if_marks[ str( il - 1 ) ]
			for i in range( len( t ) ):
				if t[str(i)]["0"]  == 0:
					nextLines[0] = bm.dtb( getBinLine( lines, t[str(i)]["1"], marks ) )
					break
			for i in range( len( t ) ):
				if t[str(i)]["1"]  == ln_n:
					tn = i
					break
			try:
				tnn = t[str(tn+1)]["0"]
			except:
				tnn = None
			if tnn == None:
				nextLines[2] = nextLines[0]
			else:
				if tnn == 0:
					nextLines[2] = bm.dtb( getBinLine( lines, t[str(tn+1)]["1"], marks ) )
				elif tnn == 1 or tnn == 2:
					nextLines[2] = bm.dtb( getBinLine( lines, t[str(tn+1)]["1"] + 2, marks ) )
			if nextLines[0] == None:
				raise CustomException("Error: ln %s: if statement was not encoded right, 1" % (ln_n + 1))
		elif func_var == FunctionNames.Abstract.value._def.value:
			pass
		elif func_var == sei[1] and sfunc_var != function_names[3][1] and sfunc_var != function_names[3][2] and sfunc_var in funcs_names:
			il -= 1
		elif func_var in sei or func_var == function_names[3][0] or func_var == "":
			pass
		else:
			t = GetVariableType( lines[ln_n] )
			tt = lines[ln_n].rstrip()
			if t == "bin":
				full_binary_function = bm.dtb(bm.btd([int(i) for i in tt[2:]]))
			elif t == "hex":
				full_binary_function = bm.dtb(bm.htd(tt[2:]))
			elif t == "int":
				full_binary_function = bm.dtb(int( tt ))
			else:
				func_num = GetFunctionIndex( func_var )				#Logical function number
				f_func_num = func_num
				try:
					bin_func = bm.dtb( func_num, 4 )				#Function number converted to binary
				except NameError:
					raise CustomException("Error: ln %s, invalid function number or name" % (ln_n + 1))
				except Exception:
					#Most probably incorrect function name
					raise CustomException("Error: ln %s, error in parsing function number or name" % (ln_n + 1))
				
				#Get reference binary variable lenght and indexes
				bvl = _StaticBinVarLength_.copy()
				bvi = _StaticBinVarIndex_.copy()
				
				#Get type of variables
				MainType = None
				for i, _ in enumerate(function_names):
					if func_var in function_names[i]:
						MainType = i
						break
				if MainType == None:
					raise NameError
				
				#Get variable order
				bvl, bvi = GetVariableOrder(
					MainType, 
					function_names[MainType].index(func_var),
					bvl,
					bvi,
					ReorderDict
				)
				
				#Initiate binary versions of variables
				bin_vars = []
				for j, e in enumerate( zip(bvl,bvi) ):
					bin_vars.append( [0 for k in range( bvl[j] )] )
				
				if func_var == FunctionNames.ALU.value.alu_function.value:
					is_alu = 1
					try:
						bin_func = bm.dtb( GetParameterIndex( [2,0,2], vars[2] ), 4 )
					except ValueError:
						lgn.critical("Compute: ln %s: Error, invalid variables." % (ln_n + 1))
						return -1
					
					if vars[0] == function_params[2][0][2][8]:
						bin_vars[0] = bm.dtb( 1, bvl[0] )
					
					#Convert variables to binary versions
					for i, _ in enumerate(bin_vars):
						if i == 7:
							# try:
							if vars[7] in alu_types:
								lgn.debug("Type: %s" % (alu_types.index(vars[7])))
								bin_vars[2] = bm.dtb(alu_types.index(vars[7]), 4)
								break
							# except Exception:
							# 	break
						if GetParameterIndex( [2,0,i], vars[i] ) == "pass":
							break
						else:
							bin_vars[i] = bm.dtb( GetParameterIndex( [2,0,i], vars[i] ), bvl[i] )
				else:
					is_alu = 0
					function_names_index = function_names[MainType].index( func_var )
					for i in range(function_var_amount[1][function_names_index]):
						temp_type = function_params[MainType][f_func_num][i][0]
						bin_vars[i] = bm.dtb( GetParameterIndex( [MainType,function_names_index,i], vars[i] ), bvl[i] )
						if bin_vars[i] == "pass":
							bin_vars[i] = None
							break
						if func_var == function_names[1][0]:
							nextLines[0] = bm.dtb( int(vars[2]) )
						elif func_var == function_names[1][1]:
							try:
								nextLines[0] = bm.dtb( int( vars[3] ) )
							except Exception:
								raise CustomException("Error: ln %s: 4th variable missing." % (ln_n + 1))
						elif func_var == define:
							ln_n += 1
				
				full_binary_function[4] = is_alu
				
				for i, _ in enumerate(bin_func):
					full_binary_function[i] = bin_func[i]
				for i, e in enumerate(bin_vars):
					lgn.debug("Bin vars i: %s" % (i))
					for j, _ in enumerate( e ):
						lgn.debug("Bin vars: j=%s" % (j))
						full_binary_function[bvi[i] + j] = e[j]
				
				if func_var == function_names[2][0]:
					if vars[6] == "float":
						full_binary_function[10] = 1
						vars[8] = None
		
		if func_var not in wtf_excp:
			fh.write( bm.BinaryListToString( full_binary_function ) + "\n" )
			bin_ln += 1
			for i, _ in enumerate( nextLines ):
				if isinstance( nextLines[i], list ):
					fh.write( bm.BinaryListToString( nextLines[i] ) + "\n" )
					bin_ln += 1
		ln_n += 1
	
	fh.close()
	lgn.info("Assembler: Finished assembling.")
	return 1
