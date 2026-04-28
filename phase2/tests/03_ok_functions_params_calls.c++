//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

// Covers: function, nested function, formal params in/inout, call as factor, return.

program FunTest
{
    declare a,b,c;

    function inc(in x, inout y)
    {
        function inner(in k)
        {
            print k;
            return k + 1
        }
        y := y + 1;
        c := inner(in x);
        return x + y
    }

    a := 5;
    b := 2;
    c := inc(in a, inout b);
    print c
}