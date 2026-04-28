// Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

program LexerTest
{
    declare x, y, longVariableNameThatExceedsThirtyCharacters;

    /* Αυτό είναι ένα
       πολλαπλό σχόλιο */ //

    x := 32767; 
    y := -32767;
    longVariableNameThatExceedsThirtyCharacters := 1 // no semicolon here. We only use it between statements
}
