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

Add `# coding: magic_stubs` to the top of your python file. Then execute as normal. Magic Stubs will automatically fill in your function definitions where needed.

hello_world.py:
```python
# coding: magic_stubs

def print_hello_world():
    pass

print_hello_world()
```

```sh
$ python3 hello_world.py 
Hello, World!
```

## Examples

### FizzBuzz

```python
$ cat examples/fizzbuzz.py 
# coding: magic_stubs
def fizzbuzz(n):
    pass

print(' '.join([fizzbuzz(n) for n in range (1, 21)]))
```

```sh
$ python3 examples/fizzbuzz.py 
1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz 16 17 Fizz 19 Buzz
```


### Mandelbrot Set

```python
$ cat examples/mandelbrot.py 
# coding: magic_stubs
def get_string_representation_of_mandelbrot_set():
    pass

print(get_string_representation_of_mandelbrot_set())
```

```sh
$ python3 examples/mandelbrot.py 
       
                                                                                
                                                 ***                            
                                               ******                           
                                                *****                           
                                       **   *************                       
                                        ***********************                 
                                    * ************************                  
                                    ***************************                 
                                    ****************************                
                       ********    ******************************               
                     ************ ******************************                
                     ******************************************                 
*************************************************************                   
                     ******************************************                 
                     ************ ******************************                
                       ********    ******************************               
                                    ****************************                
                                    ***************************                 
                                    * ************************                  
                                        ***********************                 
                                       **   *************                       
                                                *****                           
                                               ******                           
                                                 ***                            
        
```



## Attribution
Inspired by and using Tsche's [magic_codec](https://github.com/Tsche/magic_codec/).
