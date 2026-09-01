"""Lexer for the I language."""

from __future__ import annotations

from .errors import TokenError
from .tokens import KEYWORDS, MULTI_CHAR_TOKENS, SINGLE_CHAR_TOKENS, Token


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.length = len(source)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < self.length:
            ch = self.source[self.index]

            if ch.isspace():
                self.index += 1
                continue

            if ch in {'"', "'"}:
                tokens.append(self._read_string(ch))
                continue

            if ch.isdigit():
                tokens.append(self._read_number())
                continue

            if ch.isalpha() or ch == '_':
                tokens.append(self._read_identifier())
                continue

            if self.index + 1 < self.length:
                two = self.source[self.index : self.index + 2]
                if two in MULTI_CHAR_TOKENS:
                    tokens.append(Token(MULTI_CHAR_TOKENS[two], two, self.index))
                    self.index += 2
                    continue

            if ch in SINGLE_CHAR_TOKENS:
                tokens.append(Token(SINGLE_CHAR_TOKENS[ch], ch, self.index))
                self.index += 1
                continue

            raise TokenError(f"Unexpected character '{ch}' at position {self.index}.")

        tokens.append(Token("EOF", None, self.index))
        return tokens

    def _read_string(self, quote: str) -> Token:
        start = self.index
        self.index += 1
        chars: list[str] = []

        while self.index < self.length:
            ch = self.source[self.index]
            if ch == quote:
                self.index += 1
                return Token("STRING", ''.join(chars), start)
            if ch == '\\':
                self.index += 1
                if self.index >= self.length:
                    raise TokenError("Unterminated string literal.")
                escaped = self.source[self.index]
                mapping = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '"': '"',
                    "'": "'",
                    '\\': '\\',
                }
                chars.append(mapping.get(escaped, escaped))
                self.index += 1
                continue
            chars.append(ch)
            self.index += 1

        raise TokenError("Unterminated string literal.")

    def _read_number(self) -> Token:
        start = self.index
        seen_dot = False

        while self.index < self.length:
            ch = self.source[self.index]
            if ch.isdigit():
                self.index += 1
                continue
            if ch == '.' and not seen_dot:
                seen_dot = True
                self.index += 1
                continue
            break

        text = self.source[start:self.index]
        if '.' in text:
            return Token("NUMBER", float(text), start)
        return Token("NUMBER", int(text), start)

    def _read_identifier(self) -> Token:
        start = self.index
        while self.index < self.length:
            ch = self.source[self.index]
            if ch.isalnum() or ch == '_':
                self.index += 1
            else:
                break

        text = self.source[start:self.index]
        token_type = KEYWORDS.get(text, "IDENT")
        value = text
        if token_type in {"TRUE", "FALSE"}:
            value = token_type == "TRUE"
        return Token(token_type, value, start)
