from __future__ import annotations

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

from i import run_code


def run_script(source: str) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run_code(source)
    return buffer.getvalue().strip()


def test_print_and_assignment() -> None:
    output = run_script('name = "Alex"\nprint(name)')
    assert output == "Alex"


def test_if_else_flow() -> None:
    source = '''
    age = 20
    if age >= 18 {
        print("Adult")
    } else {
        print("Minor")
    }
    '''
    assert run_script(source) == "Adult"


def test_single_quote_strings() -> None:
    output = run_script("out('Hello from I')")
    assert output == "Hello from I"


def test_yap_alias() -> None:
    output = run_script("yap('hi')")
    assert output == "hi"


def test_pin_alias() -> None:
    output = run_script("pin('hello from pin')")
    assert output == "hello from pin"


def test_prt_alias() -> None:
    output = run_script("prt('hello from prt')")
    assert output == "hello from prt"


def test_color_output() -> None:
    output = run_script("out(color('Hi', 'red'))")
    assert output == "\x1b[31mHi\x1b[0m"


def test_function_and_return() -> None:
    source = '''
    dec add(a, b) {
        give a + b
    }
    out(add(2, 3))
    '''
    assert run_script(source) == "5"


def test_distinctive_i_keywords() -> None:
    source = '''
    age = 20
    if age >= 18 {
        out("Adult")
    } else {
        out("Minor")
    }
    '''
    assert run_script(source) == "Adult"


def test_loop_and_break() -> None:
    source = '''
    total = 0
    loop 3 {
        total = total + 1
        if total == 2 {
            break
        }
    }
    print(total)
    '''
    assert run_script(source) == "2"


def test_run_i_script_works_from_different_cwd() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "run_i.sh"
    temp_dir = repo_root / "tmp_cli_test"
    temp_dir.mkdir(exist_ok=True)
    try:
        source_rel = os.path.relpath(repo_root / "examples" / "hello.i", temp_dir)
        result = subprocess.run(
            ["bash", str(script), source_rel],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(repo_root)},
        )
        assert result.returncode == 0, result.stderr
        assert "Hello, world!" in result.stdout
    finally:
        temp_dir.rmdir()
