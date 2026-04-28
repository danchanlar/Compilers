// Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

program testA
{
    declare a,b;
    declare c;

    function addmul(in x, inout y)
    {
        function nested1(in n)
        {
            function nested2()
            {
                print 123
            }
            print (n + (+2)) * 3
        }

        y := x + 1;
        c := nested1(in x);
        return y + 10
    }

    a := 1;
    b := 2 + a * a / (2 - a - (2*a));
    c := addmul(in a, inout b);

    while b < 10
        if b <> 22 or [b >= 23 and b <= 24]
            b := b + 1;

    input b;
    print c;

    switchcase
        when a = 1 : a := a + 1
        when a = 2 : a := a + 2
        when a = 3 : {
                        a := a + 1;
                        a := a + 2
                     }
        default: a := a + 10
    ;

    whilecase
        when a = 1 : a := a + 1
        when a = 2 : a := a + 2
        default: a := a + 3
    ;

    incase
        when a = 1 : a := a + 1
        when a = 2 : a := a + 2
    ;

    untilcase
        when a = 1 : a := a + 1
        when a = 2 : a := a + 2
        until a > 100
    ;

    forcase b = 10
        when a = 1 : a := a + 1
        when a = 2 : {
                        a := a + 1;
                        a := a + 2
                     }
}