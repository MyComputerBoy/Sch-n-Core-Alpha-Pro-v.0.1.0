"""BasicMath.py -> Library for basic or low level math to be implemented
"""

import BaseCPUInfo

import math as m 
import GateLevel as g 

bw = BaseCPUInfo.bit_width

#Convert floating point to binary representation
def dtb( int, l=bw ):
	q = []
	for i in range( l ):
		q.append( g.mod( int,2 ) )
		int = m.floor( int/2 )
	return q

def user_dtb(input, l=bw):
	#Handle different inputs
	q = []
	sign = 1
	if input < 0:
		sign = 0
		input *= -1
	
	if input == 0:
		exponent = 255
	else:
		try:
			exponent = 255-m.floor(m.log(input, 2))
		except ValueError:
			print("Deciman to binary: Error: Domain error.")
			raise ValueError
	
	#Manage proper exponent and mantissa
	
	mantissa = int(int(2**21*input)/int(2**(255-exponent)))
	
	#Append to q
	q.append(sign)
	output_exponent = dtb(exponent, 8)
	output_mantissa = dtb(mantissa, 23)
	for i, e in enumerate(output_exponent):
		q.append(e)
	for i, e in enumerate(output_mantissa):
		q.append(e)
	
	return q

#Convert binary list to floating point
def btd( list, leng = bw ):
	q = 0
	for i in range( leng ):
		try:
			q += 2**i * list[i]
		except Exception:
			q += 0
	return q

def user_btd( input, l=bw ):
	q = 0
	try:
		sign = input[0]
		exponent = input[1:9]
		mantissa = input[9:32]
	except IndexError:
		return 0
	
	v = 2**(256-btd(exponent))*(btd(mantissa)/(2**22))
	
	if sign == 1:
		return v
	return -v

#Bitwise reverse list
def reverse( list ):
	q = [0 for i in list]
	for i, e in enumerate(list):
		q[len(list)-i-1] = e
	return q

#Binary list to string, format being either example: ■ ■■ , or 1011 or with spaces inbetween as in example: ■   ■ ■  , or 1 0 1 1 
def blts( input_list, add_space=False, gui=False ):
	q = ""
	for i in input_list:
		if gui:
			if i == 1:
				q += "■"
			else:
				q += " "
		else:
			q += str( i )
		
		#If 
		if add_space:
			q += " "
	return q

#Zero out binary input and set bit at index btd(list) to one
def btib( list, len=bw ):
	temp = btd( list )
	q = [0 for i in range( len )]
	q[temp] = 1
	return q

#Binary list to string in reverse to blts(list)
def btbs( list ):
	q = ""
	for i in list:
		q = str( i ) + q
	return q

def bla(la, lb):
	q = []
	for i in la:
		q.append(i)
	for i in lb:
		q.append(i)
	return q

#Define hexadecimal characters
HexadecimalLowerCaseChars = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
HexadecimalUpperCaseChars = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]

#Convert hexadecimal to floating point
def htd( string, bool=False ):
	q = 0
	if bool:
		tstring = ""
		for i in string:
			tstring = i + tstring
		string = tstring
	iint = 0
	for i in string:
		try:
			t = HexadecimalLowerCaseChars.index(i)
		except Exception:
			t = HexadecimalUpperCaseChars.index(i)
		q += 16**(iint) * t
		iint += 1
	return q
