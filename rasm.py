"""rasm.py -> Rethinking how to refactor the assembler
"""

from typing import Self
import logging as lgn

LOGLEVEL = lgn.DEBUG

lgn.basicConfig(format="%(levelname)s: %(message)s", level=lgn.DEBUG)
lgn.getLogger().setLevel(LOGLEVEL)

class AssemblerBaseClass():
	def __init__(
		self: Self,
		ClassName: str
	):
		
		self.ClassName: str = ClassName

		self.__ListOfNames__: list[str] = []
		self.__ListOfCallableFunctions__: list = []

		self.__ListOfChildren__: list["AssemblerBaseClass"] = []

		self.BinaryBaseMap: list[int] = []
		self.BinaryAlternateMappings: list[list[int]] = [] #Change binary mappings depending on variables

	def SetNamesFromList(
		self: Self,
		ListOfNames: list[str]
	) -> bool:
		
		self.__ListOfNames__ = ListOfNames

		self.__init_child_list__()
		self.__init_map_list__()

		return True
	
	def SetCallableFunctionsFromList(
		self: Self,
		ListOfCallableFunctions: list
	) -> bool:
		
		self.__ListOfCallableFunctions__ = ListOfCallableFunctions

		return True

	def __init_child_list__(
		self: Self
	) -> bool:
		
		self.__ListOfChildren__ = [AssemblerBaseClass("Temporary%s" % (i)) for i in self.__ListOfNames__]

		return True

	def __init_map_list__(
		self: Self,
	) -> bool:
		
		self.BinaryBaseMap = [0 for _ in self.__ListOfNames__]

		return True

	def SetChilden(
		self: Self,
		ListOfChildex: list["AssemblerBaseClass"]
	) -> bool:
		
		self.__ListOfChildren__ = ListOfChildex

		return True

	def SetChildForIndex(
		self: Self,
		IndexToSetChild: int,
		ChildObject: "AssemblerBaseClass"
	) -> bool:
		
		self.__ListOfChildren__[IndexToSetChild] = ChildObject

		return True

	def SetBinaryMapping(
		self: Self,
		ListOfMappingToSet: list[int]
	) -> bool:
		
		self.BinaryBaseMap = ListOfMappingToSet

		return True

	def SetAlternateBinaryMappings(
		self: Self,
		AlternateBinaryMappings: list[list[int]]
	) -> bool:
		
		self.BinaryAlternateMappings = AlternateBinaryMappings

		return True

	def SetBinaryMapFromIndex(
		self: Self,
		IndexToSetBinaryMap: int,
		BinaryToSetMapping: int
	) -> bool:
		
		self.BinaryBaseMap[IndexToSetBinaryMap] = BinaryToSetMapping

		return True
	
	def SetBinaryMapFromName(
		self: Self,
		NameToSetBinary: str,
		BinaryToSetMapping: int
	) -> bool:
		
		self.SetBinaryMapFromIndex(self.GetIndexOfName(NameToSetBinary), BinaryToSetMapping)

		return True

	def GetIndexOfName(
		self: Self,
		NameToGetIndexOf: str
	) -> int:
		
		# try:
		return self.__ListOfNames__.index(NameToGetIndexOf)
		# except ValueError:
		# 	raise ValueError("AssemblerBaseClass(%s) does not contain %s" % (self.ClassName, NameToGetIndexOf))
	
	def GetNameOfIndex(
		self: Self,
		IndexToGetNameOf: int
	) -> str:
		
		try:
			return self.__ListOfNames__[IndexToGetNameOf]
		except ValueError:
			raise ValueError("AssemblerBaseClass(%s) does not have index of %s" % (self.ClassName, IndexToGetNameOf))

	def GetChildFromIndex(
		self: Self,
		IndexToGetChildFrom: int
	) -> "AssemblerBaseClass":
		
		try:
			return self.__ListOfChildren__[IndexToGetChildFrom]
		except ValueError:
			raise ValueError("AssemblerBaseClass(%s) does not have index %s" % (self.ClassName, IndexToGetChildFrom))
	
	def GetChildFromName(
		self: Self,
		NameToGetChildFrom: str
	) -> "AssemblerBaseClass":
		
		return self.GetChildFromIndex(self.GetIndexOfName(NameToGetChildFrom))

	def GetBinaryFromIndex(
		self: Self,
		IndexToGetBinaryFrom: int,
		AlternateMappingIndex: int = -1
	) -> int:
		
		try:
			if AlternateMappingIndex == -1:
				return self.BinaryBaseMap[IndexToGetBinaryFrom]
			else:
				return self.BinaryAlternateMappings[AlternateMappingIndex][IndexToGetBinaryFrom]
		except ValueError:
			raise ValueError("AssemblerBaseClass(%s) does not contain binary mapping index %s" % (self.ClassName, IndexToGetBinaryFrom))

	def GetBinaryFromName(
		self: Self,
		NameToGetBinaryFrom: str,
		AlternateMappingIndex: int = -1
	) -> int:
		
		return self.GetBinaryFromIndex(self.GetIndexOfName(NameToGetBinaryFrom), AlternateMappingIndex)

	def CallFunctionFromIndex(
		self: Self,
		IndexOfFunctionToCall: int,
		vArgs: list[str]
	):
		
		try:
			self.__ListOfCallableFunctions__[IndexOfFunctionToCall](vArgs)
		except ValueError:
			raise ValueError("AssemblerBaseClass(%s) does not have index of %s" % (self.ClassName, IndexOfFunctionToCall))

	def CallFunctionFromName(
		self: Self,
		NameOfFunctionToCall: str,
		vArgs: list[str]
	):
		
		IndexOfFunction: int = self.GetIndexOfName(NameOfFunctionToCall)

		self.CallFunctionFromIndex(IndexOfFunction, vArgs)
	
	def SetNamesAndMappingFrom2DList(
		self: Self,
		ListOfNamesAndBinaryMappings: list[list]
	) -> bool:
		
		DidSet: bool = self.SetNamesFromList(ListOfNamesAndBinaryMappings[0])
		DidSet = DidSet and self.SetBinaryMapping(ListOfNamesAndBinaryMappings[1])

		if not DidSet:
			raise Exception("Could not set appropriate lists.")
		
		return True

	def SetNamesAndAutoGenerateBinaryMapping(
		self: Self,
		ListOfNamesToAutoGenerateMappingFrom: list[str]
	) -> bool:
		
		DidSet: bool = self.SetNamesFromList(ListOfNamesToAutoGenerateMappingFrom)

		DirectBinaryMap: list[int] = [i for i, _ in enumerate(self.__ListOfNames__)]

		DidSet = DidSet and self.SetBinaryMapping(DirectBinaryMap)

		if not DidSet:
			raise Exception("Could not set Names and Binary Mappings.")

		return True

	def __str__(
		self: Self
	) -> str:
		OutputString: str = ""

		for Name in self.__ListOfNames__:
			OutputString += "%s = %s" % (Name, self.GetIndexOfName(Name))
		
		return OutputString
	
	def __repr__(
		self: Self
	) -> str:
		IndexedNames: str = "["
		BinaryMappings: str = "["

		for i, Name in enumerate(self.__ListOfNames__):
			IndexedNames += "%s:%s" % (Name, self.GetIndexOfName(Name))
			BinaryMappings += "%s:%s" % (Name, self.GetBinaryFromName(Name))

			if i != len(self.__ListOfNames__)-1:
				IndexedNames += ", "
				BinaryMappings += ", "
			else:
				IndexedNames += "]"
				BinaryMappings += "]"

		return "rasm.AssemblerBaseClass(\"%s\"): [NamesAndIndices:%s, BinaryMappings:%s]" % (self.ClassName, IndexedNames, BinaryMappings)

