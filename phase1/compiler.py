# Eleutherios Iosifidis, 5233, cs215233
# Danai Chanlaridou 5386, cs215386


import sys # provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
from dataclasses import dataclass # dataclasses are used to represent a (reusable) data structure

# Globals that are required
token = None 
lexer = None

# Token
T_ID = "ID"
T_INT = "INT"
T_KEYWORD = "KEYWORD"
T_SYMBOL = "SYMBOL"
T_EOF = "EOF"

REL_OPS = {"=", "<", ">", "<=", ">=", "<>"}
ADD_OPS = {"+", "-"}
MUL_OPS = {"*", "/"}

KEYWORDS = {
    # program structure
    "program", "declare", "function",
    # flow
    "if", "else", "while",
    # case-family
    "switchcase", "whilecase", "incase", "untilcase", "forcase",
    "when", "default", "until",
    # i/o + return
    "return", "print", "input",
    # boolean
    "and", "or", "not",
    # parameter passing
    "in", "inout",
}

# Grammar uses ';'. Spec may mention Greek question mark; accept both.
GREEK_QMARK = "\u037E"  # ;
DECL_END = ";"          # normalized

SYMBOLS_1 = {
    "+", "-", "*", "/",
    "=", "<", ">", ",",
    "(", ")", "{", "}",
    ":", ";",
    "[", "]",
}

SYMBOLS_2 = {
    ":=", "<=", ">=", "<>",
}


@dataclass(frozen=True)
class Token:
    family: str
    lexeme: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.family}, {self.lexeme!r}, line={self.line}, col={self.col})"


# Below is the lexer
class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.current = self.text[self.pos] if self.text else None

    def error(self, msg: str) -> None:
        raise LexerError(f"[LEXER] line {self.line}, col {self.col}: {msg}")

    def advance(self) -> None:
        if self.current is None:
            return
        if self.current == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self):
        nxt = self.pos + 1
        return self.text[nxt] if nxt < len(self.text) else None

    def skip_whitespace(self) -> None:
        while self.current is not None and self.current.isspace():
            self.advance()

    def skip_comment(self) -> bool:
        # // comment
        if self.current == "/" and self.peek() == "/":
            while self.current is not None and self.current != "\n":
                self.advance()
            return True

        # /* comment */
        if self.current == "/" and self.peek() == "*":
            self.advance()  # /
            self.advance()  # *
            while True:
                if self.current is None:
                    self.error("Unterminated block comment /* ... */")
                if self.current == "*" and self.peek() == "/":
                    self.advance()  # *
                    self.advance()  # /
                    return True
                self.advance()

        return False

    def read_identifier_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.col
        buf = []

        # IDs start with alpha (we enter here only if isalpha)
        while self.current is not None and (self.current.isalpha() or self.current.isdigit()):
            buf.append(self.current)
            self.advance()

        lex = "".join(buf)
        if len(lex) > 30:
            lex = lex[:30]

        fam = T_KEYWORD if lex in KEYWORDS else T_ID
        return Token(fam, lex, start_line, start_col)

    def read_number(self) -> Token:
        # INTEGER in the TXT grammar: digits only (no sign)
        start_line, start_col = self.line, self.col
        buf = []
        while self.current is not None and self.current.isdigit():
            buf.append(self.current)
            self.advance()

        lex = "".join(buf)
        try:
            val = int(lex)
        except ValueError:
            self.error("Invalid integer literal")

        # check the range
        if val < -32767 or val > 32767:
            self.error(f"Integer out of range: {val}")

        return Token(T_INT, lex, start_line, start_col)

    def read_symbol(self) -> Token:
        start_line, start_col = self.line, self.col

        # normalize Greek question mark to ';'
        if self.current == GREEK_QMARK:
            self.advance()
            return Token(T_SYMBOL, DECL_END, start_line, start_col)

        two = (self.current or "") + (self.peek() or "")
        if two in SYMBOLS_2:
            self.advance()
            self.advance()
            return Token(T_SYMBOL, two, start_line, start_col)

        if self.current in SYMBOLS_1:
            ch = self.current
            self.advance()
            # normalize ';' to DECL_END
            if ch == ";":
                ch = DECL_END
            return Token(T_SYMBOL, ch, start_line, start_col)

        self.error(f"Unknown character: {self.current!r}")

    def next_token(self) -> Token:
        while self.current is not None:
            if self.current.isspace():
                self.skip_whitespace()
                continue

            if self.current == "/" and self.peek() in {"/", "*"}:
                if self.skip_comment():
                    continue

            if self.current.isalpha():
                return self.read_identifier_or_keyword()

            if self.current.isdigit():
                return self.read_number()

            return self.read_symbol()

        return Token(T_EOF, "EOF", self.line, self.col)


# PARSER (recursive descent)
# global: token
# Basic idea here is that when we consume a token immediately, we refill the token again and we repeat

class ParserError(Exception):
    pass


def syntax_error(msg: str) -> None:
    global token
    raise ParserError(f"[PARSER] line {token.line}, col {token.col}: {msg} (got {token})")


