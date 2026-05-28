# Eleutherios Iosifidis, 5233, cs215233
# Danai Chanlaridou 5386, cs215386


import sys
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Set, Dict, Union

# =========================
# GLOBALS
# =========================
token = None
lexer = None

current_scope = None
all_scopes: List["Scope"] = []
program_scope = None
program_name = None

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

GREEK_QMARK = "\u037E"  # Greek question mark: ;
DECL_END = ";"          # normalized statement/declaration separator

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

# Maps every quad index to the scope where it belongs. This is needed by
# final-code generation in order to resolve variables and static links.
quad_scope: Dict[int, "Scope"] = {}


def nextquad() -> int:
    return len(quads)


def genquad(op: str, x: str = "_", y: str = "_", z: str = "_") -> int:
    global current_scope
    quads.append(Quad(op, x, y, z))
    idx = len(quads) - 1
    if current_scope is not None:
        quad_scope[idx] = current_scope
    return idx


def newtemp() -> str:
    global temp_counter
    temp_counter += 1
    name = f"T_{temp_counter}"
    if current_scope is None:
        raise SemanticError("Internal error: temporary created without active scope")
    current_scope.add_temp(name)
    return name


def makelist(i: int) -> List[int]:
    return [i]


def merge(l1: List[int], l2: List[int]) -> List[int]:
    return l1 + l2


def backpatch(lst: List[int], label: int) -> None:
    for i in lst:
        quads[i].z = str(label)

# =========================
# SYMBOL TABLE
# =========================

class SemanticError(Exception):
    pass


@dataclass
class FormalParam:
    name: str
    mode: str  # "CV" for in, "REF" for inout


@dataclass
class Entity:
    name: str
    kind: str


@dataclass
class Variable(Entity):
    offset: int

    def __init__(self, name: str, offset: int):
        super().__init__(name, "variable")
        self.offset = offset


@dataclass
class TempVariable(Entity):
    offset: int

    def __init__(self, name: str, offset: int):
        super().__init__(name, "temporary")
        self.offset = offset


@dataclass
class Parameter(Entity):
    mode: str
    offset: int

    def __init__(self, name: str, mode: str, offset: int):
        super().__init__(name, "parameter")
        self.mode = mode
        self.offset = offset


@dataclass
class Function(Entity):
    formal_params: List[FormalParam] = field(default_factory=list)
    start_quad: Optional[int] = None
    frame_length: int = 0
    nesting_level: int = 0
    scope: Optional["Scope"] = None

    def __init__(self, name: str, nesting_level: int):
        super().__init__(name, "function")
        self.formal_params = []
        self.start_quad = None
        self.frame_length = 0
        self.nesting_level = nesting_level
        self.scope = None


@dataclass
class Scope:
    name: str
    nesting_level: int
    parent: Optional["Scope"]
    owner_function: Optional[Function] = None
    entities: List[Entity] = field(default_factory=list)
    offset: int = 16
    frame_length: int = 16
    start_quad: Optional[int] = None
    statements_start_quad: Optional[int] = None
    end_quad: Optional[int] = None

    def lookup_local(self, name: str) -> Optional[Entity]:
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None

    def add_entity(self, entity: Entity) -> Entity:
        if self.lookup_local(entity.name) is not None:
            raise SemanticError(
                f"[SEMANTIC] Duplicate identifier '{entity.name}' in scope '{self.name}'"
            )
        self.entities.append(entity)
        return entity

    def allocate_offset(self) -> int:
        off = self.offset
        self.offset += 4
        self.frame_length = self.offset
        return off

    def add_variable(self, name: str) -> Variable:
        return self.add_entity(Variable(name, self.allocate_offset()))

    def add_temp(self, name: str) -> TempVariable:
        return self.add_entity(TempVariable(name, self.allocate_offset()))

    def add_parameter(self, name: str, mode: str) -> Parameter:
        return self.add_entity(Parameter(name, mode, self.allocate_offset()))


