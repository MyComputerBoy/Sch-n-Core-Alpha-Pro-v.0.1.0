"""emu.py -> Refactoring and cleaning of my emulator for Schön Core Alpha Pro v.0.1.0 Python emulator
"""

#Import libraries
import BaseCPUInfo				#Basic CPU information
import math
# import BasicMath				#Basic math library
# import GateLevel
import logging as lgn			#Logging for custom exceptions
from typing import Self
from enum import Enum

LOGLEVEL = lgn.WARNING

lgn.basicConfig(format="%(levelname)s: %(message)s", level=lgn.DEBUG)
lgn.getLogger().setLevel(LOGLEVEL)

lgn.debug("Imported libraries.")

#Basic CPU info variables
GLOBALBUSWIDTH: int = BaseCPUInfo.bit_width

GLOBALBASEFOLDERLOCATION: str = BaseCPUInfo.base_folder
GLOBALPROGRAMSFOLDERLOCATION: str = BaseCPUInfo.programs_folder
GLOBALEXECUTABLEFILESFOLDERLOCATION: str = BaseCPUInfo.executable_files_folder

EXECUTABLEFILEEXTENSIONNAME: str = ".schonexe1"

class SchonCoreAlphaBus():
	def __init__(
		self: Self,
		BusWidth: int = GLOBALBUSWIDTH,
		InternalReferenceName: str = "GenericBus"
	):
		
		#Basic bus management for internal use
		self.NameOfBus: str = InternalReferenceName
		self.BusWidth: int = BusWidth

		self._Value: int = 0
	
	@property
	def Value(
		self: Self
	) -> int:
		
		return self.Value

	@Value.setter
	def Value(
		self: Self,
		Value: int
	) -> None:
		
		self.Value = Value % (2**self.BusWidth)
	
	def __getitem__(
		self: Self,
		BitIndex: int
	) -> int:
		
		return math.floor(self._Value / (2**BitIndex)) % 2
	
	def __setitem__(
		self: Self,
		BitIndex: int,
		Value: bool
	) -> None:
		
		BitMask: int = (2**self.BusWidth) - 1
		BitMask -= 2**BitIndex

		self._Value = self._Value and BitMask
		self._Value = self._Value or (2**BitIndex * Value)

	def __repr__(self) -> str:
		return "SchonCoreAlphaBus(%s).Value = %s" % (self.NameOfBus, self._Value)
	
	def __str__(self) -> str:
		return str(self._Value)

class SchonCoreAlphaRegister():
	def __init__(
		self: Self,
		RegisterName: str,
		RegisterDepth: int,
	) -> None:
		
		self.Name = RegisterName
		self.RegisterDepth: int = RegisterDepth
		self._Registers: list["SchonCoreAlphaBus"] = [SchonCoreAlphaBus(GLOBALBUSWIDTH, "%s: %s" % (self.Name, i)) for i in range(RegisterDepth)]
	
	def __setitem__(
		self: Self,
		Index: int,
		Value: int
	) -> None:
		
		self._Registers[Index].Value = Value
	
	def __getitem__(
		self: Self,
		Index: int
	) -> int:
		
		return self._Registers[Index].Value

	def __setattr__(self, Index: str, Value: int) -> None:
		self._Registers[int(Index)].Value = Value

	def __getattribute__(self, Index: str) -> SchonCoreAlphaBus:
		return self._Registers[int(Index)]

class ALUControlInputNames(Enum):
	ProgramCounterIncrement = 0
	Increment = 1
	Decrement = 2
	FunctionBitOne = 3
	FunctionBitTwo = 4
	FunctionBitThree = 5
	FunctionBitFour = 6
	SpecialFunctionVariable = 7
	SetFlags = 8

