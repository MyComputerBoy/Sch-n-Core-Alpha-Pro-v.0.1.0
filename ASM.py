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
from typing import Optional

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

	def __init__(self):			#Bts __init__()
		#Constants
		self._VersionName_: str = "Schön Core Alpha v.0.1.0" #Keep constant!	
		self._ImportExtension_: str = ".s1"                  #Keep constant!
		self._AssembledExtension_: str = ".schonexe1"        #Keep constant!	
		
		#Path of working file
		# self.ImportedFileName: Optional[str] = None
		# self.AssembledFileName: Optional[str] = None
		
		# #Different files to work with
		# self.RawFile: Optional[list[str]] = None
		# self.MetaInfoAssembling: Optional[list[str]] = None
		# self.MainAssembling: Optional[list[str]] = None	
		
		#Basic information about current work in progress file
		self.WorkingLineNumber: int = 0
		self.WorkingBinaryLineNumber: list[int] = []
		self.IfStatementsEncountered: int = 0
		self.EndOfFileLineNumber: int = 0

		#Meta information about working file
		self.BranchMarks: dict = {}
		self.Marks: dict = {}
		self.UserFunctions: dict = {}

		#Assembling information
		self.AssemblingBinaryLine: list = []
		self.AssemblingBinaryNextLine: list = []

		#State of assembling
		self.RunningState = RunningStates.Initializing

	def WorkingFile(self) -> None:                  #Properly initialize class
		lgn.debug("WorkingFile: Initialized Workingfile class.")

	def ImportFile(self, filename: str, DestinationName: str) -> None:

		#Different files to work with
		if self.RawFile is None:
			self.RawFile: list[str] = []
		if self.MetaInfoAssembling is None:
			self.MetaInfoAssembling: list[str] = []
		if self.MainAssembling is None:
			self.MainAssembling: list[str] = []	

		#Open and read file to assemble
		FileHandler = open(bf + pf + self.ImportedFileName)
		self.RawLines = FileHandler.readlines()
		FileHandler.close()

		#Path of working file
		self.ImportedFileName: str = filename
		self.AssembledFileName: str = DestinationName


		lgn.debug("ImportFile: Imported file %s." % (bf + pf + self.ImportedFileName))
	
	def IncrementGetLine(self) -> str:
		try:
			if type(self.RawFile) is type(None):
				lgn.critical("WorkingFile.IncrementGetLine(): Error: File not imported! Import file to get line.")
				raise ImportError
			q: Optional[str] = self.RawFile[self.WorkingLineNumber] # type: ignore
		except IndexError:
			lgn.debug("WorkingFile.IncrementGetLine(): Out of range of imported file.")
			raise IndexError
		self.WorkingLineNumber += 1
		return q

	def TryGetNextLine(self) -> str:
		try:
			if type(self.RawFile) is type(None):
				lgn.debug("WorkingFile.TryGetNextLine(): Error: File not imported! Import file to get line.")
				raise ImportError
			q: str = self.RawFile[self.WorkingLineNumber + 1] # type: ignore
		except IndexError:
			lgn.debug("WorkingFile.TryGetNextLine(): Out of range of imported file.")
			raise IndexError
		return q
 
	def GetMetaInfo(self) -> None:
		
		_worker_file = WorkingFile()
		
		_worker_file.WorkingFile()
		_worker_file.ImportFile(self.ImportedFileName, self.AssembledFileName) # type: ignore
		
		_worker_file.RunningState = RunningStates.Running
		
		while _worker_file.RunningState == RunningStates.Running:
			
			#Handle line
			try:
				Line = _worker_file.IncrementGetLine()
			except IndexError:
				_worker_file.RunningState = RunningStates.ExitNoError
				break
			except ImportError:
				_worker_file.RunningState = RunningStates.ExitWithErrorMessage
			
			NextLine = _worker_file.TryGetNextLine()

			#Handle tokens and function
			_tokens = tokens = GetTokens(Line)
			Function = tokens.pop(0)
			MetaName = tokens.pop(0)

			NextLineTokens = GetTokens(NextLine)
			NextLineFunction = NextLineTokens.pop(0)

			if Function == AbstractFunctions._def.value:
				self.UserFunctions[str(MetaName)] = _worker_file.WorkingLineNumber
			elif FunctionNames.__Has_Value__(Function): # type: ignore
				if Function == AbstractFunctions.mark.value:
					self.Marks[str(MetaName)] = _worker_file.WorkingFile
			elif (Function == BranchNames.Branch.value and
				NextLineFunction == SpecialCaseFunctions.StartBrace.value):
				
				if BranchVariables.conditional.value in _tokens:
					self.IfStatementsEncountered += 1

				self.WorkingLineNumber += 1

				BranchEscapeLine, BranchEscapeIndex = GetEscapeFromInscape(
        			self.WorkingLineNumber, 1, InscapeEscapeTypes.Wrapper) # type: ignore

				self.BranchMarks[str(self.IfStatementsEncountered)] = BranchEscapeLine # type: ignore
			elif IfElifElseFunctions.__Has_Value__(Function): # type: ignore
				
				if Function == IfElifElseFunctions._if:
					self.IfStatementsEncountered += 1

				self.WorkingLineNumber += 1
    
				BranchEscapeLine, BranchEscapeIndex = GetEscapeFromInscape(
        			self.WorkingLineNumber, 1, InscapeEscapeTypes.Wrapper) # type: ignore

				self.BranchMarks[str(self.IfStatementsEncountered)] = BranchEscapeLine
				
