//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

// Covers: incorrect condition grouping with ( ) instead of [ ]

program BadCond
{
    declare a,b;
    a := 1; b := 2;

    if (a = 1 and b = 2)
        a := a + 1
}