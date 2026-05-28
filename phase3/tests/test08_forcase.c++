program test08forcase
{
declare i,sum;
sum := 0;
forcase i = 5
when: i <= 5:
{
    sum := sum + i
};
print sum
}
