if jump
163
ramset to gpr 0 ram 1
rom gpr 1 0
rom gpr 2 1
rom gpr 3 2
rom gpr 4 3
rom gpr 5 4
rom gpr 6 5
rom gpr 7 6
rom gpr 8 7
rom gpr 9 8
rom gpr 10 9
compute compare gpr 0 gpr 1 gpr 1
if ==
{
rom gpr 32 10
io output gpr 32
rom gpr 32 11
io output gpr 32
rom gpr 32 12
io output gpr 32
rom gpr 32 13
io output gpr 32
rom gpr 32 14
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 2 gpr 2
if ==
{
rom gpr 32 15
io output gpr 32
rom gpr 32 16
io output gpr 32
rom gpr 32 17
io output gpr 32
rom gpr 32 18
io output gpr 32
rom gpr 32 19
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 3 gpr 3
if ==
{
rom gpr 32 20
io output gpr 32
rom gpr 32 21
io output gpr 32
rom gpr 32 22
io output gpr 32
rom gpr 32 23
io output gpr 32
rom gpr 32 24
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 4 gpr 4
if ==
{
rom gpr 32 25
io output gpr 32
rom gpr 32 26
io output gpr 32
rom gpr 32 27
io output gpr 32
rom gpr 32 28
io output gpr 32
rom gpr 32 29
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 5 gpr 5
if ==
{
rom gpr 32 30
io output gpr 32
rom gpr 32 31
io output gpr 32
rom gpr 32 32
io output gpr 32
rom gpr 32 33
io output gpr 32
rom gpr 32 34
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 6 gpr 6
if ==
{
rom gpr 32 35
io output gpr 32
rom gpr 32 36
io output gpr 32
rom gpr 32 37
io output gpr 32
rom gpr 32 38
io output gpr 32
rom gpr 32 39
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 7 gpr 7
if ==
{
rom gpr 32 40
io output gpr 32
rom gpr 32 41
io output gpr 32
rom gpr 32 42
io output gpr 32
rom gpr 32 43
io output gpr 32
rom gpr 32 44
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 8 gpr 8
if ==
{
rom gpr 32 45
io output gpr 32
rom gpr 32 46
io output gpr 32
rom gpr 32 47
io output gpr 32
rom gpr 32 48
io output gpr 32
rom gpr 32 49
io output gpr 32
if jump
157
}
compute compare gpr 0 gpr 9 gpr 9
if ==
{
rom gpr 32 50
io output gpr 32
rom gpr 32 51
io output gpr 32
rom gpr 32 52
io output gpr 32
rom gpr 32 53
io output gpr 32
rom gpr 32 54
io output gpr 32
rom gpr 32 55
io output gpr 32
}
rom gpr 32 56
io output gpr 32
ramset to gpr 0 ram 0
rom gpr 1 57
compute add gpr 1 gpr 0 gpr 0
irar gpr 0
rom ram 4 58
rom ram 5 59
rom ram 6 60
compute compare ram 4 ram 5 ram 5
if >
{
ramset to gpr 3 ram 5
ramset from gpr 3 ram 1
gbl gpr 0
ramset from gpr 0 ram 0
if jump
2
compute add ram 6 ram 5 ram 5
if jump
166
}
rom ram 1 61
gbl gpr 0
ramset from gpr 0 ram 0
if jump
2
rom ram 1 62
gbl gpr 0
ramset from gpr 0 ram 0
if jump
2
rom ram 1 63
gbl gpr 0
ramset from gpr 0 ram 0
if jump
2
eof 
0
7
8
10
12
13
26
27
37
1
4
10
14
17
17
17
17
31
17
17
31
4
4
4
31
17
9
7
9
17
17
27
21
17
17
17
19
21
21
25
14
17
17
17
14
6
4
4
4
14
17
27
31
31
14
4
0
4
38
0
1
10
8
12