def advance_token() -> None:
    global token, lexer
    token = lexer.next_token()


def match_lexeme(lex: str) -> None:
    global token
    if token.lexeme == lex:
        advance_token()
    else:
        syntax_error(f"Expected {lex!r}")


def match_family(fam: str) -> None:
    global token
    if token.family == fam:
        advance_token()
    else:
        syntax_error(f"Expected token family {fam}")


def is_statement_start() -> bool:
    global token
    if token.family == T_ID:
        return True
    if token.family == T_KEYWORD and token.lexeme in {
        "if", "while",
        "switchcase", "whilecase", "incase", "forcase", "untilcase",
        "input", "print", "return",
    }:
        return True
    return token.lexeme == "{"


# GRAMMAR IMPLEMENTATION

def program():
    # program : 'program' ID programblock ;
    match_lexeme("program")
    match_family(T_ID)
    programblock()
    if token.family != T_EOF:
        syntax_error("Expected EOF at end of file")


def programblock():
    # programblock : '{' declarations functions statements_sequence '}' ;
    match_lexeme("{")
    declarations()
    functions()
    statements_sequence(stop_lexemes={"}"})
    match_lexeme("}")


def statements_sequence(stop_lexemes: set[str]):
    # statements_sequence : statement ( ';' statement )* | ε ;
    if token.lexeme in stop_lexemes or token.family == T_EOF:
        return  # ε
    if not is_statement_start():
        return  # ε (grammar allows empty)
    statement()
    while token.lexeme == DECL_END:
        match_lexeme(DECL_END)
        # after ';' must be another statement (unless we hit stop)
        if token.lexeme in stop_lexemes or token.family == T_EOF:
            syntax_error("Expected statement after ';'")
        statement()


def declarations():
    # declarations : ( 'declare' varlist ';')* ;
    while token.lexeme == "declare":
        match_lexeme("declare")
        varlist()          # varlist may be ε
        match_lexeme(DECL_END)


def varlist():
    # varlist : ID ( ',' ID )* | ε ;
    if token.family != T_ID:
        return  # ε
    match_family(T_ID)
    while token.lexeme == ",":
        match_lexeme(",")
        match_family(T_ID)


def functions():
    # functions : ( function )* ;
    while token.lexeme == "function":
        function_def()


def function_def():
    # function : 'function' ID formalpars programblock ;
    match_lexeme("function")
    match_family(T_ID)
    formalpars()
    programblock()


def formalpars():
    # formalpars : '(' formalparlist ')' ;
    match_lexeme("(")
    formalparlist()
    match_lexeme(")")


def formalparlist():
    # formalparlist : formalparitem ( ',' formalparitem )* | ε ;
    if token.lexeme not in {"in", "inout"}:
        return  # ε
    formalparitem()
    while token.lexeme == ",":
        match_lexeme(",")
        formalparitem()


def formalparitem():
    # formalparitem : 'in' ID | 'inout' ID ;
    if token.lexeme == "in":
        match_lexeme("in")
    elif token.lexeme == "inout":
        match_lexeme("inout")
    else:
        syntax_error("Expected 'in' or 'inout' in formal parameter")
    match_family(T_ID)


def statements():
    # statements : statement | '{' statements_sequence '}' ;
    if token.lexeme == "{":
        match_lexeme("{")
        statements_sequence(stop_lexemes={"}"})
        match_lexeme("}")
    else:
        statement()


def statement():
    # statement : assignment_stat | if_stat | while_stat | switchcase_stat | whilecase_stat
    #           | incase_stat | forcase_stat | untilcase_stat | input_stat | print_stat | return_stat ;
    if token.family == T_ID:
        assignment_stat()
        return

    if token.lexeme == "if":
        if_stat()
        return
    if token.lexeme == "while":
        while_stat()
        return

    if token.lexeme == "switchcase":
        switchcase_stat()
        return
    if token.lexeme == "whilecase":
        whilecase_stat()
        return
    if token.lexeme == "incase":
        incase_stat()
        return
    if token.lexeme == "forcase":
        forcase_stat()
        return
    if token.lexeme == "untilcase":
        untilcase_stat()
        return

    if token.lexeme == "input":
        input_stat()
        return
    if token.lexeme == "print":
        print_stat()
        return
    if token.lexeme == "return":
        return_stat()
        return

    if token.lexeme == "{":
        # allowed via statements(), but statement doesn't include blocks directly in grammar
        syntax_error("Block is a 'statements' form, not a 'statement'")

    syntax_error("Unknown statement start")


def assignment_stat():
    # assignment_stat : ID ':=' expression ;
    match_family(T_ID)
    match_lexeme(":=")
    expression()


def if_stat():
    # if_stat : 'if' condition statements elsepart ;
    match_lexeme("if")
    condition()
    statements()
    elsepart()


def elsepart():
    # elsepart : 'else' statements | ε ;
    if token.lexeme == "else":
        match_lexeme("else")
        statements()


def while_stat():
    # while_stat : 'while' condition statements ;
    match_lexeme("while")
    condition()
    statements()


