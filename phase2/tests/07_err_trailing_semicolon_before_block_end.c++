//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386


// Covers: classic error ; before } ⇒ should output “Expected statement after ';'”.

program BadSemi
{
    declare a;
    { a := 1; }   // FAIL: τελικό ';' πριν από '}'
}