class BinaryInstructionInfo(Enum):
	MainFunction = [0,4]
	IsALU = [5,5]
	VariableA = [5,9]
	VariableB = [9,11]
	RegisterA = [11,18]
	RegisterB = [18,25]
	RegisterC = [25,32]

class BranchNames(Enum):
	Branch = "branch"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class BranchVariables(Enum):
	pointer = "pointer"
	conditional = "conditional"

class BranchConditionalComparisonParameters(Enum):
	LargerThan = ">"
	Equals = "="
	LargerOrEquals = ">="
	LessThan = "<"
	NotEquals = "!="
	LessOrEquqals = "<="

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class BranchConditionalIndecies(Enum):
	LargerThan = 1
	Equals = 2
	LargerOrEquals = 3
	LessThan = 4
	NotEquals = 5
	LessOrEquqals = 6

class IfElifElseFunctions(Enum):
	_if = "if"
	_elif = "elif"
	_else = "else"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class BranchFlagParameters(Enum):
	CarryOut = "co"
	IsZero = "iz"
	OverFlow = "of"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class StandardFunctions(Enum):
	rom = "rom"
	ram = "ram"
	register = "reg"
	stack = "stack"
	interrupt = "interrupt"
	general_io = "io"
	call_subroutine = "call"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class ALUFunctions(Enum):
	alu_function = "compute"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class AbstractFunctions(Enum):
	mark = "mark"
	_else = "else"
	_elif = "elif"
	_pass = "pass"
	_def = "def"
	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class SpecialCaseFunctions(Enum):
	StartBrace = "{"
	EndBrace = "}"
	DefineFunction = "def"
	EndOfFileIndicator = "eof"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class VariableTypes(Enum):
	Integer = "int"
	FloatingPoint = "float"
	Character = "char"
	String = "string"
	Boolean = "bool"
	Array = "array"
	List = "list"

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class FunctionNames(Enum):
	Branch = BranchNames
	Standard = StandardFunctions
	ALU = ALUFunctions
	Abstract = AbstractFunctions
	SpecialCase = SpecialCaseFunctions
	VariableDeclarationFunctions = VariableTypes

	def _value2member_list_map_(self):
		ValueMemberList = []
		TemporaryValue2MemberList = list(self._value2member_map_.values())
		for class_element in TemporaryValue2MemberList:
			ValueMemberList.append(class_element.value)
		return ValueMemberList

	def __Has_Value__(self, element: str) -> bool:
		for class_element in self._value2member_list_map_():
			if class_element.__Has_Value__(element):
				return True 
		return False

	def _Indexed_Has_Value_(self, element: str) -> list:
		for index, class_element in enumerate(self._value2member_list_map_()):
			if class_element.__Has_Value__(element):
				return [True, index]
		return [False, -1]

	def _Has_Value_To_Element_(self, element_test: int):
		for _, class_element in enumerate(self._value2member_list_map_()):
			if class_element.__Has_Value__(element_test):
				return [True, class_element]
		return [False, -1]

