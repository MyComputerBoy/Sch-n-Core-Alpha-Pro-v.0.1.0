mark loop
io from 0 gpr 0
io from 1 gpr 1
io from 2 gpr 2
rom gpr 3 0
compute gpr 1 compare alur 2 stk 3
if ==
{
compute gpr 0 add gpr 1 gpr 2
}
rom gpr 3 1
compute gpr 1 compare gpr 3 gpr 3
if ==
{
compute gpr 0 sub gpr 1 gpr 2
}
rom gpr 3 2
compute gpr 1 compare gpr 3 gpr 3
if ==
{
end
}
io to 2 gpr 2
loop 
mark end
eof