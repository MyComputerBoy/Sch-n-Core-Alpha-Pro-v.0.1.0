mark start
io from 0 gpr 0
io from 1 gpr 1
io from 2 gpr 2
stack push gpr 0
stack push gpr 2
rom gpr 3 0
compute gpr 1 compare gpr 3 gpr 3
if ==
{
rom gpr 0 1
io to 10 gpr 0
add 
}
rom gpr 3 1
compute gpr 1 compare gpr 3 gpr 3
if ==
{
rom gpr 0 2
io to 10 gpr 0
sub
}
rom gpr 3 2
compute gpr 1 compare gpr 3 gpr 3
if ==
{
rom gpr 0 3
io to 10 gpr 0
mul 
}
rom gpr 3 3
compute gpr 1 compare gpr 3 gpr 3
if ==
{
rom gpr 0 4
io to 10 gpr 0
div 
}
rom gpr 3 4
compute gpr 1 compare gpr 3 gpr 3
if ==
{
rom gpr 0 5
io to 10 gpr 0
eof_mark
}
mark loop_end
stack pop gpr 0
io to 0 gpr 0
start
mark eof_mark
eof
mark add
stack pop gpr 0
stack pop gpr 1
compute gpr 1 add gpr 0 gpr 2
stack push gpr 2
loop_end
mark sub
stack pop gpr 0
stack pop gpr 1
compute gpr 1 sub gpr 0 gpr 2
stack push gpr 2
loop_end
mark mul
stack pop gpr 0
stack pop gpr 1
compute gpr 1 mul gpr 0 gpr 2
stack push gpr 2
loop_end
mark div
stack pop gpr 0
stack pop gpr 1
rom gpr 2 1000
compute gpr 1 mul gpr 2 gpr 1
compute gpr 1 div gpr 0 gpr 2
stack push gpr 2
loop_end