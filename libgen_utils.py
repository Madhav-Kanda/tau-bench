import os 
import json
import asyncio
import ast
import re

from fastmcp import Client
from termcolor import colored


class Metrics:
    def __init__(self, trajectory, new_funcs):
        if isinstance(trajectory, list):
            assert(len(trajectory) == 1), "Metrics class expects a single trajectory"
            trajectory = trajectory[0]
        self.trajectory = trajectory
        self.new_funcs = new_funcs
        
        self.num_steps = 0
        self.error_in_trajectory = False
        self.task_solved = False
        self.func_called = {func: False for func in new_funcs}
        self.error_in_func = {func: False for func in new_funcs}
        self.num_calls = {func: 0 for func in new_funcs}

        self.check_trajectory()
    
    def check_trajectory(self):
        self.task_solved = self.trajectory['reward'] > 0
        self.num_steps = len(self.trajectory['traj'])
        if self.num_steps == 0:
            self.error_in_trajectory = True
            self.error_in_func = {func: True for func in self.error_in_func.keys()}

        for step in self.trajectory['traj']:
            if step['role'] == 'tool':
                if step['name'] in self.new_funcs:
                    self.func_called[step['name']] = True
                    self.num_calls[step['name']] += 1
                    if 'error' in step['content'] or 'Error' in step['content']:
                        self.error_in_trajectory = True
                        self.error_in_func[step['name']] = True
                        
    def to_dict(self):
        return {
            "num_steps": self.num_steps,
            "task_solved": self.task_solved,
            "error_in_trajectory": self.error_in_trajectory,
            "func_called": self.func_called,
            "error_in_func": self.error_in_func,
            "num_calls": self.num_calls,
            "trajectory": self.trajectory,  
            "new_funcs": self.new_funcs
        }



class Func():
    def __init__(self, name, args, description):
        self.name = name
        self.args = args
        self.description = description

    def __str__(self):
        arg_lines = []
        for name, typ, default in self.args:
            if default is not None:
                arg_lines.append(f"  - {name}: {typ} (default={default})")
            else:
                arg_lines.append(f"  - {name}: {typ}")
        args_formatted = "\n".join(arg_lines) if arg_lines else "  (no arguments)"
        
        return (
            f"Function Name: {self.name}\n"
            f"Function Arguments:\n{args_formatted}\n"
            f"Function Description: {self.description}\n"
        )
    
    def __repr__(self):
        
        return self.__str__()
    
class Library():
    def __init__(self, funcs):
        # self.funcs = [func for func in funcs if isinstance(func, Func)]
        self.funcs = [func for func in funcs]

    def add_func(self, func):
        if isinstance(func, Func):
            self.funcs.append(func)

    def get_funcs(self):
        return self.funcs

def extract_docstring_from_function_string(function_str: str) -> str:
    try:
        tree = ast.parse(function_str)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                return ast.get_docstring(node)
    except SyntaxError as e:
        print(f"Syntax error while parsing: {e}")
    return None

def is_docstring_json(docstring: str) -> bool:
    if not docstring:
        return False
    
    def clean_trailing_commas(s):
        # Remove trailing commas before } or ]
        return re.sub(r',(\s*[}\]])', r'\1', s)
    
    doc_cleaned = clean_trailing_commas(docstring)
    try:
        json.loads(doc_cleaned)
        return True
    except json.JSONDecodeError:
        return False


def get_tool_description(tool):
    """formats tool description from MCP server into a concise form for LLM prompt"""
    param_str = ''
    i = 0
    for p in tool.inputSchema['properties'].keys():
        # print(tool.inputSchema['properties'][p])
        # dlfjk
        if 'type' not in tool.inputSchema['properties'][p].keys():
            if 'anyOf' not in tool.inputSchema['properties'][p].keys():
                type = "Any"
            else:   
                type = [tool.inputSchema['properties'][p]['anyOf'][i]['type'] for i in range(len(tool.inputSchema['properties'][p]['anyOf']))]
        else:
            type = tool.inputSchema['properties'][p]['type']
        s = f'{p}:{type}'

        if 'default' in tool.inputSchema['properties'][p].keys():
            s += f' = {tool.inputSchema['properties'][p]["default"]}'
        
        if i > 0:
            param_str += ', '
        i += 1
        param_str += s
    desc = f"-{tool.name}({param_str}): {tool.description}"
    return desc

async def get_tools_(mcp_server):
    async with Client(mcp_server) as mcp_client:
        tools = await mcp_client.list_tools()
        tool_descriptions = ([
            get_tool_description(tool) for tool in tools
        ])
        return tool_descriptions
    
def get_tools(mcp_server):
    return asyncio.run(get_tools_(mcp_server))

def create_file(mcp_server_old, mcp_server_new, func_def, verbose=False):
    with open(mcp_server_old, "r") as src:
        lines = src.readlines()
    top_lines, last_lines = lines[:-2], lines[-2:]
    func_lines = [f'{line}\n' for line in func_def.splitlines()]
    if len(func_lines) == 0 or 'def' not in func_lines[0]:
        new_lines = top_lines + last_lines
    else:
        new_lines = top_lines + ['@mcp.tool()\n'] + func_lines + last_lines
    new_code = ''.join(new_lines)
    if verbose:
        print(colored(new_code, 'red'))
    with open(mcp_server_new, "w") as dst:
        dst.writelines(new_code)

if __name__ == "__main__":
    pass