SchonHardwareFunctionsNames: list[str] = [
	"rom",
	"ram",
	"reg",
	"stack",
	"jump"
	"interrupt",
	"call",
	"return",
	"io",
]

SchonBaseFunctions: "AssemblerBaseClass" = AssemblerBaseClass("BaseFunctions")
SchonBaseFunctions.SetNamesAndAutoGenerateBinaryMapping(SchonHardwareFunctionsNames)

BaseTypes: list[str] = [
	"int",
	"float",
	"char",
	"string",
	"array",
]

TypeOperations: list[str] = [	#Base type, hence int
	"add",
	"sub",
	"mul",
	"div",
	"and",
	"or",
	"xor",
	"not",
	"shift",
	"compare"
]

#NOTE!
#Needs further planning for the operations for the different types!
TypeAlternativeOperations: list[list[str]] = [
	[	#float
		"add",
		"sub",
		"mul",
		"div",
		"compare"
	],
	[	#char
	],
	[	#String
		"append",
		"pop"
	],
	[	#Array
	]
]

SchonTypeOperations: "AssemblerBaseClass" = AssemblerBaseClass("Type Operations")
SchonTypeOperations.SetNamesAndAutoGenerateBinaryMapping(TypeOperations)
SchonTypeOperations.SetAlternateBinaryMappings(TypeAlternativeOperations)

SchonBaseTypes: "AssemblerBaseClass" = AssemblerBaseClass("Types")
SchonBaseTypes.SetNamesAndAutoGenerateBinaryMapping(BaseTypes)
SchonBaseTypes.SetChilden(SchonTypeOperations)

RegisterNames: list[str] = [
	"gpr",
	"aur",
	"skr",
	"spr"
]

SchonRegisters: "AssemblerBaseClass" = AssemblerBaseClass("Registers")
SchonRegisters.SetNamesAndAutoGenerateBinaryMapping(RegisterNames)

ToFromNames: list[str] = [
	"to",
	"from"
]

SchonToFrom: "AssemblerBaseClass" = AssemblerBaseClass("To/From")
SchonToFrom.SetNamesAndAutoGenerateBinaryMapping(ToFromNames)

StartEndIndicator: list[str] = [
	"{",
	"}"
]

SchonStartEndIndicator: "AssemblerBaseClass" = AssemblerBaseClass("Start/End indicator")
SchonStartEndIndicator.SetNamesFromList(StartEndIndicator)
