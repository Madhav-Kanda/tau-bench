import json  
import pandas as pd
from enum import Enum
from collections import Counter
from statistics import mean, median, stdev, variance, multimode
from llmagent import LLMAgent

class FailureCase(Enum):
    SYSTEM_OR_TOOL_FAILURE = 1
    UNSPECIFIED_TASK_OR_AMBIGUOUS_USER_INTENT = 2
    INCORRECT_PLAN_GENERATION = 3
    INCORRECT_PLAN_EXECUTION = 4
    INCONCLUSIVE = 5
    HALLUCINATING_FACTS = 6

class Failure:
    def __init__(self, task_id, failure_case, description, step_number):
        self.task_id = task_id
        self.failure_case = failure_case
        self.description = description
        self.step_number = step_number

class Report:
    def __init__(self, task_id):
        self.task_id = task_id
        self.failures = []
        self.num_judges = 0

    def add_failure(self, failure):
        self.failures.append(failure)
        self.num_judges += 1

    def to_dict(self):
        """Convert Report to a JSON-serializable dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if key == 'failures':
                # Convert Failure objects to JSON-serializable format
                result[key] = [
                    {
                        'task_id': failure.task_id,
                        'failure_case': str(failure.failure_case),
                        'description': failure.description,
                        'step_number': failure.step_number
                    }
                    for failure in value
                ]
            else:
                result[key] = value
        return result

    def compute_stats(self, gt_failure):
        failure_cases = [f.failure_case for f in self.failures]
        step_numbers = [f.step_number for f in self.failures]
        gt_failure_case = gt_failure.failure_case
        gt_step_number = gt_failure.step_number
        total = len(self.failures)

        if total == 0:
            raise ValueError("No failures to analyze.")

        # --- Failure Case Stats ---
        failure_count = Counter(failure_cases)
        # Convert enum keys to strings for JSON serialization
        self.frequency = {str(k): v for k, v in failure_count.items()}
        self.most_common_failure = str(failure_count.most_common(1)[0][0])
        self.modes = [str(mode) for mode in multimode(failure_cases)]
        
        # Convert enum values to integers for statistical calculations
        failure_values = [fc.value for fc in failure_cases]
        self.mean = mean(failure_values)
        self.median = median(failure_values)
        self.std_dev = stdev(failure_values) if total > 1 else 0.0
        self.variance = variance(failure_values) if total > 1 else 0.0
        self.min = min(failure_values)
        self.max = max(failure_values)
        # Convert enum keys to strings for JSON serialization
        self.proportions = {str(k): v / total for k, v in failure_count.items()}

        # --- Step Number Stats ---
        self.step_mean = mean(step_numbers)
        self.step_median = median(step_numbers)
        self.step_std_dev = stdev(step_numbers) if total > 1 else 0.0
        self.step_variance = variance(step_numbers) if total > 1 else 0.0
        self.step_min = min(step_numbers)
        self.step_max = max(step_numbers)

        # --- Comparison to Ground Truth ---
        failure_matches = [fc == gt_failure_case for fc in failure_cases]
        step_abs_errors = [abs(s - gt_step_number) for s in step_numbers]

        self.failure_case_accuracy = sum(failure_matches) / total
        self.step_mae = mean(step_abs_errors)
        self.step_error_distribution = dict(Counter(step_abs_errors))

        self.gt_failure_case = str(gt_failure.failure_case)
        self.gt_step_number = gt_failure.step_number
        self.gt_failure_description = gt_failure.description

    

def convert_to_failure_case(case_str):
    case_str = case_str.strip().lower()
    if case_str == "system or tool failure":
        return FailureCase.SYSTEM_OR_TOOL_FAILURE
    elif case_str == "underspecified task or intent":
        return FailureCase.UNSPECIFIED_TASK_OR_AMBIGUOUS_USER_INTENT
    elif case_str == "underspecified task and intent":
        return FailureCase.UNSPECIFIED_TASK_OR_AMBIGUOUS_USER_INTENT
    elif case_str == "incorrect plan generation":
        return FailureCase.INCORRECT_PLAN_GENERATION
    elif case_str == "incorrect plan execution":
        return FailureCase.INCORRECT_PLAN_EXECUTION
    elif case_str == "inconclusive":
        return FailureCase.INCONCLUSIVE
    elif case_str == "hallucinating facts":
        return FailureCase.HALLUCINATING_FACTS
    else:
        raise ValueError(f"Unknown failure case: {case_str}")

def load_failures_from_csv(file_path):
    df = pd.read_csv(file_path)
    failures = []
    for _, row in df.iterrows():
        task_id = row['Task_id']
        failure_case = convert_to_failure_case(row['Failure cases'])
        description = row['Details']
        step_number = row['Step Number']
        failure = Failure(task_id, failure_case, description, step_number)
        failures.append(failure)
    return failures


class LLMJudge(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def judge_response(self, task_id, trajectory, ground_truth, outputs=None):
        system_prompt = '''
You are an expert judge.
You will be provided with a trajectory of an agent's interaction with a user.
However, the agent failed in serving the user.
We have shortlisted a set of failure cases.
Your job is to map the trajectory to one of the failure cases.
The failure cases are:
1. System or tool failure: cases when the system or a tool call failed even though the agent did the right thing. 
2. Unspecified task or ambiguous user intent: cases when the user's intent is unclear, complex or not well-defined.
3. Incorrect plan generation: cases when you you can conclusively determine from the conversation that the agent did not suggest the right sequence of steps as per the user's intent. For e.g it was evident from the conversation that the user wanted to modify an order but the agent misinterpreted it as cancel an order.
4. Incorrect plan execution: cases when you you can conclusively determine from the conversation that the agent planned to do something correctly but executed it incorrectly. For e.g it was evident from the conversation that the agent understood it needs to modify the order and intended to do it but ended up cancelling it.
5. Incorrect plan execution or generation (inconclusive): cases when you cannot definitely conclude whether the plan generation was incorrect or the execution was incorrect. USE THIS ONLY IF CHOICES 3 AND 4 DO NOT APPLY.
6. Hallucinating facts: cases when the system generates information that is not grounded in the provided context like incorrect function arguments, or incorrect system policies.
You will be provided with the trajectory of the agent's conversation with the user.
You will also be provided with a sequence of ground truth tool calls that the agent should have made.
Further, sometimes you may also be provided with a set of responses that the agent should have made in its response to the user. Along with them, we will supply a boolean value indicating whether the agent's response included that output or not.
Each step in the trajectory has an index number. You are also required to pin point the exact step in the trajectory where the failure occurred.

Output a JSON object in the following format:
{{
    "reason_for_failure": <string>,
    "failure_case": <int 1-6>,
    "reason_for_index": <string>,
    "index": <int>,
}}
'''
        if outputs is None:
            user_message = f'Conversation: {trajectory}\nGround Truth: {ground_truth}'
        else:
            user_message = f'Conversation: {trajectory}\nGround Truth: {ground_truth}\nResponses: {outputs}'
        print(self.llm_client.model)
        response = self.llm_client.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format="json_object",
        )
        completion = response.choices[0].message.content.strip()
        try:
            completion = json.loads(completion)
            required_keys = ["failure_case", "reason_for_failure", "index"]
            for key in required_keys:
                if key not in completion:
                    raise ValueError(f"Missing required key: {key}")
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"Error parsing LLM response: {e}")
            
        return Failure(
            task_id=task_id,
            failure_case=FailureCase(completion["failure_case"]),
            description=completion["reason_for_failure"],
            step_number=completion["index"]
        )

def judge_trajectories(num_runs=1):
    api_version = '2025-03-01-preview'  # Ensure this is a valid API version see: https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation#latest-ga-api-release
    model_name = 'o3'  # Ensure this is a valid model name
    model_version = '2025-04-16'  # Ensure this is a valid model version
    deployment_name = "o3_2025-04-16" #re.sub(r'[^a-zA-Z0-9-_]', '', f'{model_name}_{model_version}')  # If your Endpoint doesn't have harmonized deployment names, you can use the deployment name directly: see: https://aka.ms/trapi/models

    judge = LLMJudge(api_version=api_version, model_name=model_name, model_version=model_version, deployment_name=deployment_name)
    log_file = 'tool-calling-l0-4o-with-index.json'
    
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Error loading {log_file}: {e}")
    
    responses = []
    for i in range(len(data)):
        if data[i]['reward'] > 0:
            continue
        responses.append(Report(data[i]['task_id']))
    for j in range(num_runs):
        counter = 0
        for i in range(len(data)):
            if data[i]['reward'] > 0:
                continue
            assert(responses[counter].task_id == data[i]['task_id']), f"Task ID mismatch at index {i}: {responses[counter].task_id} != {data[i]['task_id']}"
            print(f"Processing run {j + 1}, entry {i + 1}/{len(data)}")
            try:
                trajectory = data[i]['traj']
                ground_truth = data[i]['info']['task']['actions']
                try:
                    outputs = data[i]['info']['reward_info']['info']['outputs']
                except Exception as e:
                    outputs = None
                task_id = data[i]['task_id']
                res = judge.judge_response(task_id, trajectory, ground_truth, outputs)
                responses[counter].add_failure(res)
                counter += 1
            except KeyError as e:
                raise RuntimeError(f"Missing key {e} in data entry {i}")
            except Exception as e:
                raise RuntimeError(f"Error processing data entry {i}: {e}")
    return responses

def filter_task_ids(responses, ground_truth_failures):
    task_ids = [failure.task_id for failure in ground_truth_failures]
    filtered_responses = [response for response in responses if response.task_id in task_ids]
    return filtered_responses

def sort_responses_by_task_id(responses):
    return sorted(responses, key=lambda x: x.task_id)

def validate_responses(responses: list[Report], ground_truth_failures: list[Failure]):
    for i in range(len(responses)):
        print(responses[i].task_id, ground_truth_failures[i].task_id)
    for i in range(len(responses)):
        assert responses[i].task_id == ground_truth_failures[i].task_id, f"Task ID mismatch at index {i}: {responses[i].task_id} != {ground_truth_failures[i].task_id}"
    return

def analysis(data):
    correct_cases = 0
    incorrect_cases = 0
    correct_distance = 0
    incorrect_distance = 0
    for task in data:
        print(f"{task['most_common_failure'].split('.')[1]},{task['std_dev']},{task['step_mean']},{task['step_std_dev']}")
        if task['most_common_failure'] == task['gt_failure_case']:
            correct_cases += 1
            correct_distance += abs(task['step_mean'] - task['gt_step_number'])
        else:
            incorrect_cases += 1
            incorrect_distance += abs(task['step_mean'] - task['gt_step_number'])
    print(f"Correct cases: {correct_cases}, Incorrect cases: {incorrect_cases}")
    print(f"Average distance for correct cases: {correct_distance/correct_cases if correct_cases > 0 else 0}, Average distance for incorrect cases: {incorrect_distance/incorrect_cases if incorrect_cases > 0 else 0}, Overall average distance: {(correct_distance + incorrect_distance)/(correct_cases + incorrect_cases) if (correct_cases + incorrect_cases) > 0 else 0}")

def main():
    file_name = "ground_truth_failures_tau_bench.csv"
    try:
        ground_truth_failures = load_failures_from_csv(file_name)
        responses = judge_trajectories(num_runs=5)
        filtered_responses = filter_task_ids(responses, ground_truth_failures)
        sorted_responses = sort_responses_by_task_id(filtered_responses)
        validate_responses(sorted_responses, ground_truth_failures)
        
        for i, response in enumerate(sorted_responses):
            response.compute_stats(ground_truth_failures[i])
            
        analysis(sorted_responses)
        output_file = "llm_judge_responses_multiple_runs.json"  
        with open(output_file, 'w') as f:
            json.dump([response.to_dict() for response in sorted_responses], f, indent=4)
        
        print(f"Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
    