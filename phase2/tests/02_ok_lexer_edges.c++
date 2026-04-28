//  Eleutherios Iosifidis, 5233, cs215233
// Danai Chanlaridou 5386, cs215386

// Covers: comments // and /*...*/, long ID (truncated at 30), numbers, input/print

program LexerEdges
{
    declare x, longVariableNameThatExceedsThirtyCharacters;

    /* block comment
       spanning lines */
    // line comment

    x := 32767;
    longVariableNameThatExceedsThirtyCharacters := 1;
    input x; print x
}