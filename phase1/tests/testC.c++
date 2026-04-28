// Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

program testC
{
    declare a,b;

    a := 1;
    b := 2;

    while a < 10
        if b <> 22 or (b >= 23 and b <= 24)   // it must be [ ... ] not ( ... )
            a := a + 1;

    print a
}