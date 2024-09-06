# def preprocess(data: str):
#     print("Hello World - from preprocessor")
#     # 1/0



#     return data


import ast
import astor
import hashlib
import json
import appdirs

from openai import OpenAI 
import os

MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


APP_NAME = 'python_english'



# print("Assistant: " + completion.choices[0].message.content)


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
            print(f"Cache hit: {cache_file_path}")
            return json.loads(cached_data)
    
    completion = client.chat.completions.create(*args, **kwargs)

    completion_json = json.dumps(serialize_completion(completion))

    with open(cache_file_path, 'w') as f:
        f.write(request_str + '\n')
        f.write(completion_json)
    return json.loads(completion_json)
    

class AddLogDecorator(ast.NodeTransformer):
    def __init__(self, all_code):
        super().__init__()
        self.all_code = all_code

    def _get_end_line(self, node):
        """ Helper method to estimate the end line of a node """
        # For simplicity, assume function body ends at the end of the last statement
        # More complex cases would require better handling
        if hasattr(node, 'body') and node.body:
            last_stmt = node.body[-1]
            return getattr(last_stmt, 'lineno', node.lineno)
        return node.lineno

        # start_line = node.lineno

        # end_line = node.lineno + 1

        # stripped_src = astor.to_source(node)



    def visit_FunctionDef(self, node):
        # Extract the function's start and end line numbers
        start_line = node.lineno
        end_line = self._get_end_line(node)
        
        # Extract the relevant section from the original source code
        code_lines = self.all_code.splitlines()
        function_stub = '\n'.join(code_lines[start_line-1:end_line])
        
        # Print the function's code including comments
        print(function_stub)
        
        # print(astor.to_source(node))
        # node.

#         ast2 = ast.parse("""
# def print_hello_world():
#     print("Hello, World!")
# """)
        
#         # print(ast2.body[0])

#         return ast2.body[0]

#         # # Add the @python_english decorator to each function
#         # decorator = ast.Name(id='python_english', ctx=ast.Load())
#         # node.decorator_list.append(decorator)
#         return node

        # all_code = 
        
        # function_stub = astor.to_source(node)

        # completion = client.chat.completions.create(
        #     model=MODEL,
        #     messages=[
        #         {"role": "system", "content": "You are a helpful programming assistant which takes stubs of python code and returns fully implemented function. Return only the code wrapped in triple backticks (```)."},
        #         {"role": "user", "content": f"Code context:{self.all_code}"},
        #         {"role": "user", "content": f"Function stub:{function_stub}"}
        #     ]
        # )
        # response = completion.choices[0].message.content

        # print(os.)


        cache_dir = appdirs.user_cache_dir(appname=APP_NAME)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        

        completion = cached_llm_call(cache_dir, model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful programming assistant which takes stubs of python code and returns fully implemented function. Return only any required imports followed by the function implementation, all wrapped in triple backticks (```). Do NOT return copies of any code from the 'Code Context'"},
                {"role": "user", "content": f"Code context:{self.all_code}"},
                {"role": "user", "content": f"Function stub:{function_stub}"}
            ]
        )

        response = completion['choices'][0]['message']['content']


        # response = """```def print_hello_world():\n    print("Hello, World!")```"""

        print('response:', response, '-')

        response = strip_backticks(response)

        # return node

        # print(response)

        new_ast = ast.parse(response)
        # return node
        return new_ast.body


def preprocess(data: str):
    # Parse the file into an AST
    tree = ast.parse(data)

    # Modify the AST to add the @python_english decorator to all functions
    transformer = AddLogDecorator(data)
    transformed_tree = transformer.visit(tree)

    # Convert the modified AST back into source code
    new_source_code = astor.to_source(transformed_tree)

    # Add a newline at start of file as first line will be dropped since it is expected to contain the magic line.
    new_source_code = '\n' + new_source_code

    print('new_source_code:\n---\n', new_source_code)
    print('---')

    return new_source_code