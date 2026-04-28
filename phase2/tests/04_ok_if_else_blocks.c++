//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

// Covers: if/else, statements as block { ... }, boolfactor with [ ], not.

program IfTest
{
    declare a,b;

    a := 1; b := 10;

    if [a = 1 and not [b < 5]]
    {
        b := b + 1; a := a + 2
    }
    else
    {
        b := b - 1
    };

    print a; print b
}
