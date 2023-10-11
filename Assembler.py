"""uc.py -> Updated assembler for Schön Core Delta v.0.5.0

My own proprietary low level language for my CPU Schön Core Delta v.0.5.0
Major non-user functions:

inline(bool, line, filename, used_in_escape) -> Handles if statements
getBinLine(lines, line, marks) -> Handles line indexing for assembled file
gin(if_marks, ts) -> Handles if statement orders, able to handle nested if statements and if elif else statements
find_marks(lines) -> Handles marks for absolute line ignorant jumping
get_var_order(MainType: int, FuncNum: int, BVL: list, BVI: list, ReorderDict: dict) -> Handles variable ordering for easier conversion between assembly and machine instruction

Major user functions:

comp(filename: str, dest_name: str) -> Function to call for assembly of filename to dest_name, dest_name automatically apllies ".schonexe" postfix

"""

#Schön Assembler for Schön Core Delta v.0.5.0


import basecpuinf

import importlib as il 
import math 
import bm 

##########################################################
#Show advanced infomation
#To show advanced info, set variable to "yes"
#Otherwise set it to "no"
##########################################################
show_adv_inf = "no"

#Get Basic Info about Simulated CPU and Folders
bw = basecpuinf.bit_width
bf = basecpuinf.base_folder
pf = basecpuinf.programs_folder
exeff = basecpuinf.executable_files_folder

class CustomException(Exception):
	pass

function_names = [
	[	"if", "irar", ],
	[	"rom", "ram", "reg", "io", "gbl", "rar", ],
	[	"compute" ],
	[	"mark",	"else",	"elif",	"pass", ],
]
#Start end indicator
sei = [ "{", "}", ]
#To from names
tfn = [ "to", "from", ]
#Register names in order
#General purpose, alu, stack pointers, interrupt, special purpose
regs = ["gpr","alur","stk","itr","spr"]
#Jump name
jump_name = "jump"

function_params = [
	[	#Setup special parameters, at the moment only if is implemeted, thus only the if operators
		[	[True], [None], ["jump", ">", "==", ">=", "<", "!=", "<=", "weird", "co", ">c", "==c", ">=c", "<c", "!=c", "<=c"], [True], [None] ],
		[	[True], [None], ["pass"] ],
	],
	[	#Setup general function parameters, True=types of regs, False=to/from, None=nan (copy user input in general), "pass"=stop checking for parameters
		[	[True], [None], ["pass"] ],								#rom
		[	[False],[True], [None], ["pass"] ],						#ram
		[	[True], [None], [False], [True], [None],["pass"] ],		#reg
		[	["input","output"],[True], [None], ["pass"] ],			#io
		[	[True], [None], ["pass"] ],								#gbl
		[	[False], [True], [None], [True], [None],["pass"] ],		#rar
	],
	[	#Setup special device parameters (e.g. ALU)
		[	[True], [None], ["add","sub","mul","div","and","or","xor","not","shift","","","","","","","compare"],[True],[None],[True],[None],["pass"] ],
	],
	[
		[	[None] ],
		[	["pass"] ],
		[	[True], [None], [">", "==", ">=", "<", "!=", "<=", "weird", "co", ">c", "==c", ">=c", "<c", "!=c", "<=c", "jump",], [True], [None] ],
		[	["pass"] ],
	],
]
#Function parameter offset for skipped variables
function_param_offset = [
	[
		0, 0,
	],
	[
		1, 0, 0, 0, 0, 0,
	],
	[
		0,
	],
]
#Amount of variables expected
function_var_amount = [
	[
		5,
		1,
	],
	[
		2,
		3,
		5,
		3,
		2,
		5,
	],
	[
		[ 7 ],
	],
]
#EOF indicator name
eof = "eof"

var_excp = [
	[	#Functions that need no variables
		sei[0],sei[1],eof,function_names[3][1],
	],
	[	#Functions that need only first variables
		function_names[1][5],
		function_names[3][0],
		function_names[3][2],
	],
]
#Get function parameter index
def getParIndex( indx=[0,0,0], var="" ):
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
	"",
]
#Function to manage if statements
def inline( bool, line, filename, used_in_escape ):
	fh = open( bf + pf + filename, "r" )
	lines = fh.readlines()
	fh.close()
	if bool:
		if used_in_escape == 1 and sei[1] in lines[line]:
			return False
		else:
			return True
	else:
		if sei[0] in lines[line]:
			return False
		else:
			return True

