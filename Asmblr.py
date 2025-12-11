"""Schön Core Alpha v.0.1.0 Python Edition Assembler (Refactored) -> My new refactored assembler for my Schön Core Alpha v.0.1.0
Main User classes:
Assembler
"""

# import math
from typing import Self

class Symbols():
	"""Assembler.Symbols() -> Class for predefined and dynamic symbols for assembly
	"""

	def __init__(self: Self) -> None:
		#Base container for all symbols, static and dynamic
		self.SymbolGroups: dict[str, list[str]] = {}

		self.CreateSymbolsGroup("FunctionsSymbols")
		self.CreateSymbolsGroup("ComparisonSymbols")
		self.CreateSymbolsGroup("ArithmeticLogicSymbols")
	
	def __setitem__(self: Self, Key: str, Value: str) -> None:
		self.SymbolGroups[Key].append(Value)
	
	def __getitem__(self: Self, Key: str, Index: int) -> str:
		return self.SymbolGroups[Key][Index]
	
	def CreateSymbolsGroup(self: Self, GroupName: str) -> bool:
		try:
			self.SymbolGroups[GroupName] = []
			return True
		except Exception:
			return False
	
	def DeleteSymbolsGroup(self: Self, Key: str) -> bool:
		try:
			del self.SymbolGroups[Key]
			return True
		except KeyError:
			return False

class Assembler: #Main assembler class to assemble
	def __init__(self):
		#Static variables
		self._ASSEMBLERNAME_: str = "Schön Core"		#Do not change!
		self._ASSEMBLERCORE_: str = "Alpha Pro"			#Do not change!
		self._ASSEMBLERCOREVERSION_: str = "v.0.1.0"	#Do not change!
		self._ASSEMBLERVERSION_: str = "0.1.0"			#Do not change!
		self._ASSEMBLYEXTENSION_: str = "s"				#Do not change!
		self._RAWBINARYEXTENSION_: str = "schonexe"		#Do not change!

		#Initialisation of dynamic variables
		#File paths and names
		self.FileToAssemblePath: str = ""
		self.FileToAssembleName: str = ""
		self.FileDestinationPath: str = ""
		self.FileDestinationName: str = ""

		#Worker variables
		self.AssemblyFileRead: list[str] = []	#Raw file read to asssemble
		self.SymbolicFile: list[str] = []		#Raw file parsed by initial symbolic parsing
		self.WorkerFile: list[str] = []			#File for processing complete output file
		self.RawBinaryOutputFile: list[str] = []	#Raw output file in raw binary

		self.SymbolsHandler: "Symbols" = Symbols()