def enter_scope(name: str, owner_function: Optional[Function] = None) -> Scope:
    global current_scope, all_scopes
    level = 0 if current_scope is None else current_scope.nesting_level + 1
    scope = Scope(name=name, nesting_level=level, parent=current_scope, owner_function=owner_function)
    current_scope = scope
    all_scopes.append(scope)
    if owner_function is not None:
        owner_function.scope = scope
    return scope


def exit_scope() -> Scope:
    global current_scope
    if current_scope is None:
        raise SemanticError("Internal error: exit_scope without active scope")
    scope = current_scope
    scope.frame_length = scope.offset
    if scope.owner_function is not None:
        scope.owner_function.frame_length = scope.frame_length
    current_scope = scope.parent
    return scope


def add_function_to_current_scope(name: str) -> Function:
    if current_scope is None:
        raise SemanticError("Internal error: function without active parent scope")
    func = Function(name, current_scope.nesting_level + 1)
    current_scope.add_entity(func)
    return func


def resolve_entity(name: str, from_scope: Optional[Scope] = None) -> Tuple[Entity, Scope]:
    scope = from_scope if from_scope is not None else current_scope
    while scope is not None:
        ent = scope.lookup_local(name)
        if ent is not None:
            return ent, scope
        scope = scope.parent
    raise SemanticError(f"[SEMANTIC] Undeclared identifier '{name}'")


def require_lvalue(name: str) -> Entity:
    ent, _ = resolve_entity(name)
    if isinstance(ent, Function):
        raise SemanticError(f"[SEMANTIC] Function '{name}' cannot be used as a variable")
    return ent


def require_function(name: str) -> Function:
    ent, _ = resolve_entity(name)
    if not isinstance(ent, Function):
        raise SemanticError(f"[SEMANTIC] Identifier '{name}' is not a function")
    return ent


def is_ancestor_scope(ancestor: Scope, child: Scope) -> bool:
    scope = child
    while scope is not None:
        if scope is ancestor:
            return True
        scope = scope.parent
    return False

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
        self.comment_depth = 0

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
                    self.error("Nested block comments are not supported")
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
        if len(lex) > 30:
            lex = lex[:30]
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

        if val < -32767 or val > 32767:
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


def optional_lexeme(lex: str) -> bool:
    global token
    if token.lexeme == lex:
        advance_token()
        return True
    return False


def match_family(fam: str) -> str:
    global token
    if token.family == fam:
        lex = token.lexeme
        advance_token()
        return lex
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

# =========================
# GRAMMAR + SEMANTIC ACTIONS
# =========================

def program():
    global program_scope, program_name
    match_lexeme("program")
    prog_name = match_family(T_ID)
    program_name = prog_name

    program_scope = enter_scope(prog_name)
    q_begin = genquad("begin_block", prog_name, "_", "_")
    program_scope.start_quad = q_begin

    programblock()
    q_halt = genquad("halt", "_", "_", "_")
    quad_scope[q_halt] = program_scope
    q_end = genquad("end_block", prog_name, "_", "_")
    program_scope.end_quad = q_end
    quad_scope[q_end] = program_scope

    exit_scope()

    if token.family != T_EOF:
        syntax_error("Expected EOF at end of file")


def programblock():
    match_lexeme("{")
    declarations()
    functions()
    if current_scope is None:
        raise SemanticError("Internal error: programblock without scope")
    current_scope.statements_start_quad = nextquad()
    statements_sequence(stop_lexemes={"}"})
    match_lexeme("}")


def statements_sequence(stop_lexemes: Set[str]):
    if token.lexeme in stop_lexemes or token.family == T_EOF:
        return
    if not is_statement_start():
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
        if token.family == T_ID:
            for name in varlist_collect():
                current_scope.add_variable(name)
        match_lexeme(DECL_END)


def varlist_collect() -> List[str]:
    names = []
    if token.family != T_ID:
        return names
    names.append(match_family(T_ID))
    while token.lexeme == ",":
        match_lexeme(",")
        names.append(match_family(T_ID))
    return names


