# Eleutherios Iosifidis, 5233, cs215233
# Danai Chanlaridou 5386, cs215386

import sys
from dataclasses import dataclass
from typing import Optional, List, Tuple, Set

# =========================
# GLOBALS
# =========================
token = None
lexer = None
function_depth = 0

# =========================
# TOKEN
# =========================
T_ID = "ID"
T_INT = "INT"
T_KEYWORD = "KEYWORD"
T_SYMBOL = "SYMBOL"
T_EOF = "EOF"

REL_OPS = {"=", "<", ">", "<=", ">=", "<>"}
ADD_OPS = {"+", "-"}
MUL_OPS = {"*", "/"}

KEYWORDS = {
    "program", "declare", "function",
    "if", "else", "while",
    "switchcase", "whilecase", "incase", "untilcase", "forcase",
    "when", "default", "until",
    "return", "print", "input",
    "and", "or", "not",
    "in", "inout",
}

GREEK_QMARK = "\u037E"  # ;
DECL_END = ";"          # normalized
MAX_ID_LEN = 30
INT_MIN = -32767
INT_MAX = 32767

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

# =========================
# QUADS / IR
# =========================

@dataclass
class Quad:
    op: str
    x: str
    y: str
    z: str


quads: List[Quad] = []
temp_counter = 0


def reset_compilation_state() -> None:
    global quads, temp_counter, function_depth
    quads = []
    temp_counter = 0
    function_depth = 0


def nextquad() -> int:
    return len(quads)


def genquad(op: str, x: str = "_", y: str = "_", z: str = "_") -> int:
    quads.append(Quad(op, x, y, z))
    return len(quads) - 1


def newtemp() -> str:
    global temp_counter
    temp_counter += 1
    return f"T_{temp_counter}"


def makelist(i: int) -> List[int]:
    return [i]


def merge(l1: List[int], l2: List[int]) -> List[int]:
    return l1 + l2


def backpatch(lst: List[int], label: int) -> None:
    for i in lst:
        quads[i].z = str(label)


# =========================
# TOKEN STRUCT
# =========================

@dataclass(frozen=True)
class Token:
    family: str
    lexeme: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.family}, {self.lexeme!r}, line={self.line}, col={self.col})"


# =========================
# LEXER
# =========================
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
        if self.current == "/" and self.peek() == "/":
            while self.current is not None and self.current != "\n":
                self.advance()
            return True

        if self.current == "/" and self.peek() == "*":
            self.advance()
            self.advance()
            while True:
                if self.current is None:
                    self.error("Unterminated block comment /* ... */")
                if self.current == "/" and self.peek() == "*":
                    self.error("Nested block comments are not allowed")
                if self.current == "*" and self.peek() == "/":
                    self.advance()
                    self.advance()
                    return True
                self.advance()

        return False

    def read_identifier_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.col
        buf = []
        while self.current is not None and (self.current.isalpha() or self.current.isdigit()):
            buf.append(self.current)
            self.advance()

        lex = "".join(buf)
        if len(lex) > MAX_ID_LEN:
            lex = lex[:MAX_ID_LEN]

        fam = T_KEYWORD if lex in KEYWORDS else T_ID
        return Token(fam, lex, start_line, start_col)

    def read_number(self) -> Token:
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

        if val > INT_MAX:
            self.error(f"Integer out of range: {val}")

        return Token(T_INT, lex, start_line, start_col)

    def read_symbol(self) -> Token:
        start_line, start_col = self.line, self.col

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


# =========================
# PARSER
# =========================
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


def match_family(fam: str) -> str:
    global token
    if token.family == fam:
        lex = token.lexeme
        advance_token()
        return lex
    syntax_error(f"Expected token family {fam}")


def parse_signed_integer_constant() -> int:
    sign = 1
    if token.lexeme in ADD_OPS:
        if token.lexeme == "-":
            sign = -1
        match_lexeme(token.lexeme)

    if token.family != T_INT:
        syntax_error("Expected integer constant")

    value = int(match_family(T_INT)) * sign
    if value < INT_MIN or value > INT_MAX:
        syntax_error(f"Integer constant out of range [{INT_MIN}, {INT_MAX}]")
    return value


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


# =========================
# GRAMMAR + SEMANTIC ACTIONS
# =========================

def program():
    match_lexeme("program")
    prog_name = match_family(T_ID)

    genquad("begin_block", prog_name, "_", "_")
    programblock()
    genquad("end_block", prog_name, "_", "_")

    if token.family != T_EOF:
        syntax_error("Expected EOF at end of file")



def programblock():
    match_lexeme("{")
    declarations()
    functions()
    statements_sequence(stop_lexemes={"}"}, require_nonempty=True)
    match_lexeme("}")



