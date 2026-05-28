case++ compiler - Phase 3
==========================

Team
----
Eleutherios Iosifidis, 5233, cs215233
Danai Chanlaridou, 5386, cs215386


1. Description
--------------
This program is a compiler for the case++ programming language and implements
Phase 3 of the project. For an input source file with the .c++ extension, it
performs the following stages:

1) Lexical analysis
2) Syntax analysis
3) Semantic checks
4) Intermediate code generation using quads
5) Symbol table construction
6) Final RISC-V assembly code generation

If the input program is syntactically and semantically correct, the compiler
produces three output files:

- .int   : intermediate code in quad format
- .symb  : symbol table dump
- .asm   : final RISC-V assembly code


2. How to run
-------------
The compiler is executed from the command line using the following format:

    python3 compiler.py input.c++

Example:

    python3 compiler.py test01_arithmetic.c++

If compilation is completed successfully, the following message is printed:

    Compilation successfully completed.
    Intermediate code written to: test01_arithmetic.int
    Symbol table written to: test01_arithmetic.symb
    Final RISC-V code written to: test01_arithmetic.asm

If an error is detected, the compiler prints an appropriate error message,
including the line and column where the problem was found.


3. Output files
---------------

3.1 The .int file
-----------------
The .int file contains the intermediate code in quad format. Each quad has the
following form:

    number: operator, operand1, operand2, result

Example:

    5: +, a, b, T_1
    6: :=, T_1, _, c

The first quad computes a + b and stores the result in the temporary variable
T_1. The second quad assigns the value of T_1 to the variable c.

The compiler uses quads for arithmetic operations, assignments, jumps,
conditions, input, output, return values, parameters, and function calls.

The main quad operations generated are:

- begin_block : beginning of a program block or function block
- end_block   : end of a program block or function block
- halt        : program termination
- :=          : assignment
- +, -, *, /  : arithmetic operations
- if=, if<, if>, if<=, if>=, if<> : conditional jumps
- jump        : unconditional jump
- inp         : input from keyboard
- out         : output of a value
- retv        : return value from a function
- par         : parameter passing
- call        : function call


3.2 The .symb file
------------------
The .symb file contains the symbol table. For each scope, it prints:

- the scope name
- the nesting level
- the frame length
- the starting quad
- the quad where the executable statements begin
- the ending quad
- the entities that belong to the scope

The entities stored in the symbol table are:

- Variable      : normal variable
- TempVariable  : temporary variable created by the compiler
- Parameter     : function parameter
- Function      : function entity

For each variable, temporary variable, and parameter, the compiler stores an
offset inside the activation record. For each function, the compiler stores its
formal parameters, starting quad, frame length, and nesting level.


3.3 The .asm file
-----------------
The .asm file contains the final RISC-V assembly code. The generated assembly
can be used in RARS/Venus-style simulators.

The final code includes:

- labels of the form L_1, L_2, ...
- arithmetic instructions
- branch instructions
- input/output instructions using ecall
- activation record management
- function calls using jal
- function returns using jr ra

At the beginning of the program, space is allocated on the stack for the main
program activation record. The gp register points to the base of the main
activation record, while sp points to the current activation record.


4. Lexical analysis
-------------------
The lexer reads the source file character by character and produces tokens.

The compiler supports:

- identifiers
- integer constants
- reserved keywords
- operators
- symbols
- single-line comments using //
- multi-line comments using /* ... */

Integer constants must be in the following range:

    -32767 to 32767

Identifiers are truncated to 30 characters, according to the implementation.

The lexer ignores spaces, tabs, and new lines. It also normalizes the Greek
question mark ; to the regular semicolon ; so that it is recognized correctly as
a separator.

If an unknown character, an unterminated comment, or a nested block comment is
found, the compiler reports a lexical error.


5. Syntax analysis
------------------
The parser is a recursive descent parser. This means that each grammar rule of
the case++ language is implemented by a corresponding Python function.

The general form of a program is:

    program program_name {
        declarations
        functions
        statements
    }

Variable declarations are supported using:

    declare a, b, c;

Functions with parameters are supported using:

    function f(in x, inout y) {
        ...
        return expression
    }

Parameters declared as in are passed by value, while parameters declared as
inout are passed by reference.


6. Supported statements
-----------------------

6.1 Assignment
--------------
An assignment has the following form:

    x := expression

The compiler generates an assignment quad:

    :=, expression_place, _, x


6.2 if - else
-------------
The if statement supports both simple selection and selection with else:

    if condition statement

or

    if condition statement else statement

Intermediate code generation for if statements uses true/false lists and
backpatching.


6.3 while
---------
The while statement repeats its body while the condition is true:

    while condition statement

The compiler stores the starting quad of the condition, so that at the end of
the body it can generate a jump back to the beginning.


6.4 switchcase
--------------
The switchcase statement checks the when conditions sequentially and then
executes the default branch if no previous case has been selected.

General form:

    switchcase
    when condition:
        statement
    default:
        statement

After a successful when branch, a jump is generated so that execution continues
after the end of the switchcase statement and does not fall through to the next
cases.


6.5 whilecase
-------------
The whilecase statement repeatedly checks its when branches. When a when branch
is executed, control returns to the beginning of the whilecase statement. If no
when condition is true, the default branch is executed.


