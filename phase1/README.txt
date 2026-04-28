CASE++ PHASE 1 – LEXICAL & SYNTAX ANALYZER
========================================

Eleutherios Iosifidis (AM: 5233, cs215233)
Danai Chanlaridou (AM: 5386, cs215386)

Description
-----------
This program implements **Phase 1** of a compiler for the CASE++ language.
It includes:

• A **Lexical Analyzer (Lexer)**  
• A **Syntax Analyzer (Parser)** using recursive descent  

The program checks whether a given CASE++ source file is:
✔ lexically correct  
✔ syntactically correct  

No semantic analysis or code generation is performed in this phase.


Language Features Supported
---------------------------
The lexer and parser support the full CASE++ Phase 1 grammar, including:

Program structure:
• program
• declare
• function

Statements:
• assignment
• if / else
• while
• switchcase
• whilecase
• incase
• forcase
• untilcase
• input
• print
• return
• blocks { }

Expressions:
• arithmetic expressions (+, -, *, /)
• relational operators (=, <, >, <=, >=, <>)
• boolean expressions (and, or, not)

Parameter passing:
• in
• inout

--------------------------------------------------

Lexer Details
-------------
Token families:
• ID        → Identifiers
• INT       → Integer constants
• KEYWORD   → Reserved words
• SYMBOL    → Operators and punctuation
• EOF       → End of file

Supported comments:
• Single-line: // comment
• Multi-line: /* comment */

Additional Notes:
• Integers must be in range [-32767, 32767]
• Identifiers are truncated to 30 characters
• Greek question mark (;) is accepted and normalized to ';'

--------------------------------------------------

Parser Details
--------------
• Implemented using **recursive descent**
• Grammar strictly follows the CASE++ specification
• Detects and reports syntax errors with:
  - line number
  - column number
  - unexpected token

--------------------------------------------------

How to Run
----------
1. Make sure you have **Python 3.8+** installed.
2. Open a terminal in the project directory.
3. Run the program using:

   python casepp_phase1.py <filename>

Example:
   python casepp_phase1.py test.c++

--------------------------------------------------

Output
------
• If the program is correct:

  Compilation successfully completed (Phase 1: lexical + syntax).

• If an error occurs:

  [LEXER] line X, col Y: <error description>
  OR
  [PARSER] line X, col Y: <error description>

--------------------------------------------------

Error Handling
--------------
The program terminates immediately on:
• Lexical errors (invalid characters, unterminated comments, invalid numbers)
• Syntax errors (grammar violations)

--------------------------------------------------

Limitations
-----------
• No symbol table
• No semantic checks
• No intermediate or final code generation

These will be handled in later phases.
