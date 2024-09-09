import ast
import astor
import hashlib
import json
import appdirs
import os
from openai import OpenAI 

APP_NAME = 'magic-stubs'

MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def strip_backticks(s):
    s = s.strip()
    triple_backticks = '```'
    if s.startswith(triple_backticks):
        s = s[len(triple_backticks):]
    if s.endswith(triple_backticks):
        s = s[:-len(triple_backticks)]

    if s.startswith('python\n'):
        s = s[len('python\n'):]

    return s


def serialize_completion(completion):
    return {
        "id": completion.id,
        "choices": [
            {
                "finish_reason": choice.finish_reason,
                "index": choice.index,
                "message": {
                    "content": choice.message.content,
                    "role": choice.message.role,
                    "function_call": {
                        "arguments": json.loads(
                            choice.message.function_call.arguments) if choice.message.function_call and choice.message.function_call.arguments else None,
                        "name": choice.message.function_call.name
                    } if choice.message and choice.message.function_call else None
                } if choice.message else None
            } for choice in completion.choices
        ],
        "created": completion.created,
        "model": completion.model,
        "object": completion.object,
        "system_fingerprint": completion.system_fingerprint,
        "usage": {
            "completion_tokens": completion.usage.completion_tokens,
            "prompt_tokens": completion.usage.prompt_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }


def cached_llm_call(cache_dir, *args, **kwargs):
    args_str = ', '.join(map(str, args))
    kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    request_str = f"args: ({args_str}), kwargs: {{{kwargs_str}}}"
    request_hash = hashlib.sha256(request_str.encode()).hexdigest()

    cache_file_path = os.path.join(cache_dir, f'{request_hash}.txt')

    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as f:
            lines = f.readlines()
        if len(lines) > 1:
            cached_data = lines[1].strip()
            return json.loads(cached_data)
    
    completion = client.chat.completions.create(*args, **kwargs)

    completion_json = json.dumps(serialize_completion(completion))

    with open(cache_file_path, 'w') as f:
        f.write(request_str + '\n')
        f.write(completion_json)
    return json.loads(completion_json)
    

def is_function_in_class(func_node, tree):
    if not isinstance(func_node, ast.FunctionDef):
        raise ValueError("The provided node is not a function.")

    class ParentVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_class = False
            self.function_node = None
        
        def visit_ClassDef(self, node):
            if self.function_node in [n for n in ast.walk(node)]:
                self.in_class = True
            self.generic_visit(node)

    visitor = ParentVisitor()
    visitor.function_node = func_node
    visitor.visit(tree)

    return visitor.in_class


class ImplementFunctions(ast.NodeTransformer):
    def __init__(self, all_code, tree):
        super().__init__()
        self.all_code = all_code
        self.tree = tree

    def _get_end_line(self, node):
        if hasattr(node, 'body') and node.body:
            last_stmt = node.body[-1]
            return getattr(last_stmt, 'lineno', node.lineno)
        return node.lineno

    def visit_FunctionDef(self, node):
        start_line = node.lineno
        end_line = self._get_end_line(node)
        
        code_lines = self.all_code.splitlines()
        function_stub = '\n'.join(code_lines[start_line-1:end_line])
        
        cache_dir = appdirs.user_cache_dir(appname=APP_NAME)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        completion = cached_llm_call(cache_dir, model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful programming assistant which takes stubs of python code and returns fully implemented function. Return ONLY any required imports followed by the function implementation, all wrapped in triple backticks (```). Return NO other code. Do NOT return copies of any code from the 'Code Context'. This includes parts of wrapping classes. You may modify the function signature only if needed for it to function, e.g. if the function is a class method but is missing the self parameter."},
                {"role": "user", "content": f"Code context:{self.all_code}"},
                {"role": "user", "content": f"Function stub:{function_stub}"},
                {"role": "user", "content": f"Function stub line numbers: start:{start_line} end:{end_line}"},
                {"role": "user", "content": f"Function stub is inside class: {is_function_in_class(node, self.tree)}"}
            ]
        )

        raw_response = completion['choices'][0]['message']['content']
        response = strip_backticks(raw_response)
        new_ast = ast.parse(response)
        return new_ast.body
    
def remove_coding_line_if_present(source_code):
    """
    Normally this preprocessor is called with the
    `# coding: magic_stubs` line already removed.
    However if the generated code crashes, it will
    be called again during the generation of the
    stack trace, and in this case the `# coding ...`
    line will not have been removed.

    We solve this by stripping the  `# coding ...`
    line from the context if present, ensuring the
    context is the same on subsequent calls even in
    the case of crashes.
    """
    magic_lines = ('# coding: magic_stubs', '# coding: magic-stubs')
    if source_code.startswith(magic_lines):
        return source_code[source_code.index('\n'):]
    return source_code


def preprocess(source_code: str):
    source_code = remove_coding_line_if_present(source_code)
    tree = ast.parse(source_code)
    transformer = ImplementFunctions(source_code, tree)
    transformed_tree = transformer.visit(tree)

    new_source_code = astor.to_source(transformed_tree)

    # Add a newline at start of file as first line will be dropped since it is expected to contain the magic line.
    new_source_code = '\n' + new_source_code

    # print('new_source_code:\n---\n', new_source_code, '---')

    return new_source_code