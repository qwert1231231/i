# I Language

I is a small, beginner-friendly language inspired by Python, C, Rust, C#, and JavaScript.

## Quick start

```bash
git clone https://github.com/qwert1231231/i.git
cd i
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Example

```i
pin("Hello, world!")
```

## Run a file

```bash
i examples/hello.i
```

## Run the project directly

```bash
python -m i examples/hello.i
```

## Install without a venv

### Linux / macOS

```bash
python3 -m pip install -e .
```

### Windows

```powershell
py -m pip install -e .
```

## Run tests

```bash
python -m pytest -q
```

## GitHub usage

After cloning the project from GitHub, do this once:

```bash
cd i
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Then run programs from anywhere in the project folder:

```bash
i examples/hello.i
```
