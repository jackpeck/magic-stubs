# Magic Stubs

**Magic Stubs** implements your functions for you.

## Demo


https://github.com/user-attachments/assets/f4d0fb4e-3b24-41d6-87ee-ff5931341219



## Technology

MagicStubs.py uses a combination of abusing source code encodings, LLM calls, and AST rewriting so you don't have to bother writing code.

## Installation

```sh
pip install magic_stubs
export OPENAI_API_KEY=...
```

## Usage

Add `# coding: magic_stubs` to the top of your python file. Then execute as normal.

test.py:
```python
# coding: magic_stubs

def print_hello_world():
    pass

print_hello_world()
```

```sh
$ python3 test.py 
Hello, World!
```


## Attribution
Inspired by and using Tsche's [https://github.com/Tsche/magic_codec/](magic_codec).
