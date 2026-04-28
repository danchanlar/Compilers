//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

// Covers: while + nested if, correct ; separators. 

program WhileTest
{
    declare i,sum;

    i := 1; sum := 0;

    while i <= 5
    {
        sum := sum + i;
        i := i + 1
    };

    print sum
}