"""Interpreter for the I language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import RuntimeError as ILRuntimeError
from .parser import (
    Assign,
    BinaryOp,
    Block,
    BreakStmt,
    Call,
    ContinueStmt,
    ForStmt,
    FunctionDecl,
    IfStmt,
    Index,
    Literal,
    ListLiteral,
    LoopStmt,
    MainStmt,
    MapLiteral,
    PrintStmt,
    Program,
    ReturnStmt,
    UnaryOp,
    Variable,
)


class ReturnSignal(Exception):
    def __init__(self, value: Any = None) -> None:
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Environment:
    def __init__(self, parent: Environment | None = None) -> None:
        self.parent = parent
        self.values: dict[str, Any] = {}

    def declare(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        self.values[name] = value

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise ILRuntimeError(f"Undefined variable: {name}")

    def child(self) -> "Environment":
        return Environment(self)


@dataclass
class FunctionValue:
    name: str
    params: list[str]
    body: Block
    closure: Environment

    def __call__(self, args: list[Any]) -> Any:
        call_env = Environment(self.closure)
        if len(args) != len(self.params):
            raise ILRuntimeError(f"Function {self.name} expected {len(self.params)} arguments, got {len(args)}.")
        for name, value in zip(self.params, args):
            call_env.declare(name, value)
        try:
            for stmt in self.body.statements:
                execute_statement(stmt, call_env)
        except ReturnSignal as signal:
            return signal.value
        return None


class Interpreter:
    def __init__(self) -> None:
        self.globals = Environment()
        self._register_builtins()

    def _register_builtins(self) -> None:
        self.globals.declare("print", self._builtin_print)
        self.globals.declare("out", self._builtin_print)
        self.globals.declare("yap", self._builtin_print)
        self.globals.declare("input", self._builtin_input)
        self.globals.declare("ask", self._builtin_input)
        self.globals.declare("color", self._builtin_color)
        self.globals.declare("read", self._builtin_read)
        self.globals.declare("write", self._builtin_write)
        self.globals.declare("append", self._builtin_append)
        self.globals.declare("int", int)
        self.globals.declare("float", float)
        self.globals.declare("str", str)
        self.globals.declare("len", len)

    def _builtin_print(self, *args: Any) -> None:
        print(" ".join(str(arg) for arg in args))

    def _builtin_color(self, text: Any, color_name: str = "white") -> str:
        palette = {
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "black": "\033[30m",
            "reset": "\033[0m",
        }
        code = palette.get(str(color_name).lower(), palette["white"])
        return f"{code}{text}\033[0m"

    def _builtin_input(self, prompt: str = "") -> str:
        if prompt:
            print(prompt, end="")
        return input()

    def _builtin_read(self, filename: str) -> str:
        try:
            with open(str(filename), 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ILRuntimeError(f"File not found: {filename}")
        except Exception as e:
            raise ILRuntimeError(f"Error reading file {filename}: {e}")

    def _builtin_write(self, filename: str, content: str) -> None:
        try:
            with open(str(filename), 'w', encoding='utf-8') as f:
                f.write(str(content))
        except Exception as e:
            raise ILRuntimeError(f"Error writing to file {filename}: {e}")

    def _builtin_append(self, filename: str, content: str) -> None:
        try:
            with open(str(filename), 'a', encoding='utf-8') as f:
                f.write(str(content))
        except Exception as e:
            raise ILRuntimeError(f"Error appending to file {filename}: {e}")

    def run(self, program: Program) -> Any:
        for stmt in program.statements:
            execute_statement(stmt, self.globals)
        return None

    def evaluate(self, expr: Any, env: Environment) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Variable):
            return env.get(expr.name)
        if isinstance(expr, ListLiteral):
            return [self.evaluate(item, env) for item in expr.elements]
        if isinstance(expr, MapLiteral):
            result: dict[Any, Any] = {}
            for key_expr, value_expr in expr.entries:
                key = self.evaluate(key_expr, env)
                value = self.evaluate(value_expr, env)
                result[key] = value
            return result
        if isinstance(expr, UnaryOp):
            value = self.evaluate(expr.operand, env)
            if expr.op == "-":
                return -value
            if expr.op == "not":
                return not value
            raise ILRuntimeError(f"Unsupported unary operator: {expr.op}")
        if isinstance(expr, BinaryOp):
            left = self.evaluate(expr.left, env)
            right = self.evaluate(expr.right, env)
            if expr.op == "+":
                return left + right
            if expr.op == "-":
                return left - right
            if expr.op == "*":
                return left * right
            if expr.op == "/":
                return left / right
            if expr.op == "%":
                return left % right
            if expr.op == "**":
                return left ** right
            if expr.op == "==":
                return left == right
            if expr.op == "!=":
                return left != right
            if expr.op == ">":
                return left > right
            if expr.op == "<":
                return left < right
            if expr.op == ">=":
                return left >= right
            if expr.op == "<=":
                return left <= right
            if expr.op == "and":
                return bool(left) and bool(right)
            if expr.op == "or":
                return bool(left) or bool(right)
            raise ILRuntimeError(f"Unsupported binary operator: {expr.op}")
        if isinstance(expr, Call):
            callee = self.evaluate(expr.callee, env)
            args = [self.evaluate(arg, env) for arg in expr.arguments]
            if callable(callee):
                if isinstance(callee, FunctionValue):
                    return callee(args)
                return callee(*args)
            raise ILRuntimeError(f"Attempted to call non-callable value: {callee!r}")
        if isinstance(expr, Index):
            target = self.evaluate(expr.target, env)
            index = self.evaluate(expr.index, env)
            return target[index]
        raise ILRuntimeError(f"Unsupported expression type: {type(expr).__name__}")


def execute_statement(stmt: Any, env: Environment) -> Any:
    if isinstance(stmt, PrintStmt):
        args = [evaluate_expression(value, env) for value in stmt.values]
        if args:
            print(" ".join(str(arg) for arg in args))
        else:
            print()
        return None
    if isinstance(stmt, Call):
        evaluate_expression(stmt, env)
        return None
    if isinstance(stmt, Assign):
        env.assign(stmt.name, evaluate_expression(stmt.value, env))
        return None
    if isinstance(stmt, IfStmt):
        if evaluate_expression(stmt.condition, env):
            execute_block(stmt.then_block, env)
        elif stmt.else_block is not None:
            execute_block(stmt.else_block, env)
        return None
    if isinstance(stmt, LoopStmt):
        if stmt.count is None:
            while True:
                try:
                    execute_block(stmt.body, env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return None
        count = evaluate_expression(stmt.count, env)
        for _ in range(int(count)):
            try:
                execute_block(stmt.body, env)
            except ContinueSignal:
                continue
            except BreakSignal:
                break
        return None
    if isinstance(stmt, ForStmt):
        if stmt.start is not None and stmt.end is not None:
            start = evaluate_expression(stmt.start, env)
            end = evaluate_expression(stmt.end, env)
            for i in range(int(start), int(end)):
                loop_env = Environment(env)
                loop_env.declare(stmt.name, i)
                try:
                    execute_block(stmt.body, env if stmt.body is None else stmt.body, loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return None
        collection = evaluate_expression(stmt.collection, env)
        for item in collection:
            loop_env = Environment(env)
            loop_env.declare(stmt.name, item)
            try:
                execute_block(stmt.body, loop_env)
            except ContinueSignal:
                continue
            except BreakSignal:
                break
        return None
    if isinstance(stmt, BreakStmt):
        raise BreakSignal()
    if isinstance(stmt, ContinueStmt):
        raise ContinueSignal()
    if isinstance(stmt, ReturnStmt):
        if stmt.value is None:
            raise ReturnSignal(None)
        raise ReturnSignal(evaluate_expression(stmt.value, env))
    if isinstance(stmt, FunctionDecl):
        env.declare(stmt.name, FunctionValue(stmt.name, stmt.params, stmt.body, env))
        return None
    if isinstance(stmt, MainStmt):
        execute_block(stmt.body, env)
        return None
    if isinstance(stmt, Block):
        execute_block(stmt, env)
        return None
    raise ILRuntimeError(f"Unsupported statement type: {type(stmt).__name__}")


def evaluate_expression(expr: Any, env: Environment) -> Any:
    if isinstance(expr, Literal):
        return expr.value
    if isinstance(expr, Variable):
        return env.get(expr.name)
    if isinstance(expr, ListLiteral):
        return [evaluate_expression(item, env) for item in expr.elements]
    if isinstance(expr, MapLiteral):
        data: dict[Any, Any] = {}
        for key_expr, value_expr in expr.entries:
            data[evaluate_expression(key_expr, env)] = evaluate_expression(value_expr, env)
        return data
    if isinstance(expr, UnaryOp):
        value = evaluate_expression(expr.operand, env)
        if expr.op == "-":
            return -value
        if expr.op == "not":
            return not value
        raise ILRuntimeError(f"Unsupported unary operator: {expr.op}")
    if isinstance(expr, BinaryOp):
        left = evaluate_expression(expr.left, env)
        right = evaluate_expression(expr.right, env)
        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "%": lambda a, b: a % b,
            "**": lambda a, b: a ** b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "and": lambda a, b: bool(a) and bool(b),
            "or": lambda a, b: bool(a) or bool(b),
        }
        if expr.op not in ops:
            raise ILRuntimeError(f"Unsupported binary operator: {expr.op}")
        return ops[expr.op](left, right)
    if isinstance(expr, Call):
        callee = evaluate_expression(expr.callee, env)
        args = [evaluate_expression(arg, env) for arg in expr.arguments]
        if callable(callee):
            if isinstance(callee, FunctionValue):
                return callee(args)
            return callee(*args)
        raise ILRuntimeError(f"Attempted to call non-callable value: {callee!r}")
    if isinstance(expr, Index):
        target = evaluate_expression(expr.target, env)
        index = evaluate_expression(expr.index, env)
        return target[index]
    raise ILRuntimeError(f"Unsupported expression type: {type(expr).__name__}")


def execute_block(block: Block, env: Environment) -> Any:
    for stmt in block.statements:
        execute_statement(stmt, env)
    return None


def run_code(source: str) -> Any:
    from .lexer import Lexer
    from .parser import Parser

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.run(program)
    return None


def run_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        source = file.read()
    return run_code(source)
