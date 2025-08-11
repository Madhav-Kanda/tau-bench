import json
from termcolor import colored
from llmagent import LLMAgent
from libgen_utils import *

class FunctionSuggestionAgent(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def suggest_funcs(self, tasks, library):
        system_prompt = f'''
You are an expert at generating functions from tasks.
You will be given a list of conversations between a user and an assistant.
Your task is to propose high-level functions that are commonly used in solving the user's requests.
You are also given the current library of already defined functions.
You need to suggest one function that can be added to this library and can be used in most of the observed tasks.
Output only the name of the function, its arguments and the description in the following json format:
{{
    "name": <name of the function>,
    "arguments": <arguments of the function>,
    "description": <description of the function>
}}
'''
        user_message = "\n".join(f"Conversation: {task['traj']}" for task in tasks)
        user_message += f"\nCurrent Library: {library}"
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format="json_object",
        )
        completion = response.choices[0].message.content.strip()
        completion = json.loads(completion)
        return completion

class LibRankerAgent(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def rank_funcs(self, funcs):
        system_prompt = f'''
You are an expert in creating a library of functions.
You will be given a list of functions that are are defined.
You are also given a list of functions that we wish to define. 
However, while defining a function, you may need the other one. 
So, your task is to rank the functions in such a way that to define a function with a lower rank we do not need the function with a higher rank.
So, basically give a topological sort.
Output in the following format:
function_1
function_2
...
Just output the function names in the correct order.       
Do not output any explanation or anything else. 
If there are multiple functions that can be defined, prefer the one that has more utility.
'''
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(funcs)},
            ],
        )
        completion = response.choices[0].message.content.strip()
        return completion
    

class FuncDefinitionAgent(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_func(self, library, new_func, tasks):
        system_prompt = f'''
You are an expert in writing new functions. 
You will be given a list of conversations between a user and an assistant.
There is a library of functions that can be used to solve the queries.
However, the user has suggested a new function that would be helpful to add to the current set.
Your task is to define the new function.
You can use the functions in the current set.
You can use the queries and the steps taken to solve them to understand what the function does.    
Do not use any function that is not in the current set.
Remember the all the inputs to the function must be string. You can typcast them internally if you want. 
For example, if you want an input parameter x to be a string, you should expect that the user will provide it as a string.
You can internally say x = str(x).
Regardless of the types, in the function definition, do not give any type hints.
Also, make sure that your function has a doc string.
Output a JSON object in the following fomat:
{{
    "new_function": <new_function>,
    "explanation": <explanation>
}}
'''
        user_message = f'Current available functions: {library}\nNew function: {new_func}\nSolved Tasks: {tasks}'
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format="json_object"
        )
        completion = response.choices[0].message.content.strip()
        completion = json.loads(completion)
        # print(completion)
        return completion['new_function']

class DocStringGenerator(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_docstring(self, func):
        system_prompt = f'''
You are an expert in writing docstrings for functions.
You will be given a function along with a docstring.
Your task is to change the docstring for the function to the following format:
{{
  "type": "function",
  "function": {{
    "name": "get_orders_by_status",
    "description": "<full free-text docstring here>",
    "parameters": {{
      "type": "object",
      "properties": {{}},
      "required": []
    }}
  }}
}}
Output only the format in the following json format:
{{
    "explanation": <explanation of the changes>
    "function": <updated function with docstring>,
}}
'''
        user_message = f'Function {func}'
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format="json_object"
        )
        completion = response.choices[0].message.content.strip()
        completion = json.loads(completion)
        completion = completion['function']
        return completion

class FuncCorrector(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def correct_function(self, func):
        system_prompt = f'''
You are an expert at predicting problems with functions.
The user generated a function to be used by an LLM agent.
Although the function is conceptually fine, since it is called by an LLM agent, it may be incorrect.
The LLM may not call the function with the correct arguments or expected types.
Your task is to predict such problems and correct the function by trying to convert the argument into the required format first.
In case you cannot handle things, make sure top return a proper error message so that someone can look at the logs and interpret the error.
You need to make sure that the docstring is in a proper format as before.
Output a JSON object in the following fomat:
{{
    "new_function": <new_function>,
    "explanation": <explanation>
}}
'''
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'{func}'},
            ],
            response_format="json_object"
        )
        completion = response.choices[0].message.content.strip()
        completion = json.loads(completion)
        return completion["new_function"]