6.6 incase
----------
The incase statement checks all when branches. If at least one when branch is
executed, the whole incase statement is repeated from the beginning. For this
reason, the compiler creates a temporary flag variable that records whether a
case was executed.


6.7 untilcase
-------------
The untilcase statement executes its when branches and then checks the until
condition. If the until condition is false, control returns to the beginning of
the statement.


6.8 forcase
-----------
In this compiler, the forcase statement has the following form:

    forcase i = N
    when condition:
        statement

The control variable i is initialized to 1 and is increased until it becomes
greater than N. If N is less than 1, the compiler reports a semantic error.


6.9 input
---------
The input statement reads an integer from the keyboard:

    input x

The generated quad is:

    inp, x, _, _


6.10 print
----------
The print statement prints the value of an expression:

    print expression

The generated quad is:

    out, expression_place, _, _


6.11 return
-----------
The return statement returns a value from a function:

    return expression

A return statement is not allowed inside the main program block. If it is used
there, the compiler reports a semantic error.


7. Expressions and conditions
-----------------------------
The compiler supports arithmetic expressions with:

- addition +
- subtraction -
- multiplication *
- division /
- optional sign + or -
- parentheses
- variables
- integer constants
- function calls

Conditions support:

- relational operators =, <>, <, >, <=, >=
- logical and
- logical or
- logical not
- grouping with [ and ]

Conditions are implemented using backpatching. In other words, the compiler first
generates quads with unknown jump targets and later fills in the correct target
labels when they become known.


8. Semantic checks
------------------
The compiler performs basic semantic checks, such as:

- whether an identifier has been declared before it is used
- whether there is a duplicate declaration in the same scope
- whether a function is used correctly as a function
- whether a variable is used correctly as an lvalue
- whether the number of actual parameters in a function call is correct
- whether the parameter passing modes match the function definition
- whether an inout parameter receives a real variable and not an expression
- whether return is not used inside the main program block
- whether the value used in forcase is at least 1

If a semantic error is detected, compilation stops and the compiler prints a
message describing the problem.


9. Symbol table and scopes
--------------------------
The compiler creates a separate scope for:

- the main program
- each function

Each scope has its own nesting level and a pointer to its parent scope. This
allows the compiler to support nested functions/scopes, because it can search
for variables in outer scopes.

Each variable, parameter, and temporary variable receives an offset. These
offsets are later used during final code generation in order to access the
correct memory positions inside activation records.


10. Final RISC-V code generation
--------------------------------
The final code generator translates the quads into RISC-V assembly code.

The main registers used are:

- sp : points to the current activation record
- gp : points to the activation record of the main program
- ra : return address from a function
- a0 : value register used for input/output ecalls
- a7 : system call code for ecall
- t0, t1, t2, t6 : temporary registers

Input and output are implemented using RISC-V ecalls:

- a7 = 5  : read integer
- a7 = 1  : print integer
- a7 = 11 : print character
- a7 = 10 : exit

After each print, the compiler also prints a newline character.

For function calls, the compiler creates an activation record. The activation
record contains:

- space for the return value
- dynamic link
- return address
- static link
- parameters
- local variables
- temporary variables

The static link is used to access variables that belong to outer scopes.


11. Tests
---------
Ten test programs were used to check the implementation. For each test, there is
a .c++ input file and the corresponding generated .int, .symb, and .asm files.

The tests are:

1) test01_arithmetic.c++
   Tests variable declarations, arithmetic operations, assignments, and print.
   It shows that temporary variables, arithmetic quads, and RISC-V code for
   simple expressions are generated correctly.

2) test02_if_boolean.c++
   Tests if statements, logical operators, and boolean expressions.
   It shows that relational operators, jumps, and backpatching of true/false
   lists work correctly.

3) test03_while_factorial.c++
   Tests the while statement through a factorial calculation.
   It shows that the loop returns correctly to the beginning of the condition
   and that multiplication and variable updates are handled correctly.

4) test04_switchcase_default.c++
   Tests switchcase together with default.
   It verifies that when a when branch is executed, control jumps after the end
   of the switchcase statement instead of continuing to the next cases.

5) test05_whilecase.c++
   Tests the whilecase statement.
   It shows that after a successful when branch, execution returns to the
   beginning of the whilecase statement, while the default branch is available
   when no condition is true.

6) test06_incase.c++
   Tests the incase statement.
   It shows the use of the temporary flag variable and the repetition of incase
   when at least one when branch is executed.

7) test07_untilcase.c++
   Tests the untilcase statement.
   It shows that the when branches are executed and then the until condition is
   checked in order to decide whether the repetition should continue.


12. Suggested way to run all tests
----------------------------------
From the folder where the files are located, all tests can be executed using the
following commands.

On Linux/macOS:

    for f in test*.c++; do
        python3 compiler.py "$f"
    done

On Windows PowerShell:

    Get-ChildItem test*.c++ | ForEach-Object { python compiler.py $_.Name }

After running the tests, each test should have the corresponding output files:

    testXX_name.int
    testXX_name.symb
    testXX_name.asm


13. Conclusion
--------------
This implementation completes a compiler for the case++ language, starting from
the source program and reaching final RISC-V assembly code generation. The
compiler stores intermediate code in quads, constructs a symbol table with
scopes and offsets, performs semantic checks, and uses the symbol table
information to generate final code with correct activation record management,
parameter passing, return values, and nested scope support.
