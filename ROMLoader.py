
import basecpuinf

import bm

bw = basecpuinf.bit_width
bf = basecpuinf.base_folder
exeff = basecpuinf.executable_files_folder

fh = open( bf + "rom/fn.txt", "r" )
lines = fh.readlines()
fh.close()
filename = lines[0]

def rom( rw, index, list = [] ):
	if rw == 0:
		fh = open( bf + exeff + filename + ".schonexe", "r" )
		lines = fh.readlines()
		fh.close()
		q = lines[index]
		q = q.strip()
		q = [int( i ) for i in q]
		return q