def functions():
    while token.lexeme == "function":
        function_def()


def function_def():
    match_lexeme("function")
    fname = match_family(T_ID)

    func = add_function_to_current_scope(fname)
    parent_scope = current_scope
    fscope = enter_scope(fname, owner_function=func)

    formalpars(func)

    q_begin = genquad("begin_block", fname, "_", "_")
    fscope.start_quad = q_begin
    func.start_quad = q_begin

    programblock()

    q_end = genquad("end_block", fname, "_", "_")
    fscope.end_quad = q_end
    quad_scope[q_end] = fscope

    finished_scope = exit_scope()
    func.frame_length = finished_scope.frame_length
    current_scope_ref = parent_scope
    if current_scope is not current_scope_ref:
        raise SemanticError("Internal error: bad scope restoration after function")


def formalpars(func: Function):
    match_lexeme("(")
    formalparlist(func)
    match_lexeme(")")


def formalparlist(func: Function):
    if token.lexeme not in {"in", "inout"}:
        return
    formalparitem(func)
    while token.lexeme == ",":
        match_lexeme(",")
        formalparitem(func)


def formalparitem(func: Function):
    if token.lexeme == "in":
        match_lexeme("in")
        name = match_family(T_ID)
        func.formal_params.append(FormalParam(name, "CV"))
        current_scope.add_parameter(name, "CV")
    elif token.lexeme == "inout":
        match_lexeme("inout")
        name = match_family(T_ID)
        func.formal_params.append(FormalParam(name, "REF"))
        current_scope.add_parameter(name, "REF")
    else:
        syntax_error("Expected 'in' or 'inout' in formal parameter")


def statements():
    if token.lexeme == "{":
        match_lexeme("{")
        statements_sequence(stop_lexemes={"}"})
        match_lexeme("}")
    else:
        statement()


def statement():
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
    require_lvalue(lhs)
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
    optional_lexeme(":")
    exit_list: List[int] = []
    while token.lexeme == "when":
        match_lexeme("when")
        optional_lexeme(":")
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
    optional_lexeme(":")
    start = nextquad()

    while token.lexeme == "when":
        match_lexeme("when")
        optional_lexeme(":")
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
        optional_lexeme(":")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        genquad(":=", "1", "_", flag)
        statements()
        backpatch(flist, nextquad())

    genquad("if=", flag, "1", str(start))


def untilcase_stat():
    match_lexeme("untilcase")
    start = nextquad()

    while token.lexeme == "when":
        match_lexeme("when")
        optional_lexeme(":")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        backpatch(flist, nextquad())

    match_lexeme("until")
    tlist_u, flist_u = condition()
    q_loop = genquad("jump", "_", "_", str(start))
    backpatch(tlist_u, nextquad())
    backpatch(flist_u, q_loop)


def forcase_stat():
    match_lexeme("forcase")
    var = match_family(T_ID)
    require_lvalue(var)
    match_lexeme("=")
    n = match_family(T_INT)

    if int(n) < 1:
        raise SemanticError("[SEMANTIC] forcase integer_value must be >= 1")

    genquad(":=", "1", "_", var)
    start = nextquad()

    q_if_done = genquad("if>", var, n, "_")

    while token.lexeme == "when":
        match_lexeme("when")
        optional_lexeme(":")
        tlist, flist = condition()
        match_lexeme(":")
        backpatch(tlist, nextquad())
        statements()
        backpatch(flist, nextquad())

    t = newtemp()
    genquad("+", var, "1", t)
    genquad(":=", t, "_", var)
    genquad("jump", "_", "_", str(start))

    backpatch([q_if_done], nextquad())


def input_stat():
    match_lexeme("input")
    name = match_family(T_ID)
    require_lvalue(name)
    genquad("inp", name, "_", "_")


def print_stat():
    match_lexeme("print")
    place = expression()
    genquad("out", place, "_", "_")


