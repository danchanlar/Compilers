program test07untilcase
{
declare x,sum;
x := 0;
sum := 0;
untilcase
when: x < 4:
{
    x := x + 1;
    sum := sum + x
}
until x >= 4;
print sum
}
