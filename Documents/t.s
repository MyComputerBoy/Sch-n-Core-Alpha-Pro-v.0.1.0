rom gpr 0 5
rom gpr 1 3
stack push gpr 0
adding gpr 1
eof
def adding
{
stack pop gpr 0
stack pop gpr 1
compute gpr 0 add gpr 1 gpr 2
stack push gpr 2
}