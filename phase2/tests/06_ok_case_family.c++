//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

//Covers: switchcase/whilecase/incase/untilcase/forcase with blocks and without “finally ;” inside blocks.

program CaseFamily
{
    declare a,b;

    a := 2; b := 0;

    switchcase
        when a = 1 : b := 10
        when a = 2 : { b := 20; b := b + 1 }
        default: b := 99
    ;

    incase
        when b > 10 : b := b + 5
        when b < 0  : b := 0
    ;

    untilcase
        when b < 30 : b := b + 3
        until b >= 30
    ;

    forcase b = 3
        when a = 2 : a := a + 1
        when a = 3 : a := a + 2
}