def return_stat():
    match_lexeme("return")
    if current_scope is program_scope:
        raise SemanticError("[SEMANTIC] return cannot appear in the main program block")
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
    if sign is not None and sign == "-":
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
        ent, _ = resolve_entity(name)
        if isinstance(ent, Function):
            raise SemanticError(
                f"[SEMANTIC] Function '{name}' used without actual parameters"
            )
        return name

    func = require_function(name)
    args = actualpars_collect()

    if len(args) != len(func.formal_params):
        raise SemanticError(
            f"[SEMANTIC] Function '{name}' expects {len(func.formal_params)} parameters, "
            f"got {len(args)}"
        )

    for i, ((actual_mode, actual_val), formal) in enumerate(zip(args, func.formal_params), start=1):
        if actual_mode == "in" and formal.mode != "CV":
            raise SemanticError(
                f"[SEMANTIC] Parameter {i} of '{name}' must be passed with inout"
            )
        if actual_mode == "inout" and formal.mode != "REF":
            raise SemanticError(
                f"[SEMANTIC] Parameter {i} of '{name}' must be passed with in"
            )
        if actual_mode == "inout":
            require_lvalue(actual_val)

    for mode, val in args:
        if mode == "in":
            genquad("par", val, "CV", "_")
        else:
            genquad("par", val, "REF", "_")

    ret = newtemp()
    genquad("par", ret, "RET", "_")
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
        require_lvalue(name)
        return ("inout", name)
    syntax_error("Expected 'in' or 'inout' in actual parameters")

# =========================
# OUTPUT: INTERMEDIATE CODE AND SYMBOL TABLE
# =========================

def base_output_path(src_path: str) -> str:
    if src_path.lower().endswith(".c++"):
        return src_path[:-4]
    return src_path


def output_label_for_quad(idx: int) -> int:
    return idx + 1


def printable_quad_arg(arg: str, is_target: bool = False) -> str:
    if is_target and arg.isdigit():
        return str(int(arg) + 1)
    return arg


