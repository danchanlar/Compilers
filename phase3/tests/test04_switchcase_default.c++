program test04switchcase
{
declare x,y;
x := 3;
y := 0;
switchcase:
when: x = 1:
{
    y := 10
}
when: x = 2:
{
    y := 20
}
default:
{
    y := 99
};
print y
}
