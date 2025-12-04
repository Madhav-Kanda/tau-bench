import json
import copy
# from litellm import completion
from tau_bench.trapi_infer import completion, model_dump
from typing import List, Optional, Dict, Any

from tau_bench.agents.base import Agent
from tau_bench.envs.base import Env
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME
from termcolor import colored

from tau_bench.globals import *

from tau_bench.agents.llmagent import LLMAgent

class SubtaskChecker:
    def __init__(self, model_name: str, provider: str):
        self.model_name = model_name
        self.provider = provider

    def check_subtask(self, history, subtask):
        system_prompt = f'''
You are a helpful assistant.
A customer is interacting with a customer support agent with their request.
We have already collected some information from the customer , so we know a subtask that needs to be solved somewhere through the conversation. 
Your job is to check whether the specific subtask has yet been solved or not.      
We will provide you with the history of the conversation between the customer and the customer support agent.
We will also provide you with the subtask that needs to be checked.
Return your answer in the following json format:
{{
    "solved": <True or False>,
    "reason": <reason>
}}  
'''
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f'Conversation history: \n{history}\n\nSubtask: \n{subtask}'}]
        res = completion(
            model=self.model_name,
            custom_llm_provider=self.provider,
            messages=messages,
            response_format="json_object",
        )
        msg = model_dump(res.choices[0].message)
        res = json.loads(msg["content"])
        # print(colored(res, 'magenta'))
        return res
    
    def check_subtasks(self, history, subtasks):
        res = [self.check_subtask(history, subtask) for subtask in subtasks]
        return [i['solved'] for i in res], [i['reason'] for i in res]
    

def read_formalized_tasks(task_split='test', env_type='retail'):
    file_name = f'formalized_tasks_{env_type}_{task_split}.json'
    tasks = json.loads(open(file_name).read())
    return tasks

def read_one_shot_tasks(task_split='test', env_type='retail'):
    file_name = f'one_shot_{env_type}_{task_split}.json'
    tasks = json.loads(open(file_name).read())
    return tasks


class ToolCallingWithSubtasksCheckAgent(Agent):
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

        self.formalized_tasks_all = read_formalized_tasks()
        self.one_shot_tasks_all = read_one_shot_tasks()
        self.subtasks_checker = SubtaskChecker(model_name=self.model, provider=self.provider)

    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 30
    ) -> SolveResult:
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.wiki},
            {"role": "user", "content": obs},
        ]
        ret_messages = copy.deepcopy(messages)
        self.formalized_tasks = copy.deepcopy(self.formalized_tasks_all[task_index])
        self.one_shot_task = self.one_shot_tasks_all[task_index]
        # print(task_index)
        # print(obs)
        # print(self.formalized_tasks)
        # print(self.one_shot_task)
        # kjsd
        for k in range(max_num_steps):
            # print(f'Step: {k}')
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
            # print(colored(str(action), 'blue'))
            action_agent_time.record_time(time.time() - start_time)
            start_time = time.time()
            env_response = env.step(action)
            # print(colored(env_response, 'green'))
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
                ret_messages.extend(
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
                ret_messages.extend(
                    [
                        next_message,
                        {"role": "user", "content": env_response.observation},
                    ]
                )
            subtasks_solved, subtasks_solved_reasons = self.subtasks_checker.check_subtasks(messages, self.formalized_tasks)
            ret_messages.extend([{"role": "subtask_checker", "content": f"Subtasks solved: {subtasks_solved}"}])
            ret_messages.extend([{"role": "subtask_checker", "content": f"Subtasks solved Reason: {subtasks_solved_reasons}"}])
            # print(subtasks_solved)
            for i in range(len(subtasks_solved)-1, -1, -1):
                if subtasks_solved[i]:
                    del self.formalized_tasks[i]
            if env_response.done:
                break
        # print(colored(self.formalized_tasks, 'red'))
        return SolveResult(
            reward=reward,
            info=info,
            messages=ret_messages,
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