def statements_sequence(stop_lexemes: Set[str], require_nonempty: bool = False):
    if token.lexeme in stop_lexemes or token.family == T_EOF:
        if require_nonempty:
            syntax_error("Expected at least one statement")
        return

    if not is_statement_start():
        if require_nonempty:
            syntax_error("Expected statement")
        return

    statement()
    while token.lexeme == DECL_END:
        match_lexeme(DECL_END)
        if token.lexeme in stop_lexemes or token.family == T_EOF:
            syntax_error("Expected statement after ';'")
        statement()



def declarations():
    while token.lexeme == "declare":
        match_lexeme("declare")
        if token.family != T_ID:
            syntax_error("Expected at least one identifier after 'declare'")
        varlist_collect()
        match_lexeme(DECL_END)



def varlist_collect() -> List[str]:
    names = [match_family(T_ID)]
    while token.lexeme == ",":
        match_lexeme(",")
        names.append(match_family(T_ID))
    return names



def functions():
    while token.lexeme == "function":
        function_def()



def function_def():
    global function_depth

    match_lexeme("function")
    fname = match_family(T_ID)

    genquad("begin_block", fname, "_", "_")
    formalpars()
    function_depth += 1
    try:
        programblock()
    finally:
        function_depth -= 1
    genquad("end_block", fname, "_", "_")



def formalpars():
    match_lexeme("(")
    formalparlist()
    match_lexeme(")")



def formalparlist():
    if token.lexeme not in {"in", "inout"}:
        return
    formalparitem()
    while token.lexeme == ",":
        match_lexeme(",")
        formalparitem()



def formalparitem():
    if token.lexeme == "in":
        match_lexeme("in")
        match_family(T_ID)
    elif token.lexeme == "inout":
        match_lexeme("inout")
        match_family(T_ID)
    else:
        syntax_error("Expected 'in' or 'inout' in formal parameter")



def statements():
    if token.lexeme == "{":
        match_lexeme("{")
        statements_sequence(stop_lexemes={"}"}, require_nonempty=True)
        match_lexeme("}")
    else:
        statement()



def statement():
    if token.lexeme == "{":
        statements()
        return

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

    syntax_error("Unknown statement start")



def assignment_stat():
    lhs = match_family(T_ID)
    match_lexeme(":=")
    place = expression()
    genquad(":=", place, "_", lhs)



def if_stat():
    match_lexeme("if")
    tlist, flist = condition()

    backpatch(tlist, nextquad())
    statements()

    if token.lexeme == "else":
        j = genquad("jump", "_", "_", "_")
        backpatch(flist, nextquad())
        match_lexeme("else")
        statements()
        backpatch([j], nextquad())
    else:
        backpatch(flist, nextquad())



def while_stat():
    match_lexeme("while")
    start = nextquad()
    tlist, flist = condition()
    backpatch(tlist, nextquad())
    statements()
    genquad("jump", "_", "_", str(start))
    backpatch(flist, nextquad())



def switchcase_stat():
    match_lexeme("switchcase")
    exit_list: List[int] = []

    while token.lexeme == "when":
        match_lexeme("when")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        exit_list.append(genquad("jump", "_", "_", "_"))
        backpatch(flist, nextquad())

    match_lexeme("default")
    match_lexeme(":")
    statements()
    backpatch(exit_list, nextquad())



def whilecase_stat():
    match_lexeme("whilecase")
    start = nextquad()

    while token.lexeme == "when":
        match_lexeme("when")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        genquad("jump", "_", "_", str(start))
        backpatch(flist, nextquad())

    match_lexeme("default")
    match_lexeme(":")
    statements()



def incase_stat():
    match_lexeme("incase")
    start = nextquad()
    flag = newtemp()
    genquad(":=", "0", "_", flag)

    while token.lexeme == "when":
        match_lexeme("when")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        genquad(":=", "1", "_", flag)
        statements()
        backpatch(flist, nextquad())

    q = genquad("if=", flag, "1", "_")
    backpatch([q], start)



def untilcase_stat():
    match_lexeme("untilcase")
    start = nextquad()

    while token.lexeme == "when":
        match_lexeme("when")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        backpatch(flist, nextquad())

    match_lexeme("until")
    tlist_u, flist_u = condition()
    backpatch(flist_u, nextquad())
    genquad("jump", "_", "_", str(start))
    backpatch(tlist_u, nextquad())



def forcase_stat():
    match_lexeme("forcase")
    var = match_family(T_ID)
    match_lexeme("=")
    n_val = parse_signed_integer_constant()
    if n_val < 1:
        syntax_error("forcase integer_value must be a positive integer >= 1")
    n = str(n_val)

    genquad(":=", "1", "_", var)
    start = nextquad()

    q_if = genquad("if>", var, n, "_")

    while token.lexeme == "when":
        match_lexeme("when")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        backpatch(flist, nextquad())

    t = newtemp()
    genquad("+", var, "1", t)
    genquad(":=", t, "_", var)
    genquad("jump", "_", "_", str(start))

    quads[q_if].z = str(nextquad())



