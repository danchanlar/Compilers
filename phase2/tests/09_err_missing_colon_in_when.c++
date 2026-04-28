//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386


// Covers: incorrect syntax when condition statements without :

program BadWhen
{
    declare a;
    a := 1;

    switchcase
        when a = 1  a := 2
        default: a := 3
    ;
}