class TokenTypes(Enum):
	String = 0
	Char = 1
	Number = 2
	Unknown = 3

class WrapperInscapeEscapes(Enum):
	Inscape = "{"
	Escape = "}"

	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_
	
	def IsInscape(self, element: str) -> bool:
		return element == WrapperInscapeEscapes.Inscape.value
	
	def IsEscape(self, element: str) -> bool:
		return element == WrapperInscapeEscapes.Escape.value

class MathematicalInscapeEscape(Enum):
	Inscape = "("
	Escape = ")"
	
	def _Has_Value_(self, element: str) -> bool:
		return element in self._value2member_map_
	
	def IsInscape(self, element: str) -> bool:
		return element == MathematicalInscapeEscape.Inscape.value
	
	def IsEscape(self, element: str) -> bool:
		return element == MathematicalInscapeEscape.Escape.value

class InscapeEscapeTypes(Enum):
	Wrapper = WrapperInscapeEscapes
	Mathematical = MathematicalInscapeEscape

	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_
	
	def IsInscape(self, element: str, ScapeType):
		if ScapeType == InscapeEscapeTypes.Wrapper:
			return WrapperInscapeEscapes.IsInscape(element) # type: ignore
		elif ScapeType == InscapeEscapeTypes.Mathematical:
			return MathematicalInscapeEscape.IsInscape(element) # type: ignore
		else:
			return TypeError
	
	def IsEscape(self, element: str, ScapeType):
		if ScapeType == InscapeEscapeTypes.Wrapper:
			return WrapperInscapeEscapes.IsEscape(element) # type: ignore
		elif ScapeType == InscapeEscapeTypes.Mathematical:
			return MathematicalInscapeEscape.IsEscape(element) # type: ignore
		else:
			return TypeError

class InscapeEscapeExits(Enum):
	NoError = 0
	EscapeNotFound = 1
	InscapeNotFound = 2
	UnknownError = 3

class RegisterNames(Enum):
	GeneralPurpose = "gpr"
	ArithmeticLogic = "alur"
	Stack = "stk"
	SpecialPurpose = "spr"

	def _value2member_list_map_(self):
		ValueMemberList = []
		TemporaryValue2MemberList = list(self._value2member_map_.values())
		for class_element in TemporaryValue2MemberList:
			ValueMemberList.append(class_element.value)
		return ValueMemberList
    
	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class InscapeEscapeNames(Enum):
	Inscape = "{"
	Escape = "}"

	def _value2member_list_map_(self):
		ValueMemberList = []
		TemporaryValue2MemberList = list(self._value2member_map_.values())
		for class_element in TemporaryValue2MemberList:
			ValueMemberList.append(class_element.value)
		return ValueMemberList
	
	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class ToFromNames(Enum):
	To = "to"
	From = "from"

	def _value2member_list_map_(self):
		ValueMemberList = []
		TemporaryValue2MemberList = list(self._value2member_map_.values())
		for class_element in TemporaryValue2MemberList:
			ValueMemberList.append(class_element.value)
		return ValueMemberList
	
	def __Has_Value__(self, element: str) -> bool:
		return element in self._value2member_map_

