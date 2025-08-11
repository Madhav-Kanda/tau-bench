import json
import copy
import ast
# from litellm import completion
from tau_bench.trapi_infer import completion, model_dump
from typing import List, Optional, Dict, Any

from tau_bench.agents.base import Agent
from tau_bench.envs.base import Env
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME
from termcolor import colored

from tau_bench.globals import *

from tau_bench.agents.llmagent import LLMAgent

class SubtaskChecker(LLMAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    "reason": <reason>
    "solved": <True or False>,
}}  
'''
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f'Conversation history: \n{history}\n\nSubtask: \n{subtask}'}]
        res = self.llm_client.complete(model = self.model_name, messages=messages, response_format="json_object").choices[0].message['content']
        res = json.loads(res)
        # print(colored(res, 'magenta'))
        return res
    
    def check_subtasks(self, history, subtasks):
        res = [self.check_subtask(history, subtask) for subtask in subtasks]
        return [i['solved'] for i in res], [i['reason'] for i in res]
    
class SubtaskCreator(LLMAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_subtasks_(self, history, current_subtasks, subtasks_status):
        system_prompt = f'''
You are a helpful assistant and an expert at extracting important information from a conversation.
A customer is interacting with a customer support agent with their request.
We are trying to do some book-keeping by maintaining the concrete intents that the customer wants.
You will be provided with a partial conversation between the customer and the agent.  
Your job is to extract the sub-intents that the customer is trying to solve.
You may also be prided with the current set of intents that we have already extracted.
You will also be given whther the subtasks have been solved in the conversation so far or not.
You need to provide the following outputs:
1. An updated list of intents
2. A point-wise reasoning of the intents in the list
3. Whether each intent in the list is solved or not
4. The reason for why each intent in the list is solved or not. 
The reason should precede the respective answers, i.e., return your answer in the following json format:
{{
    "reason for intent list": <Reasoning of the intents in the updated list>
    "intent list": <updated list>,
    "reason for intent status": <Reason for each intent being solved or not>,
    "intent status": <True or False>,
}}  
Make sure that all 4 lists are of the same size
'''
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f'Conversation history: \n{history}\n\nCurrent intents: \n{current_subtasks}\n\nIntents status: \n{subtasks_status}'}]
        res = self.llm_client.complete(model = self.model_name, messages=messages, response_format="json_object").choices[0].message['content']
        res = json.loads(res)
        # print(colored(res, 'magenta'))
        return res
    
    def update_subtasks(self, history, current_subtasks, subtasks_status):
        res = self.update_subtasks_(history, current_subtasks, subtasks_status)
        # print(res)
        # print(res['reason'])
        # print(res['intent list'], type(res['intent list']))
        # print(res['intent status'], type(res['intent status']), type(res['intent status'][0]))
        intent_list = (res['intent list'])
        intent_status = (res['intent status'])
        reason1 = (res['reason for intent list'])
        reason2 = (res['reason for intent status'])
        # kdfjs
        return intent_list, intent_status, reason1, reason2
    

def read_formalized_tasks(task_split='test', env_type='retail'):
    file_name = f'formalized_tasks_{env_type}_{task_split}.json'
    tasks = json.loads(open(file_name).read())
    return tasks

def read_one_shot_tasks(task_split='test', env_type='retail'):
    file_name = f'one_shot_{env_type}_{task_split}.json'
    tasks = json.loads(open(file_name).read())
    return tasks


class ToolCallingWithDynamicSubtasksWithFeedback(Agent):
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

        self.subtasks_creator = SubtaskCreator()
        self.subtasks_checker = SubtaskChecker()

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
        self.subtasks = []
        self.subtasks_solved = []
        max_steps_after_done = 4
        after_done = -1
        
        for k in range(max_num_steps):
            if after_done >= max_steps_after_done:
                break
            if after_done >= 0:
                after_done += 1
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
                self.subtasks, self.subtasks_solved, reason1, reason2 = self.subtasks_creator.update_subtasks(messages, self.subtasks, self.subtasks_solved)
                ret_messages.extend(
                    [
                        next_message,
                        {"role": "user", "content": env_response.observation},
                        {"role": "subtask_creator", "content": f"Subtasks: {self.subtasks}"},
                        {"role": "subtask_creator", "content": f"Subtasks Reason: {reason1}"},
                        {"role": "subtask_creator", "content": f"Subtasks solved: {self.subtasks_solved}"},
                        {"role": "subtask_creator", "content": f"Subtasks Reason: {reason2}"},
                    ]
                )
            if env_response.done and after_done == -1:
                after_done = 0
                pending_subtasks = [self.subtasks[i] for i in range(len(self.subtasks)) if not self.subtasks_solved[i]]
                if len(pending_subtasks) != 0:
                    messages.extend([{"role": "assistant", "content": f"Thought: There are still some pending unsolved tasks from request including {pending_subtasks}"}])
                    ret_messages.extend([{"role": "assistant", "content": f"Thought: There are still some pending unsolved tasks from request including {pending_subtasks}"}])
                    after_done = 0
                else:
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