def input_stat():
    match_lexeme("input")
    name = match_family(T_ID)
    genquad("inp", name, "_", "_")



def print_stat():
    match_lexeme("print")
    place = expression()
    genquad("out", place, "_", "_")



def return_stat():
    if function_depth <= 0:
        syntax_error("'return' is only allowed inside a function")
    match_lexeme("return")
    place = expression()
    genquad("retv", place, "_", "_")


# =========================
# CONDITIONS & EXPRESSIONS
# =========================

def condition() -> Tuple[List[int], List[int]]:
    t1, f1 = boolterm()
    while token.lexeme == "or":
        match_lexeme("or")
        backpatch(f1, nextquad())
        t2, f2 = boolterm()
        t1 = merge(t1, t2)
        f1 = f2
    return t1, f1



def boolterm() -> Tuple[List[int], List[int]]:
    t1, f1 = boolfactor()
    while token.lexeme == "and":
        match_lexeme("and")
        backpatch(t1, nextquad())
        t2, f2 = boolfactor()
        f1 = merge(f1, f2)
        t1 = t2
    return t1, f1



def boolfactor() -> Tuple[List[int], List[int]]:
    if token.lexeme == "not":
        match_lexeme("not")
        match_lexeme("[")
        t, f = condition()
        match_lexeme("]")
        return f, t

    if token.lexeme == "[":
        match_lexeme("[")
        t, f = condition()
        match_lexeme("]")
        return t, f

    e1 = expression()
    if token.lexeme not in REL_OPS:
        syntax_error("Expected relational operator in boolfactor")
    op = token.lexeme
    match_lexeme(op)
    e2 = expression()

    q1 = genquad(f"if{op}", e1, e2, "_")
    q2 = genquad("jump", "_", "_", "_")
    return makelist(q1), makelist(q2)



def expression() -> str:
    sign = optional_sign()
    p = term()
    if sign == "-":
        t = newtemp()
        genquad("-", "0", p, t)
        p = t

    while token.lexeme in ADD_OPS:
        op = token.lexeme
        match_lexeme(op)
        p2 = term()
        t = newtemp()
        genquad(op, p, p2, t)
        p = t
    return p



def optional_sign() -> Optional[str]:
    if token.lexeme in ADD_OPS:
        s = token.lexeme
        match_lexeme(s)
        return s
    return None



def term() -> str:
    p = factor()
    while token.lexeme in MUL_OPS:
        op = token.lexeme
        match_lexeme(op)
        p2 = factor()
        t = newtemp()
        genquad(op, p, p2, t)
        p = t
    return p



def factor() -> str:
    if token.family == T_INT:
        return match_family(T_INT)
    if token.lexeme == "(":
        match_lexeme("(")
        p = expression()
        match_lexeme(")")
        return p
    if token.family == T_ID:
        name = match_family(T_ID)
        return idtail(name)
    syntax_error("Expected INTEGER, '(' expression ')', or ID")



def idtail(name: str) -> str:
    if token.lexeme != "(":
        return name

    args = actualpars_collect()
    ret = newtemp()
    genquad("par", ret, "RET", "_")
    for mode, val in args:
        if mode == "in":
            genquad("par", val, "CV", "_")
        else:
            genquad("par", val, "REF", "_")
    genquad("call", name, "_", "_")
    return ret



def actualpars_collect() -> List[Tuple[str, str]]:
    match_lexeme("(")
    items = actualparlist_collect()
    match_lexeme(")")
    return items



def actualparlist_collect() -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    if token.lexeme not in {"in", "inout"}:
        return items
    items.append(actualparitem_collect())
    while token.lexeme == ",":
        match_lexeme(",")
        items.append(actualparitem_collect())
    return items



def actualparitem_collect() -> Tuple[str, str]:
    if token.lexeme == "in":
        match_lexeme("in")
        place = expression()
        return ("in", place)
    if token.lexeme == "inout":
        match_lexeme("inout")
        name = match_family(T_ID)
        return ("inout", name)
    syntax_error("Expected 'in' or 'inout' in actual parameters")


# =========================
# OUTPUT
# =========================

def write_int_file(src_path: str) -> str:
    if src_path.lower().endswith(".c++"):
        out_path = src_path[:-3] + "int"
    else:
        out_path = src_path + ".int"

    with open(out_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(quads):
            f.write(f"{i}: ({q.op}, {q.x}, {q.y}, {q.z})\n")
    return out_path


# =========================
# MAIN
# =========================

def compile_file(path: str) -> str:
    global lexer, token

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise OSError(f"Cannot open file: {e}") from e

    reset_compilation_state()
    lexer = Lexer(text)
    token = lexer.next_token()
    program()
    return write_int_file(path)



def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <file.c++>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        int_path = compile_file(path)
        print("Compilation successfully completed (lexical + syntax + IR).")
        print(f"Intermediate code written to: {int_path}")
    except (OSError, LexerError, ParserError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
