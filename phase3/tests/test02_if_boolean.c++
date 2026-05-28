program test02ifbool
{
declare a,b,c;
a := 5;
b := 10;
c := 0;
if [a < b and b >= 10] or not [a = 5]
{
    c := 1
}
else
{
    c := 2
};
print c
}
