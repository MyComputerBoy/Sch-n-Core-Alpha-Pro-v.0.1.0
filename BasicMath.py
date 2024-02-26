"""BasicMath.py -> Library for basic or low level math to be implemented
"""

import BaseCPUInfo
import math as m 
import GateLevel as g 
from enum import Enum			#Enum for elimination of magic numbers

class FloatComparisonStates(Enum):
	equals = 0
	greater_than = 1
	less_than = 2
	invalid_comparison = 3

bw = BaseCPUInfo.bit_width

string_index = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[];'\\,./{}:||<>? "

#Convert floating point to binary representation
def dtb( int, l=bw ):
	q = []
	for i in range( l ):
		q.append( g.mod( int,2 ) )
		int = m.floor( int/2 )
	return q

#Floating point conversion
def user_dtb(input):
	#Handle different inputs
	q = []
	sign = 1
	if input < 0:
		sign = 0
		input *= -1
	
	if input == 0:
		exponent = 128
	else:
		try:
			exponent = 128-m.floor(m.log(input, 2))
		except ValueError:
			print("Decimal to binary: Error: Domain error.")
			raise ValueError
	
	#Manage proper exponent and mantissa
	
	if input == 0:
		mantissa = 0
	else:
		mantissa = int(int(2**21*input)/2**(128-exponent))
	
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

def user_btd( input ):
	try:
		sign = input[0]
		exponent = btd(input[1:9])
		mantissa = btd(input[9:32])
	except IndexError:
		return 0
	
	v = 2**(128-exponent)*(mantissa/(2**21))
	
	if sign == 1:
		return v
	return -v

def user_ctb(char):
	return btd(string_index.index(char))

def user_btc(list):
	return string_index[btd(list)]

def float_compare(num_a, num_b):
	float_a = user_btd(num_a)
	float_b = user_btd(num_b)

	if float_a > float_b:
		return FloatComparisonStates.greater_than
	elif float_a == float_b:
		return FloatComparisonStates.equals
	elif float_a < float_b:
		return FloatComparisonStates.less_than
	else:
		return FloatComparisonStates.invalid_comparison

def char_read(num_a, num_b):
	return num_a[btd(num_b):btd(num_b)+8]

def char_Write(num_a, num_b, num_c):
	c_int = btd(num_c)
	num_a[0:8] = num_b[c_int:c_int+8]
	return num_a

def string_char_append(num_a, num_b):
	if btd(num_a[0:8]) == 0:
		num_a[0:8] = num_b[0:8]
	elif btd(num_a[8:16]) == 0:
		num_a[8:16] = num_b[0:8]
	elif btd(num_a[16:24]) == 0:
		num_a[16:24] = num_b[0:8]
	elif btd(num_a[24:32]) == 0:
		num_a[24:32] = num_b[0:8]
	return num_a

def string_string_append(num_a, num_b):
	if btd(num_a[0:8]) == 0:
		num_a[0:8] = num_b
	elif btd(num_a[8:16]) == 0:
		num_a[8:16] = num_b[:24]
	elif btd(num_a[16:24]) == 0:
		num_a[16:24] = num_b[:16]
	elif btd(num_a[24:32]) == 0:
		num_a[24:32] = num_b[:8]
	return num_a

def string_char_read(num_a, num_b):
	b_int = btd(num_b)
	return num_a[btd(b_int):b_int+8]

def string_char_write(num_a, num_b, num_c):
	c_int = btd(num_c)
	num_a[c_int:c_int+8] = num_b[:8] 
	return num_a

def bool_read(num_a, num_b):
	if btd(num_a[btd(num_b)]) == 0:
		return False 
	return True

def bool_write(num_a, num_b, value):
	num_a[btd(num_b)] = value
	return num_a

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