class EmulatorArithmeticLogicUnit():
	def __init__(
		self: Self,
		NameOfEmulatorALU: str,
	) -> None:
		
		self.NAME = NameOfEmulatorALU
		
		self.MainInputBus: "SchonCoreAlphaBus" = SchonCoreAlphaBus(GLOBALBUSWIDTH, "EmulatorALUMainInputBus")
		self.MainControlInputBus: "SchonCoreAlphaBus" = SchonCoreAlphaBus(GLOBALBUSWIDTH, "EmulatorALUMainControlInputBus")

		DidResetALURegisters: bool = self.ResetALURegisters()

		if not DidResetALURegisters:
			raise SystemError("Could not reset ALU internal registers.")
		
		self._WorkingBRegister: int = 0

	def ResetALURegisters(
		self: Self,
	) -> bool:
		
		self.BRegister: "SchonCoreAlphaRegister" = SchonCoreAlphaRegister("EmulatorALUBRegister", 1)
		self.OutputRegister: "SchonCoreAlphaRegister" = SchonCoreAlphaRegister("EmulatorALUOutputRegister", 1)
		self.FlagsRegister: "SchonCoreAlphaRegister" = SchonCoreAlphaRegister("EmulatorALUFlagsRegister", 1)

		return True
	
	def DoSingleClockCycle(
		self: Self
	) -> bool:
		
		if self.MainControlInputBus[ALUControlInputNames.ProgramCounterIncrement.value] or self.MainControlInputBus[ALUControlInputNames.Increment.value] or self.MainControlInputBus[ALUControlInputNames.Decrement.value]:
			self._WorkingBRegister = 1

		return True

class Emulator():
	def __init__(
		self: Self,
		NameOfEmulator: str,
		SizeOfEmulatedRAMInWords: int,
		SizeOfEmulatorROMInWords: int,
	) -> None:
		
		self.NAME = NameOfEmulator

		self._MainBus: "SchonCoreAlphaBus" = SchonCoreAlphaBus(GLOBALBUSWIDTH, "MainEmulatorBus")
		self._GPIOBus: "SchonCoreAlphaBus" = SchonCoreAlphaBus(GLOBALBUSWIDTH, "EmulatorGPIOBus")

		self.__ROMSIZE__: int = SizeOfEmulatorROMInWords
		DidResetROM: bool = self.ResetROM()

		if not DidResetROM:
			raise SystemError("Could not reset main emulator ROM.")

		#Based on the instruction set, there are room for 16 registers per type of register, meaning a combined 64 registers available
		self.__AMOUNTOFREGISTERSPERREGISTERTYPE__: int = 16
		self.__NAMESOFREGISTERTYPES__: list[str] = [
			"gpr",
			"alr",
			"str",
			"spr"
		]

		self.Registers: dict[str, "SchonCoreAlphaRegister"] = {}

		DidResetRegisters: bool = self.ResetRegisters()
		if not DidResetRegisters:
			raise SystemError("Could not reset main emulator registers.")

		#NOTE!
		#The CPU does not address to individual bytes, but to words, meaning accessing individual bytes is not trivial
		#Since this is a 32 bit CPU, the standard 2**32 words of ram is possible, hence 16GB worth of ram possible

		self.__RAMSIZE__: int = SizeOfEmulatedRAMInWords
		DidResetRAM: bool = self.ResetRAM()
		if not DidResetRAM:
			raise SystemError("Could not reset main emulator RAM.")
	
	def ResetROM(
		self: Self
	) -> bool:
		
		self.__ROM = SchonCoreAlphaRegister("MainEmulatorROM", self.__ROMSIZE__)

		return True
	
	def ResetRAM(
		self: Self
	) -> bool:
		
		self.RAM = SchonCoreAlphaRegister("MainEmulatorRAM", self.__RAMSIZE__)

		return True
	
	def ResetRegisters(
		self: Self
	) -> bool:
		
		for NameOfRegister in self.__NAMESOFREGISTERTYPES__:
			self.Registers[NameOfRegister] = SchonCoreAlphaRegister(NameOfRegister, self.__AMOUNTOFREGISTERSPERREGISTERTYPE__)
		
		return True
	
	def LoadFileToROM(
		self: Self,
		PathToROMFile: str
	) -> bool:
		
		FileHandler = open(PathToROMFile, "r")
		WordsRead = FileHandler.readlines()
		FileHandler.close()

		for i, Word in enumerate(WordsRead):
			self.__ROM[i] = int(Word)
		
		return True
	
