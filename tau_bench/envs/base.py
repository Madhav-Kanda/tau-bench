# Copyright Sierra

import asyncio
from logging import config
import random
import os
import json
import inspect
import re
import importlib.util
import builtins

from hashlib import sha256
from tau_bench.envs.tool import Tool
from typing import Any, Callable, Dict, List, Type, Optional, Set, Union, Tuple
from fastmcp import Client
from termcolor import colored


from tau_bench.envs.user import load_user, UserStrategy
from tau_bench.types import (
    Action,
    Task,
    EnvInfo,
    EnvResetResponse,
    EnvResponse,
    RewardResult,
    RewardOutputInfo,
    RewardActionInfo,
    RESPOND_ACTION_NAME,
)
from tau_bench.envs.my_data import global_data

ToHashable = Union[
    str, int, float, Dict[str, "ToHashable"], List["ToHashable"], Set["ToHashable"]
]
Hashable = Union[str, int, float, Tuple["Hashable"], Tuple[Tuple[str, "Hashable"]]]

import logging

logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)




def load_module_from_file(filepath):
    """Dynamically load a module from a file path."""
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract_registered_tools(filepath):
    module = load_module_from_file(filepath)
    mcp_instance = getattr(module, "mcp", None)
    if mcp_instance is None:
        raise RuntimeError("No FastMCP instance found in the file.")
    
    # Await the coroutine synchronously
    tool_names = asyncio.run(mcp_instance.list_tools())

    tools_descriptions = []
    for tool in tool_names:  # 'tool_names' is a list of Tool objects
        tool_name = getattr(tool, "name", None)
        if tool_name is None:
            continue
        func = getattr(module, tool_name, None)
        if func is None:
            continue
        doc = inspect.getdoc(func)
        if not doc:
            continue
        def clean_trailing_commas(s):
            # Remove trailing commas before } or ]
            s = re.sub(r',(\s*[}\]])', r'\1', s)
            return s

        doc_cleaned = clean_trailing_commas(doc)

        try:
            description_json = json.loads(doc_cleaned)
            tools_descriptions.append(description_json)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
    return tools_descriptions



def to_hashable(item: ToHashable) -> Hashable:
    if isinstance(item, dict):
        return tuple((key, to_hashable(value)) for key, value in sorted(item.items()))
    elif isinstance(item, list):
        return tuple(to_hashable(element) for element in item)
    elif isinstance(item, set):
        return tuple(sorted(to_hashable(element) for element in item))
    else:
        return item


def consistent_hash(
    value: Hashable,
) -> str:
    return sha256(str(value).encode("utf-8")).hexdigest()


class Env(object):
    def __init__(
        self,
        data_load_func: Callable[[], Dict[str, Any]],
        tools: List[Type[Tool]],
        tasks: List[Task],
        wiki: str,
        rules: List[str],
        user_strategy: Union[str, UserStrategy],
        user_model: str,
        user_provider: Optional[str] = None,
        task_index: Optional[int] = None,
        mcp_server = None,
    ) -> None:
        super().__init__()
        self.mcp_server = os.path.normpath(mcp_server)
        self.data_load_func = data_load_func
        self.data = data_load_func()
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=2)
        # self.tools_map: Dict[str, Type[Tool]] = {
        #     tool.get_info()["function"]["name"]: tool for tool in tools
        # }
        # self.tools_info = [tool.get_info() for tool in tools]
        self.tools_info = extract_registered_tools(self.mcp_server)
        self.new_tools_list = [tool['function']['name'] for tool in self.tools_info]
        self.terminate_tools = []
        self.tasks = tasks
        if task_index is not None:
            self.task_index = task_index
        else:
            self.task_index = random.randint(0, len(tasks))
        self.task = tasks[self.task_index]
        self.wiki = wiki
        self.rules = rules
        self.user = load_user(
            user_strategy=user_strategy, model=user_model, provider=user_provider
        )
        self.actions: List[Action] = []

    def reset(self, task_index: Optional[int] = None) -> EnvResetResponse:
        if task_index is None:
            task_index = random.randint(0, len(self.tasks))
        self.task_index = task_index
        self.data = self.data_load_func()
        self.task = self.tasks[task_index]
        self.actions = []
        initial_observation = self.user.reset(instruction=self.task.instruction)
        return EnvResetResponse(
            observation=initial_observation, info=EnvInfo(task=self.task, source="user")
        )

    async def tool_call(self, function, function_args):
        mcp_client = Client(self.mcp_server)
        async with mcp_client:
            func_response = await mcp_client.call_tool(function, function_args)
            res = func_response.content[0].text
        return res

    def step(self, action: Action) -> EnvResponse:
        self.actions.append(action)

        info = EnvInfo(task=self.task)
        reward = 0
        done = False
        if action.name == RESPOND_ACTION_NAME:
            observation = self.user.step(action.kwargs["content"])
            info.source = "user"
            done = "###STOP###" in observation
        # elif action.name in self.tools_map:
        elif action.name in self.new_tools_list:
            # args = action.kwargs.copy()
            # observation = asyncio.run(self.tool_call(action.name, args))
            # print(observation)
            # dmb
            try:
                # observation = self.tools_map[action.name].invoke(
                #     data=self.data, **action.kwargs
                # )
                args = action.kwargs.copy()
                args["data"] = self.data
                observation = asyncio.run(self.tool_call(action.name, args))
            except Exception as e:
                observation = f"Error: {e}"
            info.source = action.name
            if action.name in self.terminate_tools:
                done = True
        else:
            observation = f"Unknown action {action.name}"
            info.source = action.name

        if done:
            reward_res = self.calculate_reward()
            reward = reward_res.reward
            info.reward_info = reward_res
            info.user_cost = self.user.get_total_cost()
        return EnvResponse(observation=observation, reward=reward, done=done, info=info)

    def get_data_hash(self) -> str:
        return consistent_hash(to_hashable(self.data))

    def calculate_reward(self) -> RewardResult:
        data_hash = self.get_data_hash()
        reward = 1.0
        actions = [
            action for action in self.task.actions if action.name != RESPOND_ACTION_NAME
        ]

        # Check if the database changes are correct. If they are not correct, then we set the reward to 0.
        # TODO: cache gt_data_hash in tasks.py (low priority)
        self.data = self.data_load_func()
        for action in self.task.actions:
            if action.name not in self.terminate_tools:
                self.step(action)
        gt_data_hash = self.get_data_hash()
        info = RewardActionInfo(
            r_actions=data_hash == gt_data_hash, gt_data_hash=gt_data_hash
        )
        if not info.r_actions:
            reward = 0.0

        if len(self.task.outputs) > 0:
            # check outputs
            r_outputs = 1.0
            outputs = {}
            for output in self.task.outputs:
                found = False
                for action in self.actions:
                    if (
                        action.name == RESPOND_ACTION_NAME
                        and output.lower()
                        in action.kwargs["content"].lower().replace(",", "")
                    ):
                        found = True
                        break
                outputs[output] = found
                if not found:
                    r_outputs = 0.0
                    reward = 0.0
            info = RewardOutputInfo(r_outputs=r_outputs, outputs=outputs)
            
        return RewardResult(reward=reward, info=info, actions=actions)