def getFuncNum( func_var, bool=False ):
	if bool == False:
		m = 1
	else:
		m = 0
	if func_var in function_names[1]:
		return function_names[1].index( func_var ) + 1 * m
	elif func_var in function_names[2]:
		return function_names[2].index( func_var ) + 15 * m
	else:
		return NameError

def getBinLine( lines, line, marks ):
	"""getBinLine(lines: list, line: int, marks: dict) -> Handles line indexing for assembled file
	Parameters:
	
	lines: list of lines to handle
	line: number of the line to compute to
	marks: dict of marks and if marks to take into consideration
	
	Returns: int of the binary line number post assembled
	"""
	blns = {	#Length of binary lines
		function_names[1][0]: 2,	#rom
		function_names[1][1]: 2,	#ram
		function_names[3][0]: 0,	#mark
		function_names[3][1]: 1,	#else
		function_names[3][2]: 3,	#elif
		sei[1]: 0,
	}
	l = 0
	bin_rel_ln = 0
	for i in range( line ):
		gblln = lines[l].split()
		gblf = gblln.pop( 0 )
		if gblf in blns:
			bin_rel_ln += blns[gblf]
		elif gblf in marks:
			bin_rel_ln += 2
		else:
			bin_rel_ln += 1
		l += 1
	return bin_rel_ln
	
#Function to manage if statement order
def gin( if_marks, ts ):
	if len( if_marks[ts] ) == 0:
		return str( ts )
	else:
		ts = int( ts )
		for j, _ in enumerate( if_marks ):
			t = if_marks[str(ts-j)]
			if len( t ) == 0:
				return str( ts-j )
			else:
				iint = 1
				for i, _ in enumerate( t ):
					if t[str(i)]["0"] == 0:
						break
					elif iint == len( t ):
						return str( ts-j )
					iint += 1
	return str( 0 )

