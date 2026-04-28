// Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386


program testB
{
    declare a,b;

    function f(in x)
    {
        function g()
        {
            print 1;   // τελικό ';' πριν από '}'
        }
        return x + 1
    }

    a := 1;
    b := f(in a)
}