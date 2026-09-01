"""Parser for the I language."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import ParseError
from .tokens import Token


@dataclass
class Program:
    statements: list[Any] = field(default_factory=list)


@dataclass
class Block:
    statements: list[Any] = field(default_factory=list)


@dataclass
class Literal:
    value: Any


@dataclass
class Variable:
    name: str


@dataclass
class ListLiteral:
    elements: list[Any]


@dataclass
class MapLiteral:
    entries: list[tuple[Any, Any]]


@dataclass
class BinaryOp:
    left: Any
    op: str
    right: Any


@dataclass
class UnaryOp:
    op: str
    operand: Any


@dataclass
class Call:
    callee: Any
    arguments: list[Any]


@dataclass
class Index:
    target: Any
    index: Any


@dataclass
class Assign:
    name: str
    value: Any


@dataclass
class PrintStmt:
    values: list[Any]


@dataclass
class IfStmt:
    condition: Any
    then_block: Block
    else_block: Block | None = None


@dataclass
class LoopStmt:
    count: Any | None
    body: Block


@dataclass
class ForStmt:
    name: str
    start: Any | None = None
    end: Any | None = None
    collection: Any | None = None
    body: Block | None = None


@dataclass
class BreakStmt:
    pass


@dataclass
class ContinueStmt:
    pass


@dataclass
class ReturnStmt:
    value: Any | None = None


@dataclass
class FunctionDecl:
    name: str
    params: list[str]
    body: Block


@dataclass
class MainStmt:
    body: Block


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse(self) -> Program:
        statements: list[Any] = []
        while not self._match("EOF"):
            statements.append(self._parse_statement())
        return Program(statements)

    def _parse_statement(self) -> Any:
        if self._match("PRINT") or self._match("OUT"):
            return self._parse_print()
        if self._match("RETURN") or self._match("GIVE"):
            if self._check("RBRACE") or self._check("EOF"):
                return ReturnStmt()
            return ReturnStmt(self._parse_expression())
        if self._match("BREAK"):
            return BreakStmt()
        if self._match("CONTINUE") or self._match("SKIP"):
            return ContinueStmt()
        if self._match("IF"):
            return self._parse_if()
        if self._match("LOOP"):
            return self._parse_loop()
        if self._match("FOR"):
            return self._parse_for()
        if self._match("DEC"):
            return self._parse_function()
        if self._match("MAIN"):
            return MainStmt(self._parse_block())
        return self._parse_assignment_or_expression()

    def _parse_print(self) -> PrintStmt:
        values: list[Any] = []
        if not self._check("LPAREN"):
            values.append(self._parse_expression())
            return PrintStmt(values)
        self._expect("LPAREN")
        if not self._check("RPAREN"):
            values.append(self._parse_expression())
            while self._match("COMMA"):
                values.append(self._parse_expression())
        self._expect("RPAREN")
        return PrintStmt(values)

    def _parse_if(self) -> IfStmt:
        condition = self._parse_expression()
        then_block = self._parse_block()
        else_block: Block | None = None
        if self._match("ELSE") or self._match("ALT"):
            if self._match("IF"):
                nested = self._parse_if()
                else_block = Block([nested])
            else:
                else_block = self._parse_block()
        return IfStmt(condition, then_block, else_block)

    def _parse_loop(self) -> LoopStmt:
        if self._check("LBRACE"):
            return LoopStmt(None, self._parse_block())
        count = self._parse_expression()
        body = self._parse_block()
        return LoopStmt(count, body)

    def _parse_for(self) -> ForStmt:
        name = self._expect("IDENT").value
        if self._match("ASSIGN"):
            start = self._parse_expression()
            self._expect("TO")
            end = self._parse_expression()
            body = self._parse_block()
            return ForStmt(name=name, start=start, end=end, body=body)
        self._expect("IN")
        collection = self._parse_expression()
        body = self._parse_block()
        return ForStmt(name=name, collection=collection, body=body)

    def _parse_function(self) -> FunctionDecl:
        name = self._expect("IDENT").value
        self._expect("LPAREN")
        params: list[str] = []
        if not self._check("RPAREN"):
            first = self._expect("IDENT").value
            params.append(first)
            while self._match("COMMA"):
                params.append(self._expect("IDENT").value)
        self._expect("RPAREN")
        body = self._parse_block()
        return FunctionDecl(name, params, body)

    def _parse_assignment_or_expression(self) -> Any:
        expr = self._parse_expression()
        if isinstance(expr, Variable) and self._match("ASSIGN"):
            value = self._parse_expression()
            return Assign(expr.name, value)
        if isinstance(expr, Variable) and self._match("PLUS_ASSIGN"):
            value = self._parse_expression()
            return Assign(expr.name, BinaryOp(Variable(expr.name), "+", value))
        if isinstance(expr, Variable) and self._match("MINUS_ASSIGN"):
            value = self._parse_expression()
            return Assign(expr.name, BinaryOp(Variable(expr.name), "-", value))
        if isinstance(expr, Variable) and self._match("STAR_ASSIGN"):
            value = self._parse_expression()
            return Assign(expr.name, BinaryOp(Variable(expr.name), "*", value))
        if isinstance(expr, Variable) and self._match("SLASH_ASSIGN"):
            value = self._parse_expression()
            return Assign(expr.name, BinaryOp(Variable(expr.name), "/", value))
        return expr

    def _parse_expression(self) -> Any:
        return self._parse_or()

    def _parse_or(self) -> Any:
        expr = self._parse_and()
        while self._match("OR") or self._match("ANY"):
            expr = BinaryOp(expr, "or", self._parse_and())
        return expr

    def _parse_and(self) -> Any:
        expr = self._parse_equality()
        while self._match("AND") or self._match("ALL"):
            expr = BinaryOp(expr, "and", self._parse_equality())
        return expr

    def _parse_equality(self) -> Any:
        expr = self._parse_comparison()
        while True:
            if self._match("EQ"):
                expr = BinaryOp(expr, "==", self._parse_comparison())
            elif self._match("NEQ"):
                expr = BinaryOp(expr, "!=", self._parse_comparison())
            else:
                break
        return expr

    def _parse_comparison(self) -> Any:
        expr = self._parse_additive()
        while True:
            if self._match("LT"):
                expr = BinaryOp(expr, "<", self._parse_additive())
            elif self._match("GT"):
                expr = BinaryOp(expr, ">", self._parse_additive())
            elif self._match("LTE"):
                expr = BinaryOp(expr, "<=", self._parse_additive())
            elif self._match("GTE"):
                expr = BinaryOp(expr, ">=", self._parse_additive())
            else:
                break
        return expr

    def _parse_additive(self) -> Any:
        expr = self._parse_multiplicative()
        while True:
            if self._match("PLUS"):
                expr = BinaryOp(expr, "+", self._parse_multiplicative())
            elif self._match("MINUS"):
                expr = BinaryOp(expr, "-", self._parse_multiplicative())
            else:
                break
        return expr

    def _parse_multiplicative(self) -> Any:
        expr = self._parse_unary()
        while True:
            if self._match("STAR"):
                expr = BinaryOp(expr, "*", self._parse_unary())
            elif self._match("SLASH"):
                expr = BinaryOp(expr, "/", self._parse_unary())
            elif self._match("PERCENT"):
                expr = BinaryOp(expr, "%", self._parse_unary())
            elif self._match("POWER"):
                expr = BinaryOp(expr, "**", self._parse_unary())
            else:
                break
        return expr

    def _parse_unary(self) -> Any:
        if self._match("MINUS"):
            return UnaryOp("-", self._parse_unary())
        if self._match("NOT") or self._match("NEVER"):
            return UnaryOp("not", self._parse_unary())
        return self._parse_postfix()

    def _parse_postfix(self) -> Any:
        expr = self._parse_primary()
        while True:
            if self._match("LBRACKET"):
                index = self._parse_expression()
                self._expect("RBRACKET")
                expr = Index(expr, index)
            elif self._match("LPAREN"):
                args: list[Any] = []
                if not self._check("RPAREN"):
                    args.append(self._parse_expression())
                    while self._match("COMMA"):
                        args.append(self._parse_expression())
                self._expect("RPAREN")
                expr = Call(expr, args)
            else:
                break
        return expr

    def _parse_primary(self) -> Any:
        if self._match("NUMBER"):
            return Literal(self._previous().value)
        if self._match("STRING"):
            return Literal(self._previous().value)
        if self._match("TRUE"):
            return Literal(True)
        if self._match("FALSE"):
            return Literal(False)
        if self._match("NULL"):
            return Literal(None)
        if self._match("IDENT"):
            return Variable(self._previous().value)
        if self._match("LBRACKET"):
            elements: list[Any] = []
            if not self._check("RBRACKET"):
                elements.append(self._parse_expression())
                while self._match("COMMA"):
                    elements.append(self._parse_expression())
            self._expect("RBRACKET")
            return ListLiteral(elements)
        if self._match("LBRACE"):
            entries: list[tuple[Any, Any]] = []
            if not self._check("RBRACE"):
                key = self._parse_expression()
                self._expect("COLON")
                value = self._parse_expression()
                entries.append((key, value))
                while self._match("COMMA"):
                    key = self._parse_expression()
                    self._expect("COLON")
                    value = self._parse_expression()
                    entries.append((key, value))
            self._expect("RBRACE")
            return MapLiteral(entries)
        if self._match("LPAREN"):
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr
        raise ParseError(f"Unexpected token {self._peek().type} while parsing expression.")

    def _parse_block(self) -> Block:
        self._expect("LBRACE")
        statements: list[Any] = []
        while not self._check("RBRACE"):
            if self._check("EOF"):
                raise ParseError("Unterminated block.")
            statements.append(self._parse_statement())
        self._expect("RBRACE")
        return Block(statements)

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _previous(self) -> Token:
        return self.tokens[self.index - 1]

    def _check(self, token_type: str) -> bool:
        return self._peek().type == token_type

    def _match(self, token_type: str) -> bool:
        if self._check(token_type):
            self.index += 1
            return True
        return False

    def _expect(self, token_type: str) -> Token:
        if not self._check(token_type):
            raise ParseError(f"Expected {token_type} but found {self._peek().type}.")
        token = self._peek()
        self.index += 1
        return token
