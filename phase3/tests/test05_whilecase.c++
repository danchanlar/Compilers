program test05whilecase
{
declare x,sum;
x := 1;
sum := 0;
whilecase:
when: x < 4:
{
    sum := sum + x;
    x := x + 1
}
default:
{
    sum := sum + 100
};
print sum
}
