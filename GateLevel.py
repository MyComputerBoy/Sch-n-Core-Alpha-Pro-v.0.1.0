"""GateLevel.py -> Gate level implementation of the project
"""

import BaseCPUInfo
import math as m
import BasicMath as bm

bw = BaseCPUInfo.bit_width

def mod(n, b):
	return n-m.floor( n/b )* b 

#Logical and
def a(na, nb):
	return na * nb 

#Logical or
def o(na, nb):
	return m.ceil( na/2 + nb/2 )

#Logical xor
def x(na, nb):
	return mod( na + nb, 2 )

#Logical not
def n(na):
	return 1-na 

#Logical and in list format
def al(la, lb):
	q = []
	for i in range( len(la) ):
		q.append( a( la[i], lb[i] ) )
	return q

#Logical or in list format
def ol(la, lb):
	q = []
	for i in range( bw ):
		q.append( o( la[i], lb[i] ) )
	return q

#Logical xor in list format
def xl(la, lb):
	q = []
	for i in range( bw ):
		q.append( x( la[i], lb[i] ) )
	return q

#Logical not in list format
def nl(la):
	q = []
	for i in range( bw ):
		q.append( n( la[i] ) )
	return q

#Logical shift up/down
def shift(list, leng, ud=1):
	if ud == 1:
		tq = bm.dtb(m.floor( bm.btd(list) * 2**leng))
		return tq, list[mod(bw-leng,bw)]
	
	tq = bm.dtb(m.floor(bm.btd(list) / 2**leng))
	return tq, list[mod(leng-1,bw)]

def la(la, lb, ci=0):
	a = bm.btd(la)
	b = bm.btd(lb)
	tq = a + b + ci
	if m.sqrt(tq**2) >= 2**bw:
		ci = 1
	return bm.dtb(tq), ci

def ula(la, lb, ci=0):
	a = bm.user_btd(la)
	b = bm.user_btd(lb)
	tq = a + b + ci
	if m.sqrt(tq**2) >= 2**bw:
		ci = 1
	return bm.user_dtb(tq), ci

def ls(la, lb, ci=0):
	a = bm.btd(la)
	b = bm.btd(nl(lb))
	ci = 1-ci
	tq = a + b + ci
	if m.sqrt(tq**2) >= 2**bw:
		ci = 1
	return bm.dtb(tq), ci

def uls(la, lb, ci=0):
	a = bm.user_btd(la)
	b = bm.user_btd(lb)
	tq = a - b + ci
	if m.sqrt(tq**2) >= 2**bw:
		ci = 1
	return bm.user_dtb(tq), ci
def mul(al, bl):
	a = bm.btd(al)
	b = bm.btd(bl)
	return bm.dtb(a * b)
def umul(al, bl):
	a = bm.user_btd(al)
	b = bm.user_btd(bl)
	return bm.user_dtb(a * b)

def div(al, bl):
	a = bm.btd(al)
	b = bm.btd(bl)
	return bm.dtb(m.floor(a / b))

def udiv(al, bl):
	a = bm.user_btd(al)
	b = bm.user_btd(bl)
	return bm.user_dtb(a/b)
def uidiv(al, bl):
	a = bm.user_btd(al)
	b = bm.user_btd(bl)
	return bm.user_dtb(m.floor(a/b))