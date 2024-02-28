"""Assembler.py -> WIP assembler for Schön Core Alpha v.0.1.0

My own proprietary low level language for my CPU Schön Core Alpha v.0.1.0
Major non-user functions:

WIP

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

class RunningStates(Enum):
	Initializing = 0
	Running = 1
	ExitNoError = 2
	ExitUnknownFunction = 3
	ExitUnknownError = 4
	ExitWithErrorMessage = 5

class WorkingFile():	

	#Constants
	_VersionName_: str = "Schön Core Alpha v.0.1.0" #Keep constant!	
	_ImportExtension_: str = ".s1"                  #Keep constant!
	_AssembledExtension_: str = "schonexe1"         #Keep constant!	
	
	#Path of working file
	ImportedFileName: str = None
	AssembledFileName: str = None
	
	#Different files to work with
	RawFile: list = None
	MetaInfoAssembling: list = None
	MainAssembling: list = None	
	
	#Basic information about current work in progress file
	WorkingLineNumber: int = 0
	WorkingBinaryLineNumber: int = 0
	IfStatementsEncountered: int = 0
	EndOfFileLineNumber: int = 0

	IfMarks: list = None
	Marks: list = None
	FunctionIndecies: list = None
	FunctionNames: list = None

	RunningState = RunningStates.Initializing

	def WorkingFile(self) -> None:                  #Initialize clas		
		self.RawFile = []
		self.MetaInfoAssembling = []
		self.MainAssembling = []
		self.IfMarks = []
		self.Marks = []
		self.FunctionIndecies = []
		self.FunctionNames = []	

		lgn.debug("WorkingFile: Initialized Workingfile class.")

	def ImportFile(self, filename: str, DestinationName: str) -> None:

		self.ImportedFileName = filename	
		#Open and read file to assemble
		FileHandler = open(bf + pf + self.ImportedFileName)
		self.RawLines = FileHandler.readlines()
		FileHandler.close()

		self.AssembledFileName = DestinationName

		lgn.debug("ImportFile: Imported file %s." % (bf + pf + self.ImportedFileName))
	
	def IncrementGetLine(self) -> str:
		try:
			q: str = self.RawFile[self.WorkingLineNumber]
		except IndexError:
			return -1
		self.WorkingLineNumber += 1
		return q

	def GetMetaInfo(self) -> None:
		
		_worker_file = WorkingFile()
		
		_worker_file.WorkingFile()
		_worker_file.ImportFile(self.ImportedFileName, self.AssembledFileName)
		
		_worker_file.RunningState = RunningStates.Running
		
		while _worker_file.RunningState == RunningStates.Running:
			
			#Handle line
			Line = _worker_file.IncrementGetLine()
			if Line == -1:
				_worker_file.RunningState = RunningStates.ExitNoError
				break

			#Handle tokens and function
			tokens = GetTokens(Line)
			Function = tokens[0]

			if VariableTypes._Has_Value_(Function):
				TemporaryFunctionName = Function
				TemporaryFunctionIndex = _worker_file.WorkingLineNumber

				self.FunctionNames.append(TemporaryFunctionName)
				self.FunctionIndecies.append(TemporaryFunctionIndex)
			elif FunctionNames._Has_Value_(Function):
				if Function == AbstractFunctions.mark.value:
					self.Marks.append(Function)

class IfNames(Enum):
	If = "if"

	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class StandardFunctions(Enum):
	rom = "rom"
	ram = "ram"
	register = "reg"
	stack = "stack"
	interrupt = "interrupt"
	general_io = "io"
	call_subroutine = "call"

	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class ALUFunctions(Enum):
	alu_function = "compute"
	
	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class AbstractFunctions(Enum):
	mark = "mark"
	_else = "else"
	_elif = "elif"
	_pass = "pass"
	_def = "def"
	
	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class SpecialCaseFunctions(Enum):
	StartBrace = "{"
	EndBrace = "}"
	DefineFunction = "def"
	EndOfFileIndicator = "eof"
	
	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class VariableTypes(Enum):
	Integer = "int"
	FloatingPoint = "float"
	Character = "char"
	String = "string"
	Boolean = "bool"
	Array = "array"
	List = "list"
	
	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_

class FunctionNames(Enum):
	If = IfNames
	Standard = StandardFunctions
	ALU = ALUFunctions
	Abstract = AbstractFunctions
	SpecialCase = SpecialCaseFunctions
	VariableDeclarationFunctions = VariableTypes

	def _Has_Value_(self, element: str) -> bool:
		for element in self._value2member_map_:
			if element._Has_Value_(element):
				return True 
		return False

class TokenTypes(Enum):
	String = 0
	Char = 1
	Number = 2
	Unknown = 3

def GetTokens(Line: str) -> list:
	
	i = 0
	char = ''

	Space = " "
	Tab = "\t"
	CharIndicator = "'"

	tokens = []

	while i <= len(Line):
		char = Line[i]

		if char == Space:
			pass
		elif char == Tab:
			pass
		elif char == CharIndicator:
			TemporaryToken = [TokenTypes.Char, ""]
			while char != CharIndicator:
				i += 1
				try:
					char = Line[i]
					if char == CharIndicator:
						tokens.append(TemporaryToken[1])
						break
					TemporaryToken[1] += char
				except IndexError:
					raise IndexError
		else:
			if char.isnumeric():
				TemporaryToken = [TokenTypes.Number, ""]
			else:
				TemporaryToken = [TokenTypes.String, ""]
			
			LastChar = False
			while char != Space and char != Tab and LastChar != False:
				i += 1
				try:
					char = Line[i]
					TemporaryToken += char
				except IndexError:
					LastChar = True
					tokens.append(TemporaryToken)
					break

	return tokens

def Main(ImportFilename: str, DestinationName: str) -> None:
	"""ASM.Main(ImportFilename: str, DestinationName: str) -> Main assembler
	"""

	#Handle logging
	lgn.getLogger().setLevel(LOGLEVEL)
	
	#Handle file worker
	worker_file = WorkingFile()
	worker_file.WorkingFile()

	#Read file to RawFile
	worker_file.ImportFile(ImportFilename, DestinationName)

	#Find user defined functions and marks
	worker_file.GetMetaInfo()
	
	worker_file.RunningState = RunningStates.Running
	
	while worker_file.RunningState == RunningStates.Running:
		
		#Handle line/linenumber
		Line = worker_file.IncrementGetLine()
		if Line == -1:
			worker_file.RunningState = RunningStates.ExitNoError
			break

		#Handle tokens
		tokens = GetTokens(Line)
		Function = tokens[0]

		#Handle functions
		if (FunctionNames._Has_Value_(Function) == False and 
	  		Function in worker_file.FunctionNames):
			pass
		elif (FunctionNames._Has_Value_(Function) == False and 
				Function in worker_file.Marks):
			pass
		elif FunctionNames._Has_Value_(Function) == False:
			pass
		if IfNames._Has_Value_(Function):
			pass
		elif StandardFunctions._Has_Value_(Function):
			pass
		elif ALUFunctions._Has_Value_(Function):
			pass
		elif AbstractFunctions._Has_Value_(Function):
			pass
		elif SpecialCaseFunctions._Has_Value_(Function):
			pass
		elif VariableTypes._Has_Value_(Function):
			pass
		else:
			worker_file.RunningState = RunningStates.ExitUnknownFunction
	
	if worker_file.RunningState != RunningStates.ExitNoError:
		return worker_file.RunningState
	
	#Return final assembled binary
	return worker_file.MainAssembling