class FuncCorrectorFromTrajectories(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def correct_function(self, old_library, new_func, new_trajectory, new_func_def_history):
        system_prompt = f'''
You are an expert at debugging and improving functions.
The user had to solve a task and they had access to a list of tools they could use.
Later, there was an addition to the set of functions, and the user solved the task again.
However, it did not improve the results because the function was not defined properly.
Most errors correcspond to the argument parsing. The input was expected to be of a format but it was not.
You can correct these things by adding some additional code that converts the arguments into the required type.
Your job is to look at the trajectories and improve the newly added function.
Output a JSON object in the following fomat:
{{
    "explanation": <explanation>,
    "new_function": <new_function>,
}}
Only change the things that caused the mistake. Do not predict any new changes.
'''
        messages = [{"role": "system", "content": system_prompt}] + new_func_def_history + [{"role": "user", "content": f'Old Library: {old_library}\nNew Function: {new_func}\n\nNew Trajectory: {new_trajectory}'}]
        response = self.llm_client.complete(
            model=self.model_name,
            messages=messages,
            response_format="json_object"
        )
        completion = response.choices[0].message.content.strip()
        completion = json.loads(completion)
        # print(completion)
        # ljkdf
        return completion["new_function"], completion["explanation"]


# def get_tool_description(tool):
#     """Parses tool metadata and returns a Func object."""
#     args = []

#     for param_name, param_schema in tool.inputSchema['properties'].items():
#         param_type = param_schema.get('type')
#         default = param_schema.get('default', None)
#         args.append((param_name, param_type, default))

#     return Func(
#         name=tool.name,
#         args=args,
#         description=tool.description
#     )


# def extract_docstring_from_function_string(function_str: str) -> str:
#     try:
#         tree = ast.parse(function_str)
#         for node in tree.body:
#             if isinstance(node, ast.FunctionDef):
#                 return ast.get_docstring(node)
#     except SyntaxError as e:
#         print(f"Syntax error while parsing: {e}")
#     return None

# def is_docstring_json(docstring: str) -> bool:
#     if not docstring:
#         return False
    
#     def clean_trailing_commas(s):
#         # Remove trailing commas before } or ]
#         return re.sub(r',(\s*[}\]])', r'\1', s)
    
#     doc_cleaned = clean_trailing_commas(docstring)
#     try:
#         json.loads(doc_cleaned)
#         return True
#     except json.JSONDecodeError:
#         return False


def correct_func_from_traj(old_library, new_func, new_trajectory, new_func_def_history):
    agent = FuncCorrectorFromTrajectories()
    return agent.correct_function(old_library, new_func, new_trajectory, new_func_def_history)


def get_new_func(tasks, old_library, verbose=True):
    ####### AGENTS #######
    lib_gen_agent = FunctionSuggestionAgent()
    lib_ranker_agent = LibRankerAgent()
    func_def_agent = FuncDefinitionAgent()
    doc_string_generator = DocStringGenerator()
    func_corrector_agent = FuncCorrector()
    
    suggested_func = lib_gen_agent.suggest_funcs(tasks, old_library)
    # print(suggested_funcs)
    # if len(suggested_funcs) > 1:
    #     rank = lib_ranker_agent.rank_funcs(suggested_funcs)
    #     func_name = rank.splitlines()[0].strip()
    #     suggested_func = None
    #     for func in suggested_funcs:
    #         if func['name'] == func_name:
    #             suggested_func = func
    #             break
    #     if suggested_func is None:
    #         print(colored("Function not found", 'red'))
    #         for func in suggested_funcs:
    #             print(colored(func['name'], 'red'))
    #         return
    # else:
    #     suggested_func = suggested_funcs[0]
    
    if verbose:
        print(colored(f'Suggested function name: {suggested_func['name']}', 'blue'))
        
    
    new_func = func_def_agent.define_func(old_library, suggested_func, tasks)

    gen_flag = False
    while not gen_flag:
        new_func = doc_string_generator.update_docstring(new_func)
        doc = extract_docstring_from_function_string(new_func)
        if is_docstring_json(doc):
            gen_flag = True
        else:
            gen_flag = True
    if verbose:
        print(colored(f'Proposed function definition:\n{new_func}', 'yellow'))

    gen_flag = False
    while not gen_flag:
        new_func = func_corrector_agent.correct_function(new_func)
        doc = extract_docstring_from_function_string(new_func)
        if is_docstring_json(doc):
            gen_flag = True
        else:
            gen_flag = True
    if verbose:
        print(colored(f'Corrected function definition:\n{new_func}', 'green'))

    return suggested_func['name'], new_func
