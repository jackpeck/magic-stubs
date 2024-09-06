# def preprocess(data: str):
#     print("Hello World - from preprocessor")
#     # 1/0



#     return data


import ast
import astor

from openai import OpenAI 
import os

MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))




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


class AddLogDecorator(ast.NodeTransformer):
    def __init__(self, all_code):
        super().__init__()
        self.all_code = all_code

    def visit_FunctionDef(self, node):
        # print(str(node))

        print(astor.to_source(node))
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
        
        function_stub = astor.to_source(node)

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful programming assistant which takes stubs of python code and returns fully implemented function. Return only the code wrapped in triple backticks (```)."},
                {"role": "user", "content": f"Code context:{self.all_code}"},
                {"role": "user", "content": f"Function stub:{function_stub}"}
            ]
        )
        response = completion.choices[0].message.content

        print('response:', response, '-')

        # response = """```def print_hello_world():\n    print("Hello, World!")```"""

        response = strip_backticks(response)

        # return node

        # print(response)

        new_ast = ast.parse(response)
        # return node
        return new_ast.body[0]


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