class GenericFunctionParameterNames(Enum):
	Registers = RegisterNames
	InscapeEscapes = InscapeEscapeNames
	ToFroms = ToFromNames

	def _value2member_list_map_(self):
		ValueMemberList = []
		TemporaryValue2MemberList = list(self._value2member_map_.values())
		for class_element in TemporaryValue2MemberList:
			ValueMemberList.append(class_element.value)
		return ValueMemberList

	def _Indexed_Has_Value_(self, element):
		for class_element in self._value2member_list_map_():
			if class_element.__Has_Value__(element):
				class_element_list = class_element._value2member_list_map_()
				return [True, class_element, class_element_list.index(element)]
		return [False, -1, -1]

	def __Has_Value__(self, element: str) -> bool:
		for class_element in self._value2member_list_map_():
			if class_element.__Has_Value__(element):
				return True 
		return False

class GenericFunctionVariableTypes(Enum):
    ToFrom = 0
    StartEndIndicator = 1
    RegisterType = 2
    Number = 3
    IndexFromCustomList = 4
    Copy = 5
    EndOfVariables = 6

FunctionIndecies = [
	"rom",
	"ram",
	"register",
	"stack",
	"branch",
	"interrupt",
	"call_subroutine",
	"generel_io",
]

FunctionParameters = {
	
	"Branch": [
		
	],
	"Standard": {
		StandardFunctions.rom: [
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.IndexFromCustomList,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.ram: [
			GenericFunctionVariableTypes.ToFrom,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.register: [
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.IndexFromCustomList,
			GenericFunctionVariableTypes.name,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.stack: [
			GenericFunctionVariableTypes.IndexFromCustomList,
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.IndexFromCustomList,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.interrupt: [
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.general_io: [
			GenericFunctionVariableTypes.ToFrom,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.RegisterType,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.EndOfVariables,
		],
		StandardFunctions.call_subroutine: [
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.ToFrom,
			GenericFunctionVariableTypes.Number,
			GenericFunctionVariableTypes.EndOfVariables,
		],
	},
	"ALU": [
		GenericFunctionVariableTypes.RegisterType,
		GenericFunctionVariableTypes.Number,
		GenericFunctionVariableTypes.IndexFromCustomList,
		GenericFunctionVariableTypes.RegisterType,
		GenericFunctionVariableTypes.Number,
		GenericFunctionVariableTypes.RegisterType,
		GenericFunctionVariableTypes.Number,
		GenericFunctionVariableTypes.EndOfVariables,
	],
 
}

def GetMainTypeAndIndeciesFromTokens(Function: str, Variables: list):
    
	HasValue, MainFunctionIndex = FunctionNames._Indexed_Has_Value_(Function) # type: ignore
    
	if not HasValue:	
		raise NameError
    
	for variable_index, variable_type in enumerate(FunctionParameters[MainFunctionIndex]):
		if variable_type == GenericFunctionVariableTypes.ToFrom:
			pass
		elif variable_type == GenericFunctionVariableTypes.StartEndIndicator:
			pass
		elif variable_type == GenericFunctionVariableTypes.RegisterType:
			pass
		elif variable_type == GenericFunctionVariableTypes.Number:
			pass
		elif variable_type == GenericFunctionVariableTypes.IndexFromCustomList:
			pass
		elif variable_type == GenericFunctionVariableTypes.Copy:
			pass
		elif variable_type == GenericFunctionVariableTypes.EndOfVariables:
			break
		else:
			raise TypeError

def ConvertVariablesToBinaries(Function: str, Variables: list):
    pass

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

def GetEscapeFromInscape(Lines: list, InscapeLine: int, InscapeIndex: int, InscapeType: InscapeEscapeTypes) -> list:
	GetEscapeState = RunningStates.Running

	LineNumber = InscapeLine
	LineIndex = InscapeIndex

	Inscapes = 0

	while GetEscapeState == RunningStates.Running:
		try:
			line = Lines[LineNumber]
		except IndexError:
			return [InscapeEscapeExits.EscapeNotFound]
		
		while LineIndex < len(line):
			char = line[LineIndex]
			if InscapeEscapeTypes.IsInscape(char, InscapeType): # type: ignore
				Inscapes += 1
			elif InscapeEscapeTypes.IsEscape(char, InscapeType) and Inscapes > 0: # type: ignore
				Inscapes -= 1
			elif InscapeEscapeTypes.IsEscape(char, InscapeType) and Inscapes == 0: # type: ignore
				return [LineNumber, LineIndex]
			LineIndex += 1
		LineNumber += 1
	
	return [InscapeEscapeExits.EscapeNotFound]

def GetInscapeOnLine(Lines: list, InscapeLine: int, InscapeType: InscapeEscapeTypes):
	GetInscapeState = RunningStates.Running

	LineNumber = InscapeLine

	LineNumber = InscapeLine
	LineIndex = 0

	while GetInscapeState == RunningStates.Running:
		try:
			line = Lines[LineNumber]
		except IndexError:
			return InscapeEscapeExits.InscapeNotFound

		while LineIndex < len(line):
			char = line[LineIndex]
			if InscapeEscapeTypes.IsInscape(char, InscapeType): # type: ignore
				return LineNumber, LineIndex
			LineIndex += 1
		return InscapeEscapeExits.InscapeNotFound
	return InscapeEscapeExits.UnknownError

def Main(ImportFilename: str, DestinationName: str) -> RunningStates | list[str]:
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
		Function = tokens.pop(0)
		Variables = tokens

		#Handle function number
		ExpectHandlingFunctionNumber = False
		try:
			worker_file.WorkingBinaryLineNumber[0:4] = bm.dtb(FunctionIndecies.index(Function), 4)
		except ValueError:
			ExpectHandlingFunctionNumber = True

		#Handle functions
		if (FunctionNames.__Has_Value__(Function) == False and # type: ignore
	  		Function in worker_file.UserFunctions):
			pass
		elif (FunctionNames.__Has_Value__(Function) == False and # type: ignore
			Function in worker_file.Marks):
			pass
		elif FunctionNames.__Has_Value__(Function) == False: # type: ignore
			pass
		elif BranchNames.__Has_Value__(Function): # type: ignore
			UsingImmediate = True
			ExpectComparison = False
			
			if Variables[0] == BranchVariables.conditional.value:
				Variables.pop(0)
				UsingImmediate = False
				ExpectComparison = True
			
			if Variables[0] == BranchVariables.pointer.value:
				Variables.pop(0)
				UsingImmediate = True
			
			if UsingImmediate:
				pass

			if ExpectComparison:
				pass
		elif StandardFunctions.__Has_Value__(Function): # type: ignore
			if Function == StandardFunctions.rom.value:
				pass
			elif Function == StandardFunctions.ram.value:
				pass
			elif Function == StandardFunctions.register.value:
				pass
			elif Function == StandardFunctions.stack.value:
				pass
			elif Function == StandardFunctions.interrupt.value:
				pass
			elif Function == StandardFunctions.ram.value:
				pass
			elif Function == StandardFunctions.general_io.value:
				pass
			elif Function == StandardFunctions.call_subroutine.value:
				pass
		elif ALUFunctions.__Has_Value__(Function): # type: ignore
			pass
		elif AbstractFunctions.__Has_Value__(Function): # type: ignore
			pass
		elif SpecialCaseFunctions.__Has_Value__(Function): # type: ignore
			pass
		elif VariableTypes.__Has_Value__(Function): # type: ignore
			pass
		else:
			worker_file.RunningState = RunningStates.ExitUnknownFunction
	
		if ExpectHandlingFunctionNumber == True:
			worker_file.RunningState = RunningStates.ExitUnknownFunction

	if worker_file.RunningState != RunningStates.ExitNoError:
		return worker_file.RunningState
	
	#Return final assembled binary
	return worker_file.MainAssembling