def write_int_file(src_path: str) -> str:
    out_path = base_output_path(src_path) + ".int"
    with open(out_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(quads):
            z = printable_quad_arg(q.z, q.op == "jump" or q.op.startswith("if"))
            f.write(f"{output_label_for_quad(i)}: {q.op}, {q.x}, {q.y}, {z}\n")
    return out_path


def entity_to_string(entity: Entity) -> str:
    if isinstance(entity, Variable):
        return f"Variable(name={entity.name}, offset={entity.offset})"
    if isinstance(entity, TempVariable):
        return f"TempVariable(name={entity.name}, offset={entity.offset})"
    if isinstance(entity, Parameter):
        return f"Parameter(name={entity.name}, mode={entity.mode}, offset={entity.offset})"
    if isinstance(entity, Function):
        params = ", ".join(f"{p.name}:{p.mode}" for p in entity.formal_params)
        return (
            f"Function(name={entity.name}, params=[{params}], "
            f"start_quad={output_label_for_quad(entity.start_quad) if entity.start_quad is not None else None}, "
            f"frame_length={entity.frame_length}, level={entity.nesting_level})"
        )
    return str(entity)


def write_symbol_table_file(src_path: str) -> str:
    out_path = base_output_path(src_path) + ".symb"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Symbol Table\n")
        f.write("============\n\n")
        for scope in all_scopes:
            f.write(
                f"Scope: {scope.name}, level={scope.nesting_level}, "
                f"frame_length={scope.frame_length}, "
                f"start_quad={output_label_for_quad(scope.start_quad) if scope.start_quad is not None else None}, "
                f"statements_start_quad={output_label_for_quad(scope.statements_start_quad) if scope.statements_start_quad is not None else None}, "
                f"end_quad={output_label_for_quad(scope.end_quad) if scope.end_quad is not None else None}\n"
            )
            for entity in scope.entities:
                f.write(f"  - {entity_to_string(entity)}\n")
            f.write("\n")
    return out_path

# =========================
# FINAL CODE: RISC-V ASSEMBLY
# =========================

class FinalCodeGenerator:
    def __init__(self):
        self.lines: List[str] = []
        self.pending_pars: List[Quad] = []
        self.rel_branch = {
            "=": "beq",
            "<>": "bne",
            "<": "blt",
            ">": "bgt",
            "<=": "ble",
            ">=": "bge",
        }

    def emit(self, text: str = "") -> None:
        self.lines.append(text)

    def label(self, idx: int) -> str:
        return f"L_{idx + 1}"

    def addi(self, rd: str, rs: str, imm: int) -> None:
        if -2048 <= imm <= 2047:
            self.emit(f"    addi {rd}, {rs}, {imm}")
        else:
            self.emit(f"    li t6, {imm}")
            self.emit(f"    add {rd}, {rs}, t6")

    def subi(self, rd: str, rs: str, imm: int) -> None:
        if -2048 <= -imm <= 2047:
            self.emit(f"    addi {rd}, {rs}, {-imm}")
        else:
            self.emit(f"    li t6, {imm}")
            self.emit(f"    sub {rd}, {rs}, t6")

    def is_integer(self, s: str) -> bool:
        if s.startswith("-"):
            return s[1:].isdigit()
        return s.isdigit()

    def scope_for_quad(self, idx: int) -> Scope:
        if idx not in quad_scope:
            raise SemanticError(f"Internal error: no scope for quad {idx}")
        return quad_scope[idx]

    def resolve_at_quad(self, name: str, qidx: int) -> Tuple[Entity, Scope]:
        return resolve_entity(name, self.scope_for_quad(qidx))

    def frame_base_for_scope(self, target_scope: Scope, current: Scope, reg: str) -> None:
        if target_scope is current:
            self.emit(f"    mv {reg}, sp")
            return

        if not is_ancestor_scope(target_scope, current):
            raise SemanticError(
                f"[FINAL] Scope '{target_scope.name}' is not an ancestor of '{current.name}'"
            )

        self.emit(f"    mv {reg}, sp")
        scope = current
        while scope is not target_scope:
            self.emit(f"    lw {reg}, 12({reg})")
            scope = scope.parent

    def address_of(self, name: str, qidx: int, reg: str) -> None:
        ent, ent_scope = self.resolve_at_quad(name, qidx)
        current = self.scope_for_quad(qidx)

        if isinstance(ent, Function):
            raise SemanticError(f"[FINAL] Function '{name}' has no value address")

        # Global/main variable.
        if ent_scope is program_scope:
            if isinstance(ent, Parameter):
                raise SemanticError("Internal error: main scope cannot contain parameters")
            self.addi(reg, "gp", ent.offset)
            return

        # Local variable/temporary/CV parameter.
        if ent_scope is current:
            if isinstance(ent, Parameter) and ent.mode == "REF":
                self.emit(f"    lw {reg}, {ent.offset}(sp)")
            else:
                self.addi(reg, "sp", ent.offset)
            return

        # Non-local variable through static chain.
        self.frame_base_for_scope(ent_scope, current, reg)
        if isinstance(ent, Parameter) and ent.mode == "REF":
            self.emit(f"    lw {reg}, {ent.offset}({reg})")
        else:
            self.addi(reg, reg, ent.offset)

    def loadvr(self, value: str, qidx: int, reg: str) -> None:
        if value == "_":
            raise SemanticError("[FINAL] Cannot load '_' value")
        if self.is_integer(value):
            self.emit(f"    li {reg}, {value}")
            return
        self.address_of(value, qidx, reg)
        self.emit(f"    lw {reg}, 0({reg})")

    def storerv(self, reg: str, name: str, qidx: int) -> None:
        if name == "_":
            raise SemanticError("[FINAL] Cannot store to '_'")
        self.address_of(name, qidx, "t0")
        self.emit(f"    sw {reg}, 0(t0)")

    def callee_static_link(self, func: Function, call_scope: Scope, reg: str) -> None:
        if func.scope is None or func.scope.parent is None:
            raise SemanticError(f"[FINAL] Function '{func.name}' has no parent scope")
        target_parent = func.scope.parent
        self.frame_base_for_scope(target_parent, call_scope, reg)

    def function_entity_at_call(self, name: str, qidx: int) -> Function:
        ent, _ = self.resolve_at_quad(name, qidx)
        if not isinstance(ent, Function):
            raise SemanticError(f"[FINAL] '{name}' is not a function")
        if ent.start_quad is None or ent.scope is None:
            raise SemanticError(f"[FINAL] Function '{name}' has incomplete symbol-table info")
        return ent

    def place_actual_parameters(self, func: Function, call_qidx: int, callee_frame_reg: str) -> None:
        actuals = [p for p in self.pending_pars if p.y in {"CV", "REF"}]
        returns = [p for p in self.pending_pars if p.y == "RET"]

        if len(actuals) != len(func.formal_params):
            raise SemanticError(
                f"[FINAL] Call to '{func.name}' has {len(actuals)} actual params, "
                f"expected {len(func.formal_params)}"
            )

        # Return-value address slot.
        if returns:
            ret_place = returns[-1].x
            self.address_of(ret_place, call_qidx, "t1")
            self.emit(f"    sw t1, 0({callee_frame_reg})")

        # Actual parameters.
        if func.scope is None:
            raise SemanticError(f"[FINAL] Missing scope for function '{func.name}'")

        for actual_quad, formal in zip(actuals, func.formal_params):
            formal_ent = func.scope.lookup_local(formal.name)
            if not isinstance(formal_ent, Parameter):
                raise SemanticError(
                    f"[FINAL] Formal parameter '{formal.name}' missing in function scope"
                )
            if actual_quad.y == "CV":
                self.loadvr(actual_quad.x, call_qidx, "t1")
                self.emit(f"    sw t1, {formal_ent.offset}({callee_frame_reg})")
            elif actual_quad.y == "REF":
                self.address_of(actual_quad.x, call_qidx, "t1")
                self.emit(f"    sw t1, {formal_ent.offset}({callee_frame_reg})")
            else:
                raise SemanticError(f"[FINAL] Unknown parameter mode '{actual_quad.y}'")

    def gen_call(self, q: Quad, qidx: int) -> None:
        func = self.function_entity_at_call(q.x, qidx)
        call_scope = self.scope_for_quad(qidx)
        frame_len = func.frame_length

        self.emit(f"    # call {func.name}")
        self.subi("t0", "sp", frame_len)       # t0 points to callee activation record
        self.emit("    sw sp, 4(t0)")          # dynamic link
        self.callee_static_link(func, call_scope, "t1")
        self.emit("    sw t1, 12(t0)")         # static link
        self.place_actual_parameters(func, qidx, "t0")
        self.subi("sp", "sp", frame_len)
        self.emit(f"    jal {self.label(func.start_quad)}")
        self.addi("sp", "sp", frame_len)

        self.pending_pars = []

    def gen_begin_block(self, q: Quad, qidx: int) -> None:
        scope = self.scope_for_quad(qidx)
        if scope is program_scope:
            self.emit("    # begin main block")
        else:
            self.emit(f"    # begin function {scope.name}")
            self.emit("    sw ra, 8(sp)")

        if scope.statements_start_quad is not None and scope.statements_start_quad != qidx + 1:
            self.emit(f"    j {self.label(scope.statements_start_quad)}")

    def gen_end_block(self, q: Quad, qidx: int) -> None:
        scope = self.scope_for_quad(qidx)
        if scope is program_scope:
            self.emit("    li a7, 10")
            self.emit("    ecall")
        else:
            self.emit(f"    # end function {scope.name}")
            self.emit("    lw ra, 8(sp)")
            self.emit("    jr ra")

    def gen_ret(self, q: Quad, qidx: int) -> None:
        scope = self.scope_for_quad(qidx)
        self.loadvr(q.x, qidx, "t1")
        self.emit("    lw t0, 0(sp)")
        self.emit("    sw t1, 0(t0)")
        if scope.end_quad is not None:
            self.emit(f"    j {self.label(scope.end_quad)}")
        else:
            self.emit("    lw ra, 8(sp)")
            self.emit("    jr ra")

    def gen_quad(self, q: Quad, qidx: int) -> None:
        self.emit(f"{self.label(qidx)}:")
        self.emit(f"    # {qidx + 1}: {q.op}, {q.x}, {q.y}, {q.z}")

        if q.op == "begin_block":
            self.gen_begin_block(q, qidx)
        elif q.op == "end_block":
            self.gen_end_block(q, qidx)
        elif q.op == "halt":
            self.emit("    li a7, 10")
            self.emit("    ecall")
        elif q.op == "jump":
            self.emit(f"    j {self.label(int(q.z))}")
        elif q.op.startswith("if"):
            rel = q.op[2:]
            if rel not in self.rel_branch:
                raise SemanticError(f"[FINAL] Unknown relational op '{rel}'")
            self.loadvr(q.x, qidx, "t1")
            self.loadvr(q.y, qidx, "t2")
            self.emit(f"    {self.rel_branch[rel]} t1, t2, {self.label(int(q.z))}")
        elif q.op == ":=":
            self.loadvr(q.x, qidx, "t1")
            self.storerv("t1", q.z, qidx)
        elif q.op in {"+", "-", "*", "/"}:
            self.loadvr(q.x, qidx, "t1")
            self.loadvr(q.y, qidx, "t2")
            if q.op == "+":
                self.emit("    add t1, t1, t2")
            elif q.op == "-":
                self.emit("    sub t1, t1, t2")
            elif q.op == "*":
                self.emit("    mul t1, t1, t2")
            elif q.op == "/":
                self.emit("    div t1, t1, t2")
            self.storerv("t1", q.z, qidx)
        elif q.op == "out":
            self.loadvr(q.x, qidx, "a0")
            self.emit("    li a7, 1")
            self.emit("    ecall")
            self.emit("    li a0, 10")
            self.emit("    li a7, 11")
            self.emit("    ecall")
        elif q.op == "inp":
            self.emit("    li a7, 5")
            self.emit("    ecall")
            self.storerv("a0", q.x, qidx)
        elif q.op == "retv":
            self.gen_ret(q, qidx)
        elif q.op == "par":
            self.pending_pars.append(q)
        elif q.op == "call":
            self.gen_call(q, qidx)
        else:
            raise SemanticError(f"[FINAL] Unsupported quad operation '{q.op}'")

        self.emit("")

    def generate(self) -> str:
        if program_scope is None:
            raise SemanticError("Internal error: program scope missing")

        self.emit(".text")
        self.emit(".globl main")
        self.emit("main:")
        self.subi("sp", "sp", program_scope.frame_length)
        self.emit("    mv gp, sp")
        if program_scope.statements_start_quad is not None:
            self.emit(f"    j {self.label(program_scope.statements_start_quad)}")
        else:
            self.emit(f"    j {self.label(program_scope.start_quad)}")
        self.emit("")

        for i, q in enumerate(quads):
            self.gen_quad(q, i)

        return "\n".join(self.lines)


def write_asm_file(src_path: str) -> str:
    out_path = base_output_path(src_path) + ".asm"
    generator = FinalCodeGenerator()
    asm = generator.generate()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(asm)
        f.write("\n")
    return out_path

# =========================
# MAIN
# =========================

def main():
    global lexer, token

    if len(sys.argv) != 2:
        print("Usage: python3 compiler.py <file.c++>")
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
        int_path = write_int_file(path)
        symb_path = write_symbol_table_file(path)
        asm_path = write_asm_file(path)
        print("Compilation successfully completed.")
        print(f"Intermediate code written to: {int_path}")
        print(f"Symbol table written to: {symb_path}")
        print(f"Final RISC-V code written to: {asm_path}")
    except (LexerError, ParserError, SemanticError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
