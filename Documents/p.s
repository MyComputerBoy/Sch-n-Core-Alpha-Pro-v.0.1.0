if jump
20
ramset to gpr 0 ram 3
ramset to gpr 1 ram 4
ramset to gpr 2 ram 4
compute div gpr 0 gpr 1 gpr 1
compute mul gpr 1 gpr 2 gpr 2
compute compare gpr 0 gpr 2 gpr 2
if ==
{
rom gpr 3 0
if jump
15
}
rom gpr 3 1
ramset from gpr 3 ram 4
ramset to gpr 0 ram 0
rom gpr 1 2
compute add gpr 1 gpr 0 gpr 0
irar gpr 0
if jump
33
ramset to gpr 0 ram 3
ramset to gpr 1 ram 4
ramset to gpr 2 ram 3
compute div gpr 0 gpr 1 gpr 0
compute mul gpr 0 gpr 1 gpr 0
compute sub gpr 2 gpr 0 gpr 0
ramset from gpr 0 ram 4
ramset to gpr 0 ram 1
rom gpr 1 3
compute add gpr 1 gpr 0 gpr 0
irar gpr 0
if jump
73
rom gpr 0 4
ramset from gpr 0 ram 9
ramset to gpr 1 ram 3
ramset from gpr 1 ram 5
ramset from gpr 1 ram 6
rom ram 7 5
rom ram 8 6
compute compare ram 6 ram 7 ram 7
if >
{
ramset to gpr 1 ram 5
ramset to gpr 2 ram 7
ramset from gpr 1 ram 3
ramset from gpr 2 ram 4
gbl gpr 0
ramset from gpr 0 ram 0
if jump
2
ramset to gpr 3 ram 4
rom gpr 4 7
compute compare gpr 3 gpr 4 gpr 4
if ==
{
rom gpr 0 8
ramset from gpr 0 ram 9
if jump
67
}
compute add ram 8 ram 7 ram 7
if jump
42
}
ramset to gpr 0 ram 9
ramset from gpr 0 ram 4
ramset to gpr 0 ram 2
rom gpr 1 9
compute add gpr 1 gpr 0 gpr 0
irar gpr 0
rom ram 10 10
rom ram 11 11
rom ram 12 12
compute compare ram 10 ram 11 ram 11
if >
{
ramset to gpr 0 ram 11
ramset from gpr 0 ram 3
gbl gpr 0
ramset from gpr 0 ram 2
if jump
35
ramset to gpr 0 ram 11
ramset to gpr 1 ram 4
rom gpr 2 13
compute compare gpr 1 gpr 2 gpr 2
if ==
{
io output gpr 0
}
ramset to gpr 0 ram 11
ramset from gpr 0 ram 3
rom ram 4 14
gbl gpr 0
ramset from gpr 0 ram 1
if jump
22
ramset to gpr 0 ram 11
ramset to gpr 1 ram 4
rom gpr 2 15
rom gpr 3 16
compute compare gpr 0 gpr 3 gpr 3
if ==
{
rom gpr 2 17
if jump
119
}
compute compare gpr 1 gpr 2 gpr 2
if ==
{
rom gpr 2 18
ramset to gpr 0 ram 11
compute add gpr 2 gpr 0 gpr 0
ramset from gpr 0 ram 11
}
compute add ram 12 ram 11 ram 11
if jump
76
}
eof 
1
0
4
4
1
2
1
1
0
4
150
3
2
1
10
3
3
0
2
