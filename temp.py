import json

file = "llm_judge_responses_multiple_runs.json"
data = json.load(open(file, "r"))

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
print(f"Average distance for correct cases: {correct_distance/correct_cases if correct_cases > 0 else 0}, Incorrect distance: {incorrect_distance/incorrect_cases if incorrect_cases > 0 else 0}, Total distance: {(correct_distance + incorrect_distance)/(correct_cases + incorrect_cases) if (correct_cases + incorrect_cases) > 0 else 0}")