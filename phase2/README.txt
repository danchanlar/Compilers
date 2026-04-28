case++ Compiler – Phase 2

Eleutherios Iosifidis, 5233, cs215233
Danai Chanlaridou, 5386, cs215386

This assignment implements the case++ compiler for Phase 2.
The implementation follows the grammar and the fundamental rules of the case++ language.
The compiler performs three main tasks:

Lexical analysis
Syntax analysis
Intermediate code generation

The program reads a source code file with the .c++ extension.
It first checks whether the file is lexically correct.
Then it checks whether it is syntactically correct.
If no errors are found, it produces intermediate code in the form of quads.
The intermediate code is written to a file with the .int extension.
The implementation is contained in a single Python file, compiler.py.
This file includes the lexer, the parser, and the intermediate code generation.

Lexer
The lexer recognizes:

identifiers
integer constants
reserved keywords
symbols and operators
comments

The supported comment types are:

// ...
/* ... */

Nested block comments are not supported.
The Greek question mark is recognized as a statement terminator.
For identifiers, only the first 30 characters are taken into account.
Integer constants are checked to ensure they fall within the valid language range.

Parser
The parser is implemented using recursive descent parsing.
It checks whether the program correctly follows the case++ grammar.
It supports:

program
declare
function
assignment
if ... else
while
switchcase
whilecase
incase
untilcase
forcase
input
print
return
expressions
conditions with and, or, not
formal parameters with in and inout
actual parameters with in and inout

Functions can be nested.
Returning a value is done using return and is allowed only inside a function.
Function calls can be used within arithmetic expressions.

Intermediate Code Generation
During parsing, quads are generated.
Quads are used for:

assignments
arithmetic operations
comparisons
jumps
control flow structures
function calls
parameter passing
return values
input and output

For conditions and control flow, backpatching is used.
Temporary variables are created for intermediate results.
For function calls, the following markers are used:

CV for call by value
REF for call by reference
RET for the return value

Error Handling
The compiler reports lexical and syntax error messages.
The messages include line and column numbers, making it easier to locate the error.
Execution
The compiler is executed from the terminal using:
python compiler.py <file.c++>