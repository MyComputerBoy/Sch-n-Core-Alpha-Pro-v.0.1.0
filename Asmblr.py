import math as m

class Assembler:
	def __init__(self):
		#Static variables
		_AssemblerName_: str = "Schön Core"			#Do not change!
		_AssemblerCore_: str = "Alpha Pro"			#Do not change!
		_AssemblerCoreVersion_: str = "v.0.1.0"		#Do not change!
		_AssemblerVersion_: str = "0.1.0"			#Do not change!

		#Initialisation of dynamic variables

		#File paths and names
		FileToAssemblePath: str
		FileToAssembleName: str
		FileDestinationPath: str
		FileDestinationName: str

		#Worker variables
		FileRead: list[str] = []
		SymbolicFile: list[str] = []
		WorkerFile: list[str] = []
		FinalFileToWrite: list[str] = []
	