def switchcase_stat():
    # switchcase_stat : 'switchcase'
    #   ( 'when' condition ':' statements )*
    #   'default' ':' statements ;
    match_lexeme("switchcase")
    while token.lexeme == "when":
        match_lexeme("when")
        condition()
        match_lexeme(":")
        statements()
    match_lexeme("default")
    match_lexeme(":")
    statements()


def whilecase_stat():
    # whilecase_stat : 'whilecase'
    #   ( 'when' condition ':' statements )*
    #   'default' ':' statements ;
    match_lexeme("whilecase")
    while token.lexeme == "when":
        match_lexeme("when")
        condition()
        match_lexeme(":")
        statements()
    match_lexeme("default")
    match_lexeme(":")
    statements()


def incase_stat():
    # incase_stat : 'incase' ( 'when' condition ':' statements )* ;
    match_lexeme("incase")
    while token.lexeme == "when":
        match_lexeme("when")
        condition()
        match_lexeme(":")
        statements()


def forcase_stat():
    # forcase_stat : 'forcase' ID '=' INTEGER ( 'when' condition ':' statements )* ;
    match_lexeme("forcase")
    match_family(T_ID)
    match_lexeme("=")
    match_family(T_INT)  # INTEGER
    while token.lexeme == "when":
        match_lexeme("when")
        condition()
        match_lexeme(":")
        statements()


def untilcase_stat():
    # untilcase_stat : 'untilcase'
    #   ( 'when' condition ':' statements )*
    #   'until' condition ;
    match_lexeme("untilcase")
    while token.lexeme == "when":
        match_lexeme("when")
        condition()
        match_lexeme(":")
        statements()
    match_lexeme("until")
    condition()


def input_stat():
    # input_stat : 'input' ID ;
    match_lexeme("input")
    match_family(T_ID)


def print_stat():
    # print_stat : 'print' expression ;
    match_lexeme("print")
    expression()


def return_stat():
    # return_stat : 'return' expression ;
    match_lexeme("return")
    expression()


# Conditions & Expressions

def condition():
    # condition : boolterm ( 'or' boolterm )* ;
    boolterm()
    while token.lexeme == "or":
        match_lexeme("or")
        boolterm()


def boolterm():
    # boolterm : boolfactor ( 'and' boolfactor )* ;
    boolfactor()
    while token.lexeme == "and":
        match_lexeme("and")
        boolfactor()


def boolfactor():
    # boolfactor :
    #   'not' '[' condition ']'
    # | '[' condition ']'
    # | expression relational_oper expression ;
    if token.lexeme == "not":
        match_lexeme("not")
        match_lexeme("[")
        condition()
        match_lexeme("]")
        return

    if token.lexeme == "[":
        match_lexeme("[")
        condition()
        match_lexeme("]")
        return

    expression()
    if token.lexeme not in REL_OPS:
        syntax_error("Expected relational operator in boolfactor")
    op = token.lexeme
    match_lexeme(op)
    expression()


def expression():
    # expression : optional_sign term ( add_oper term )* ;
    optional_sign()
    term()
    while token.lexeme in ADD_OPS:
        match_lexeme(token.lexeme)
        term()


def optional_sign():
    # optional_sign : add_oper | ε ;
    if token.lexeme in ADD_OPS:
        match_lexeme(token.lexeme)


def term():
    # term : factor ( mul_oper factor )* ;
    factor()
    while token.lexeme in MUL_OPS:
        match_lexeme(token.lexeme)
        factor()


def factor():
    # factor : INTEGER | '(' expression ')' | ID idtail ;
    if token.family == T_INT:
        match_family(T_INT)
        return
    if token.lexeme == "(":
        match_lexeme("(")
        expression()
        match_lexeme(")")
        return
    if token.family == T_ID:
        match_family(T_ID)
        idtail()
        return
    syntax_error("Expected INTEGER, '(' expression ')', or ID")


def idtail():
    # idtail : actualpars | ε ;
    if token.lexeme == "(":
        actualpars()


def actualpars():
    # actualpars : '(' actualparlist ')' ;
    match_lexeme("(")
    actualparlist()
    match_lexeme(")")


def actualparlist():
    # actualparlist : actualparitem ( ',' actualparitem )* | ε ;
    if token.lexeme not in {"in", "inout"}:
        return  # ε
    actualparitem()
    while token.lexeme == ",":
        match_lexeme(",")
        actualparitem()


def actualparitem():
    # actualparitem : 'in' expression | 'inout' ID ;
    if token.lexeme == "in":
        match_lexeme("in")
        expression()
        return
    if token.lexeme == "inout":
        match_lexeme("inout")
        match_family(T_ID)
        return
    syntax_error("Expected 'in' or 'inout' in actual parameters")


# Main program

def main():
    global lexer, token

    if len(sys.argv) != 2:
        print("Usage: python casepp_phase1.py <file.c++>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"Cannot open file: {e}")
        sys.exit(1)

    lexer = Lexer(text)
    token = lexer.next_token()

    try:
        program()
        print("Compilation successfully completed (Phase 1: lexical + syntax).")
    except (LexerError, ParserError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()