def find_marks(lines: list):
	"""find_marks(lines: list) -> Handles marks for absolute line ignorant jumping
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
	marks = dict()
	if_marks = dict()
	vars = ["","","",""]
	iml = []
	for ln, line in enumerate(lines):
		func = line.split()
		try:
			func_snd = lines[ln+1].split()
			func_snd_var = func_snd.pop( 0 )
		except:
			func_snd = None
			func_snd_var = None
		try:
			func_var = func.pop( 0 )
		except Exception:
			raise CustomException("Error: ln %s, Schön Assembly does not allow white-space lines." % (ln+1))
		for i in range( 3 ):
			try:
				vars[i] = func.pop( 0 )
			except:
				vars[i] = None
		if func_var == function_names[3][0]:
			marks[vars[0]] = ln 
		elif func_var == function_names[0][0] and func_snd_var != function_names[3][0] and func_snd_var != function_names[3][1] and vars[0] != "jump":
			if_marks[ str( len( if_marks ) ) ] = dict()
		elif func_var == function_names[3][1]:
			ts = str( len( if_marks ) - 1 )
			ts = gin( if_marks, ts )
			tss = str( len( if_marks[ ts ] ) )
			lines[ln] = function_names[3][1] + " # " + str( ts ) + " " + str( tss )
			if_marks[ ts ][tss] = {'0': 1, '1': ln}
		elif func_var == function_names[3][2]:
			ts = str( len( if_marks ) - 1 )
			ts = gin( if_marks, ts )
			tss = str( len( if_marks[ ts ] ) )
			if vars[1] != None:
				lines[ln] = function_names[3][2] + " " + str( vars[0] ) + " " + str( vars[1] ) + " " + str( vars[2] ) + " # " + str( ts ) + " " + str( tss )
			else:
				lines[ln] = function_names[3][2] + " " + str( vars[0] ) + " # " + str( ts ) + " " + str( tss )
			if_marks[ ts ][tss] = {'0': 2, '1': ln}
		elif func_var == sei[1] and func_snd_var != function_names[3][1] and func_snd_var != function_names[3][2]:
			ts = str( len( if_marks ) - 1 )
			ts = gin( if_marks, ts )
			tss = str( len( if_marks[ ts ] ) )
			if_marks[ ts ][tss] = {'0': 0, '1': ln}
		ln += 1
	return marks, if_marks

#Test For Binary Or Hexadicmal
def tfbh( var ):
	if var == "0b" + var[2:]:
		return False
	elif var == "0x" + var[2:]:
		return False
	else:
		return True

#Get Variable Type
def gvt( var ):
	if var == "0b" + var[2:]:
		return "bin"
	elif var == "0x" + var[2:]:
		return "hex"
	else:
		try:
			tuv = int( var )
			return "int"
		except:
			return "other"

def get_var_order(MainType: int, FuncNum: int, BVL: list, BVI: list, ReorderDict: dict):
	QBVL = []	#Binary variable length
	QBVI = []	#Binary variable index
	
	for i, _ in enumerate(BVL):	#Reorder variables and indecies according to the ReorderDict
		QBVL.append(BVL[ReorderDict[MainType][FuncNum][i]])
		QBVI.append(BVI[ReorderDict[MainType][FuncNum][i]])
	
	return QBVL, QBVI

def create_full_binary_function(bin_vars: list, bvi: list, bvl: list, full_binary_function: list = None):
	#If full_binary_function isn't predefined initialize it to an empty word
	if full_binary_function == None:
		full_binary_function = [0 for i in range(bw)]
	
	#Populate full_binary_function with binary vars based on binary variable index and lenghts
	for i, _ in enumerate(bin_vars):
		for j, _ in enumerate(bin_vars[i]):
			full_binary_function[bvi[i] + j] = bin_vars[i][j]
	
	return full_binary_function

def init_bin_vars(bvi: list, bvl: list):
	#Initialize bin_vars
	bin_vars = []
	
	#Populate bin_vars
	for j, e in enumerate( zip(bvl,bvi) ):
		bin_vars.append( [0 for k in range( bvl[j] )] )
	
	return bin_vars

def _GetBinLine_(filename: str, ln: int):
	fh = open(bf + pf + filename)
	lines = fh.readlines()
	fh.close()
	
	marks, if_marks = find_marks(lines)
	
	return getBinLine(lines, ln, marks)

def comp( filename: str, dest_name: str ):
	"""comp(filename: str, dest_name: str) -> Function to call for assembly of filename to dest_name, dest_name automatically apllies ".schonexe" postfix
	Parameters:
	
	filename: name of file with path relative to the folder of the file unless specified so
	dest_name: name of file for destination, ".schonexe" postfix is automatically applied
	
	Returns: file with name (dest_name).schonexe
	"""
	fh = open( bf + pf + filename )
	lines = fh.readlines()
	fh.close()
	fh = open( bf + exeff + dest_name + ".schonexe5", "w+" )
	ln_n = 0		#Line number
	bin_ln = 0		#Binary line number
	il = 0			#If length
	ignore_ln = []	#Lines to ignore
	marks, if_marks = find_marks( lines )
	eofln = 0		#End Of File Line
	
	print("\n\n%s%s.py: %s" % (bf, __name__, bf + pf + filename))
	
	ReorderDict = {											#Dict for reordering variables
	
		0: {
		
				0: [5,6,2,7,8,0,1,3,4,9,10],				#Weird problems with more than expected regs copied, hacked to ignore them
				1: [0,1,2,3,4,5,6,7,8,9,10],
		
			},
		1: {
		
				0: [5,6,2,3,4,0,1,7,8,9,10],
				1: [0,5,6,2,3,1,4,7,8,9,10],
				2: [5,6,0,7,8,1,2,3,4,9,10],
				3: [0,5,6,3,4,1,2,7,8,9,10],
				4: [0,1,2,3,4,5,6,7,8,9,10],
				5: [5,6,0,7,8,1,2,3,4,9,10],
		
			},
		2: {
		
				0: [5,6,2,7,8,9,10,0,1,3,4],
		
			},
	
	}
	#|var a| |var b| |var d/c| |var d/c| |var e/c| |var e/c|
	_StaticBinVarLength_ = [ 1,1,4,2,2, 2, 5, 2, 5, 2, 5 ]
	_StaticBinVarIndex_ = [ 5,6,7,7,9,11,13,18,20,25,27 ]
	
	for i in lines:
		if eof in i:
			break 
		eofln += 1
	if show_adv_inf == "yes":
		print( "EOL: " + str( eofln ) )
		print( "IF_MARKS: " )
		print( if_marks )
	eofbln = getBinLine( lines, eofln, marks )
	while ln_n < len( lines ):
		if show_adv_inf == "yes":
			print( "ln_n: " + str( ln_n ) )
		line = lines[ln_n].split()
		func_var = line.pop( 0 )
		try:
			sline = lines[ln_n+1].split()
			sfunc_var = sline.pop( 0 )
		except:
			sfunc_var = None
		full_binary_function = [0 for i in range( bw )]
		nextLines = [None,None,None]
		vars = ["" for i in range(10)]
		t = lines[ln_n]
		tt = gvt( t )
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
				except:
					print( "Error: ln " + str(ln_n + 1) + ", Variable one missing" )
					return -1
				vars[2] = ""
				if func_var not in var_excp[1]:
					try:
						vars[1] = line.pop( 0 )
					except:
						if func_var == function_names[0][0] and vars[0] == jump_name:
							pass
						else:
							print( "Error: ln " + str(ln_n + 1) + ", Variable two missing" )
							return -1
					if func_var in sei:
						vars[2], vars[3] = ("",)*2
					for i in range( 2, 7 ):
						try:
							vars[i] = line.pop( 0 )
						except:
							break
			iint = 0
			for i in vars:
				try:
					t = vars[iint][2:]
					tt = gvt( vars[iint] )
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
		elif func_var == function_names[0][0]:
			if vars[0] == jump_name:	#JUMP
				full_binary_function[5] = 1
				try:
					nextLines[0] = bm.dtb( getBinLine( lines, int( lines[ln_n+1] ), marks ) )
				except:
					raise CustomException( "Error: ln %s: Invalid jump counter" % (ln_n + 1))
				ln_n += 1
			else:									#IF
				il += 1
				rel_ln = 1
				used_in_escape = 1
				
				
				
				try:
					temp_unused_var = lines[ln_n + rel_ln]
				except Exception:
					print( "Error: ln " + str( ln_n + 1 ) +": Expected if inscape, got none" )
					return -1
				rel_rel_ln = 1
				iblns = {
					function_names[1][0]: 2,
					function_names[1][1]: 2,
					function_names[3][0]: 0
				}
				while inline( True, ln_n + 1 + rel_rel_ln, filename, used_in_escape ):
					try:
						temp_unused_var = lines[ln_n + rel_ln + rel_rel_ln].split()
						temp_func = temp_unused_var.pop( 0 )
						try:
							temp_var = temp_unused_var.pop( 0 )
						except:
							temp_var = ""
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
							raise CustomException( "Error: ln %s: Expected if escape, got none, 0" % (ln_n + 1))
					except:
						raise CustomException( "Error: ln %s: Expected if escape, got none, 0" % (ln_n + 1))
				if temp_temp_func == function_names[3][1] or temp_temp_func == function_names[3][2]:
					bin_rel_ln += 2
				nextLines[0] = bm.dtb( bin_ln + 2 + bin_rel_ln )
				
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
					
				bvl, bvi = get_var_order(
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
						# pass
					# fpo = function_param_offset[1][function_names_index]
					#bin_vars[fpo + i] = bm.dtb( getParIndex( [1,function_names_index,i], vars[i] ), bvl[i + fpo] )
					# print(vars[i])
					try:
						bin_vars.append(bm.dtb( getParIndex( [MainType,function_names_index,i], vars[i] ), bvl[i] ))
					except Exception:
						raise CustomException("Error: ln %s, Incorrect variable input" % (ln_n + 1))
				# print("IF:")
				tbvi = _StaticBinVarIndex_.copy()
				tbvl = _StaticBinVarLength_.copy()
				skip_smaller_vars = False
				t = tbvi.index(7)
				ti = 0
				
				if tbvl[t] == 4:
					ti = t
				else:
					tbvi.pop(t)
					tbvl.pop(t)
					t = tbvi.index(7)
					if tbvl[t] == 4:
						ti = t
					else:
						raise CustomException("Error: ln %s, Unable to format bin_vars properly.")

				if bin_vars[ti] != [0 for i in range(4)]:
					skip_smaller_vars = True
				
				for i, e in enumerate(bin_vars):
					if (bvi[i] == 7 and skip_smaller_vars and i != ti or 
						bvi[i] == 9 and skip_smaller_vars):
						pass
					else:
						for j, _ in enumerate( e ):
							full_binary_function[bvi[i] + j] = e[j]
		elif func_var in marks:
			full_binary_function[18] = 1
			bin_rel_ln = getBinLine( lines, marks[func_var], marks )
			nextLines[0] = bm.dtb( bin_rel_ln )
		elif func_var == function_names[1][0] and vars[2] == "at":
			
			#Get reference binary variable lenght and indexes
			bvl = _StaticBinVarLength_.copy()
			bvi = _StaticBinVarIndex_.copy()
			
			bin_vars = init_bin_vars(bvi, bvl)
			bin_vars[5] = bm.dtb( getParIndex( [1,0,0],vars[0] ), 2 )
			bin_vars[6] = bm.dtb( getParIndex( [1,0,1],vars[1] ), 5 )
			full_binary_function = create_full_binary_function(bin_vars, bvi, bvl)
			nextLines[0] = bm.dtb(eofbln + 1 + int(vars[3]))
			full_binary_function[0] = 1
			full_binary_function[8] = 1
		elif func_var == function_names[0][1]:
			bin_vars = init_bin_vars(bvi, bvl)
			bin_vars[5] = bm.dtb( getParIndex( [1,0,0],vars[0] ), 2 )
			bin_vars[6] = bm.dtb( getParIndex( [1,0,1],vars[1] ), 5 )
			for i in range( 2 ):
				full_binary_function[i+ 9] = bin_vars[1][i]
			full_binary_function[6] = 1
		elif func_var == function_names[1][3]:
			bvi = _StaticBinVarIndex_.copy()
			bvl = _StaticBinVarLength_.copy()
			bin_vars = init_bin_vars(bvi, bvl)
			full_binary_function[2] = 1
			full_binary_function[6] = getParIndex([1,3,0], vars[0])
			if vars[1] in regs:
				full_binary_function[5] = 1
				bin_vars[5] = bm.dtb(getParIndex([1,3,1], vars[1]), 2)
				bin_vars[6] = bm.dtb(getParIndex([1,3,2], vars[2]), 5)
				for i in range(2):
					full_binary_function[11 + i] = bin_vars[5][i]
				for i in range(5):
					full_binary_function[13 + i] = bin_vars[6][i]
			else:
				# print("vars[1]: %s" % (vars[1]))
				nextLines[0] = bm.dtb(int(vars[1]))
		elif func_var == function_names[3][1]:
			# print("ELSE:")
			full_binary_function[5] = 1
			nextLines[0] = None
			t = if_marks[ str( il - 1 ) ]
			# print("t: %s" % (t))
			for i, _ in enumerate(t):
				if t[str(i)]["0"] == 0:
					# print("ln: %s" % (t[str(i)]["1"] ) )
					nextLines[0] = bm.dtb( getBinLine( lines, t[str(i)]["1"], marks ) )
					break
			if nextLines[0] == None:
				raise CustomException("Error: ln %s: if statement was not encoded right, 0" % (ln_n + 1))
		elif func_var == function_names[3][2]:
			full_binary_function = [0 for i in range( bw )]
			t_bin_vars[0] = bm.dtb( getParIndex( [0,0,0],vars[0] ) + 1 )
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
		elif func_var == sei[1] and sfunc_var != function_names[3][1] and sfunc_var != function_names[3][2]:
			il -= 1
		elif func_var in sei or func_var == function_names[3][0] or func_var == "":
			pass
		else:
			t = gvt( lines[ln_n] )
			tt = lines[ln_n].rstrip()
			if t == "bin":
				full_binary_function = bm.dtb(bm.btd([int(i) for i in tt[2:]]))
			elif t == "hex":
				full_binary_function = bm.dtb(bm.htd(tt[2:]))
			elif t == "int":
				full_binary_function = bm.dtb(int( tt ))
			else:
				func_num = getFuncNum( func_var )				#Logical function number
				# f_func_num = getFuncNum( func_var, True )		#Binary function number
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
				
				MainType = None
				for i, _ in enumerate(function_names):
					if func_var in function_names[i]:
						MainType = i
						break
				if MainType == None:
					raise NameError
				
				bvl, bvi = get_var_order(
					MainType, 
					function_names[MainType].index(func_var),
					bvl,
					bvi,
					ReorderDict
				)
				
				bin_vars = []
				for j, e in enumerate( zip(bvl,bvi) ):
					bin_vars.append( [0 for k in range( bvl[j] )] )
				if func_var == function_names[2][0]:
					is_alu = 1
					bin_func = bm.dtb( getParIndex( [2,0,2], vars[2] ), 4 )
					if vars[0] == function_params[2][0][2][8]:
						bin_vars[0] = bm.dtb( 1, bvl[0] )
					for i, _ in enumerate(bin_vars):
						if getParIndex( [2,0,i], vars[i] ) == "pass":
							break
						bin_vars[i] = bm.dtb( getParIndex( [2,0,i], vars[i] ), bvl[i] )
				else:
					is_alu = 0
					function_names_index = function_names[MainType].index( func_var )
					# print("func_var: %s" % (bm.blts(func_var)))
					# print("vars: %s" % (vars))
					# print("bvi: %s" % (bvi))
					# print("ReorderDict[%s][%s]: %s" % (MainType, func_var, ReorderDict[MainType][function_names[MainType].index(func_var)]))
					# print("function_names_index: %s" % (function_names_index))
					# print("function_var_amount[1][function_names_index]: %s" % (function_var_amount[1][function_names_index]))
					for i in range(function_var_amount[1][function_names_index]):
						try:
							temp_type = function_params[MainType][f_func_num][i][0]
						except Exception:
							break
						# fpo = function_param_offset[1][function_names_index]
						#bin_vars[fpo + i] = bm.dtb( getParIndex( [1,function_names_index,i], vars[i] ), bvl[i + fpo] )
						try:
							bin_vars[i] = bm.dtb( getParIndex( [MainType,function_names_index,i], vars[i] ), bvl[i] )
						except Exception:
							raise CustomException("Error: ln %s, Incorrect variable input." % (ln_n + 1))
						if bin_vars[i] == "pass":
							bin_vars[i] = None
							break
						if func_var == function_names[1][0]:
							nextLines[0] = bm.dtb( int( vars[2] ) )
						elif func_var == function_names[1][1]:
							try:
								nextLines[0] = bm.dtb( int( vars[3] ) )
							except Exception:
								raise CustomException("Error: ln %s: 4th variable missing." % (ln_n + 1))
				
				full_binary_function[4] = is_alu
				
				tbvi = _StaticBinVarIndex_.copy()
				tbvl = _StaticBinVarLength_.copy()
				skip_smaller_vars = False
				t = tbvi.index(7)
				ti = 0

				if tbvl[t] == 4:
					ti = t
				else:
					tbvi.pop(t)
					tbvl.pop(t)
					t = tbvi.index(7)
					if tbvl[t] == 4:
						ti = t
					else:
						raise CustomException("Error: ln %s, Unable to format bin_vars properly." % (ln_n + 1))

				if bin_vars[ti] != [0 for i in range(4)]:
					skip_smaller_vars = True
				
				for i, _ in enumerate(bin_func):
					full_binary_function[i] = bin_func[i]
				for i, e in enumerate(bin_vars):
					# print("bvi: %s" % (bvi[i]))
					if (bvi[i] == 7 and skip_smaller_vars and i != ti or 
						bvi[i] == 9 and skip_smaller_vars):
						pass
					else:
						for j, _ in enumerate( e ):
							full_binary_function[bvi[i] + j] = e[j]
				# print("full_binary_function: %s" % (bm.blts(full_binary_function)))
		if func_var not in wtf_excp:
			fh.write( bm.blts( full_binary_function ) + "\n" )
			bin_ln += 1
			for i, _ in enumerate( nextLines ):
				if isinstance( nextLines[i], list ):
					fh.write( bm.blts( nextLines[i] ) + "\n" )
					bin_ln += 1
		ln_n += 1
	fh.close()
	return 1