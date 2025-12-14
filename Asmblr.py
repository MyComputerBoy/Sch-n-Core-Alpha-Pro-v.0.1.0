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
		#There's a group for indexable groups and a group for unindexable symbols
		#So, SymbolsGroups is a dict containing every category, which is also a dict
		#And the categories has lists of all the elements that you wanna use
		#Indexable elements have predefinable elements, while unindexable elements are more of a concept, like ints, strings etc.
		self.IndexableSymbolGroups: dict[str, dict[str, list[str]]] = {}
		self.UnindexableSymbolsGroups: dict[str, dict[str, list[str]]] = {}

		# DidCreatePredefinedGroups: bool = self.CreatePredefinedGroups()
		# if not DidCreatePredefinedGroups:
		# 	raise Exception("Could not create predefined symbols.")

	def __setitem__(self: Self, IsIndexable: bool, GroupName: str, CategoryName: str, Value: str) -> None:
		if IsIndexable:
			self.IndexableSymbolGroups[GroupName][CategoryName].append(Value)
		else:
			self.UnindexableSymbolsGroups[GroupName][CategoryName].append(Value)
	
	def __getitem__(self: Self, IsIndexable: bool, GroupName: str, CategoryName: str, Index: int) -> str:
		if IsIndexable:
			return self.IndexableSymbolGroups[GroupName][CategoryName][Index]
		else:
			return self.UnindexableSymbolsGroups[GroupName][CategoryName][Index]
	
	def CreatePredefinedGroups(self: Self, IsIndexable: bool, GroupName: str, CategoryNames: list[str], PopulationList: list[list[str]]) -> bool:
		#Creating the group
		DidCreateGroupCategory: bool = self.CreateSymbolsGroup(IsIndexable, GroupName)
		if not DidCreateGroupCategory:
			raise Exception("Could not create $s group." % (GroupName))
		
		#Creating the categories
		for Category in CategoryNames:
			DidCreateGroupCategory: bool = self.CreateSymbolGroupsCategory(IsIndexable, GroupName, Category)
			if not DidCreateGroupCategory:
				raise Exception("Could not create %s[%s] category." % (GroupName, Category))
		
		#Populating the categories in the group
		PopulationIndex: int = 0
		for PopulationListElement in PopulationList:
			DidPopulateCategory: bool = self.PopulateWholeCategoryFromList(IsIndexable, GroupName, CategoryNames[PopulationIndex], PopulationListElement)
			if not DidPopulateCategory:
				raise Exception("Could not populate %s[$s] category." % (GroupName, CategoryNames[PopulationIndex]))
			PopulationIndex += 1

		return True

	def PopulateWholeCategoryFromList(self: Self, IsIndexable: bool, GroupName: str, CategoryName: str, PopulatedCategory: list[str]) -> bool:
		try:
			if IsIndexable:
				self.IndexableSymbolGroups[GroupName][CategoryName] = PopulatedCategory
			else:
				self.UnindexableSymbolsGroups[GroupName][CategoryName] = PopulatedCategory

			return True
		except Exception:
			return False

	def CreateSymbolsGroup(self: Self, IsIndexable: bool, GroupName: str) -> bool:
		try:
			if IsIndexable:
				self.IndexableSymbolGroups[GroupName] = {}
			else:
				self.UnindexableSymbolsGroups[GroupName] = {}
			return True
		except Exception:
			return False
	
	def DeleteSymbolsGroup(self: Self, IsIndexable: bool, GroupName: str) -> bool:
		try:
			if IsIndexable:
				del self.IndexableSymbolGroups[GroupName]
			else:
				del self.UnindexableSymbolsGroups[GroupName]
			return True
		except KeyError:
			return False
	
	def CreateSymbolGroupsCategory(self: Self, IsIndexable: bool, GroupName: str, CategoryName: str) -> bool:
		try:
			if IsIndexable:
				self.IndexableSymbolGroups[GroupName][CategoryName] = []
			else:
				self.UnindexableSymbolsGroups[GroupName][CategoryName] = []

			return True
		except Exception:
			return False
	
	#Format: GroupName, CategoryName, ListIndex (converted to str)
	def HasElement(self: Self, IsIndexable: bool, ElementToCheck: str) -> list[str]:

		if IsIndexable:
			GroupToLoopOver = self.IndexableSymbolGroups
		else:
			GroupToLoopOver = self.UnindexableSymbolsGroups

		for GroupToCheck in GroupToLoopOver:
			for CategoryToCheck in GroupToCheck:
				for Element in CategoryToCheck:
					if Element == ElementToCheck:
						return [GroupToCheck, CategoryToCheck, str(CategoryToCheck.index(Element))]

		raise IndexError

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
	
	def LoadAssemblyFileToClass(self: Self, PathToAssemblyFile: str) -> bool:
		try:
			FileHandler = open(PathToAssemblyFile, "r")
			self.AssemblyFileRead = FileHandler.readlines()

			return True
		except FileNotFoundError:
			return False
	
	# def ParseSymbols(self: Self) -> bool:
	# 	WorkingLineIndex: int = 0

	# 	#Go through every line to parse
	# 	for TemporaryWorkingLine in self.AssemblyFileRead:
	# 		SpaceSeperatedWorkingLine: list[str] = TemporaryWorkingLine.split(" ")

	# 		#Make sure the WorkingLineIndex reflects which line is worked on
	# 		WorkingLineIndex += 1

	# 	return True
