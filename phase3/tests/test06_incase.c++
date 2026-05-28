program test06incase
{
declare x,y;
x := 0;
y := 0;
incase
when: x < 3:
{
    x := x + 1
}
when: y < 2:
{
    y := y + 1
};
print x;
print y
}
