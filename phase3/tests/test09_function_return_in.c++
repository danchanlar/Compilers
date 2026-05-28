program test09funcret
{
declare a,b,r;
function addmul(in x, in y)
{
declare z;
z := x + y * 2;
return z
}
a := 4;
b := 6;
r := addmul(in a, in b);
print r
}
