program test03whilefact
{
declare n,i,fact;
n := 5;
i := 1;
fact := 1;
while i <= n
{
    fact := fact * i;
    i := i + 1
};
print fact
}
