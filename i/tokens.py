"""Token definitions for the I language."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    value: object
    position: int = 0

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r}, {self.position})"


KEYWORDS = {
    "out": "OUT",
    "ask": "ASK",
    "if": "IF",
    "else": "ELSE",
    "alt": "ALT",
    "for": "FOR",
    "in": "IN",
    "to": "TO",
    "loop": "LOOP",
    "break": "BREAK",
    "skip": "SKIP",
    "give": "GIVE",
    "dec": "DEC",
    "main": "MAIN",
    "all": "ALL",
    "any": "ANY",
    "never": "NEVER",
    "yes": "TRUE",
    "nah": "FALSE",
    "void": "NULL",
    "obj": "CLASS",
    "use": "USE",
}

SINGLE_CHAR_TOKENS = {
    "{": "LBRACE",
    "}": "RBRACE",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ":": "COLON",
    ".": "DOT",
    ";": "SEMI",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "PERCENT",
    "=": "ASSIGN",
    "!": "BANG",
    "<": "LT",
    ">": "GT",
    "&": "AMP",
    "|": "PIPE",
}

MULTI_CHAR_TOKENS = {
    "==": "EQ",
    "!=": "NEQ",
    ">=": "GTE",
    "<=": "LTE",
    "**": "POWER",
    "+=": "PLUS_ASSIGN",
    "-=": "MINUS_ASSIGN",
    "*=": "STAR_ASSIGN",
    "/=": "SLASH_ASSIGN",
    "%=": "PERCENT_ASSIGN",
    "++": "PLUS_PLUS",
    "--": "MINUS_MINUS",
}
