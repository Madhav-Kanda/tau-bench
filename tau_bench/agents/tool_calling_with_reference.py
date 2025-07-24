# Copyright Sierra

import json
# from litellm import completion
from tau_bench.trapi_infer import completion, model_dump
from typing import List, Optional, Dict, Any

from tau_bench.agents.base import Agent
from tau_bench.envs.base import Env
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME
from termcolor import colored
import os
from tau_bench.globals import *

def get_old_trajectory(task_id):
    old_logs_folder = "final_results/tool-calling-none-0.1_range_0-100_user-none-llm_06232025.json"
    logs = json.load(open(old_logs_folder, 'r'))
    trajectory = logs[int(task_id)]['traj'][1:]
    return trajectory

class ToolCallingAgentWithReference(Agent):
    def __init__(
        self,
        tools_info: List[Dict[str, Any]],
        wiki: str,
        model: str,
        provider: str,
        temperature: float = 0.0,
    ):
        self.tools_info = tools_info
        self.wiki = wiki
        self.model = model
        self.provider = provider
        self.temperature = temperature

    def solve(
        self, env: Env, new_func_name, task_index: Optional[int] = None, max_num_steps: int = 30
    ) -> SolveResult:
        self.old_trajectory = get_old_trajectory(task_index)
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0
        self.new_func_name = new_func_name
        system_prompt = f'''You are also given the trajectory of the user's interaction with another agent. But now, we have a new function added to the tool set. You need to use this new function to improve the trajectory. Hopefully, this new function can combine several steps in the original trajectory into a single step. So, you should prioritise using this function. The new function is: {new_func_name}. Along with each invocation of this tool, also output the steps in the older trajectory that you combine. The older trajectory is: {self.old_trajectory}'''
        system_prompt = self.wiki + "\n" + system_prompt
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": obs},
        ]
        # print(colored(self.tools_info, 'red'))
        for k in range(max_num_steps):
            start_time = time.time()
            res = completion(
                messages=messages,
                model=self.model,
                custom_llm_provider=self.provider,
                tools=self.tools_info,
                temperature=self.temperature,
            )
            temp = res.choices[0].message
            next_message = model_dump(temp)
            # next_message = res.choices[0].message
            # total_cost += res._hidden_params["response_cost"]
            total_cost += res.usage.total_tokens
            action = message_to_action(next_message)
            action_agent_time.record_time(time.time() - start_time)
            start_time = time.time()
            env_response = env.step(action)
            # print("Action\n", action)
            # print("Env Response\n", env_response)
            # print()
            env_time.record_time(time.time() - start_time)
            reward = env_response.reward
            info = {**info, **env_response.info.model_dump()}
            if action.name != RESPOND_ACTION_NAME:
                next_message["tool_calls"] = next_message["tool_calls"][:1]
                messages.extend(
                    [
                        next_message,
                        {
                            "role": "tool",
                            "tool_call_id": next_message["tool_calls"][0]["id"],
                            "name": next_message["tool_calls"][0]["function"]["name"],
                            "content": env_response.observation,
                        },
                    ]
                )
            else:
                messages.extend(
                    [
                        next_message,
                        {"role": "user", "content": env_response.observation},
                    ]
                )
            if env_response.done:
                break
        return SolveResult(
            reward=reward,
            info=info,
            messages=messages,
            total_cost=total_cost,
            records={}
        )


def message_to_action(
    message: Dict[str, Any],
) -> Action:
    if "tool_calls" in message and message["tool_calls"] is not None and len(message["tool_calls"]) > 0 and message["tool_calls"][0]["function"] is not None:
        tool_call = message["tool_calls"][0]
        return Action(
            name=tool_call["function"]["name"],
            kwargs=json.loads(tool_call["function"]["arguments"]),
        )
    else:
        return Action(name=RESPOND_ACTION_NAME, kwargs={"content": message["content"]})
