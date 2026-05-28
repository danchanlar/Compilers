program test10nested
{
declare a,b,r;
function outer(in x, inout y)
{
declare local;
function inner(in z)
{
    local := local + z;
    return local
}
local := x + y;
y := y + 1;
return inner(in y)
}
a := 5;
b := 2;
r := outer(in a, inout b);
print r;
print b
}
