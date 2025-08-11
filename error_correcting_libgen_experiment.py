import json
import subprocess
from termcolor import colored
from llmagent import LLMAgent
from libgen_utils import *
import lib_gen as lib_gen

class FunctionSuggestionAgentFromErrors(LLMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def suggest_funcs(self, trajectory, library, failure):
        system_prompt = f'''
You are an expert at generating functions from tasks.
You will be given a conversation between a user and an assistant.
But on a post-analysis, the user realised that there was something wrong with the assistant's response.
The user wants to improve the assistant's performance by suggesting a new function that can be added to the library of functions.
Hopefully, this function can be used to solve the problem.
Your task is to propose high-level functions that are commonly used in solving the user's requests.
You are also given the current library of already defined functions.
You are also given the reason of failure for the assistant.
You need to suggest one function that can be added to this library and can be used in most of the observed tasks.
Output only the name of the function, its arguments and the description in the following json format:
{{
    "name": <name of the function>,
    "arguments": <arguments of the function>,
    "description": <description of the function>
}}
'''
        user_message = f'Conversation: {trajectory}\nReason for failure: {failure}'
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

def get_new_func(tasks, train_failures, old_library, verbose=True):
    ####### AGENTS #######
    lib_gen_agent = FunctionSuggestionAgentFromErrors()
    func_def_agent = lib_gen.FuncDefinitionAgent()
    doc_string_generator = lib_gen.DocStringGenerator()
    func_corrector_agent = lib_gen.FuncCorrector()
    
    suggested_func = lib_gen_agent.suggest_funcs(tasks, old_library, train_failures)
    
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





def run_tasks(task_ids, mcp_server, output_file, agent_strategy='tool-calling', new_func_name=None):
    open(output_file, 'w').close()
    command = [
        "python", "run.py",
        "--agent-strategy", agent_strategy,
        "--env", "retail",
        "--model", "none",
        "--model-provider", "openai",
        "--user-model", "none",
        "--user-model-provider", "openai",
        "--user-strategy", "llm",
        "--max-concurrency", "10",
        "--task-ids", *map(str, task_ids),
        "--mcp-server", mcp_server,
        "--ckpt-path", output_file,
    ]
    if new_func_name:
        command += ["--new-func", new_func_name]
    subprocess.run(command)

def run_test(task_ids, mcp_server):
    run_tasks(task_ids, mcp_server, "improved_logs/test_results.json")

def run_train_chunk(train_chunk, mcp_server, new_func_name, output_file):
    run_tasks(train_chunk, mcp_server, output_file, agent_strategy='tool-calling-with-reference', new_func_name=new_func_name)
    return output_file

def generate_func(tasks, task_ids, train_failures, mcp_server_before_generation, new_mcp_server, output_folder):
    tools = get_tools(mcp_server_before_generation)
    old_library = Library(tools).get_funcs()
    ######### GET NEW FUNC CANDIDATES #######
    def_flag = False
    doc_trial = 0
    while not def_flag and doc_trial < 2:
        doc_trial += 1
        new_func_name, new_func_def = get_new_func(tasks, train_failures, old_library)
        doc = extract_docstring_from_function_string(new_func_def)
        if is_docstring_json(doc):  
            def_flag = True
    if not def_flag:
        print(colored("Failed to generate a valid function definition.", 'red'))
        return False, None, None
    print(colored(f'New function proposed: {new_func_def}', 'blue'))
    new_func_def_history = [{"role": "user", "content": "Original function: \n" + new_func_def}]

    
    ########## IMPROVE TRAJECTORIES AND FUNCTION CANDIDATES ##########
    trial = 0
    found_incorrect_trajectory = True
    max_refinement_tries = 2
    while(found_incorrect_trajectory and trial < max_refinement_tries):
        trial += 1
        ########## IMPROVE TRAJECTORIES ##########
        new_library = old_library + [new_func_def]
        open(new_mcp_server, 'w').close()
        create_file(mcp_server_before_generation, new_mcp_server, new_func_def)

        
        found_incorrect_trajectory = False
        traj_results = []
        index = -1
        for j in range(len(task_ids)):
            print(colored(task_ids[j], 'green'))
            output_file = os.path.join(output_folder, f"train_results_{task_ids[j]}.json")
            run_tasks([task_ids[j]], new_mcp_server, output_file, agent_strategy='tool-calling-with-reference', new_func_name=new_func_name)
            trajectory = json.load(open(output_file, 'r'))[0]
            res = Metrics(trajectory, [new_func_name])
            traj_results.append(res.error_in_func[new_func_name])
            
            print(colored(f'Trajectory check results: {traj_results[j]}', 'cyan'))
            if traj_results[j] == True:
                found_incorrect_trajectory = True
                index = j
                break     
        if not found_incorrect_trajectory:
            break      
        
        print("wrong trajectory", task_ids[index])
        new_trajectory = trajectory
        improved_func_def, explanation = lib_gen.correct_func_from_traj(old_library, new_func_def, new_trajectory, new_func_def_history)
        new_func_def = improved_func_def

        print(colored(f'Corrected proposed function: {new_func_def}', 'green'))
        print(colored(f'Explanation: {explanation}', 'red'))

        new_func_def_history.append({"role": "user", "content": f'Failed Trajectory: \n{new_trajectory}'})
        new_func_def_history.append({"role": "assistant", "content": f'Corrected function: \n{new_func_def}, Explanation: \n{explanation}'})

    return not(found_incorrect_trajectory), new_func_name, new_func_def


def generation_phase(num_iterations, tasks, task_ids, train_failures, mcp_server_before_generation, new_mcp_server, output_folder):
    num_new_funcs = num_iterations
    temp_mcp_server = os.path.normpath('mcp2/retail/retail_server_temp.py')
    open(temp_mcp_server, 'w').close()
    create_file(mcp_server_before_generation, temp_mcp_server, "")
    overall_success = False 
    new_funcs = {}
    for i in range(num_new_funcs):
        print(f"Generation iteration {i+1}")
        success, new_func_name, new_func_def = generate_func(tasks, task_ids, train_failures, temp_mcp_server, new_mcp_server, output_folder)
        if success:
            open(temp_mcp_server, 'w').close()
            create_file(new_mcp_server, temp_mcp_server, new_func_name)
            new_funcs[new_func_name] = new_func_def
            overall_success = True
    return overall_success, new_funcs

def validation_phase(task_ids, mcp_server, new_funcs, output_folder):
    results = []
    for i in range(len(task_ids)):
        output_file = os.path.join(output_folder, f"validation_results_{task_ids[i]}.json")
        run_tasks([task_ids[i]], mcp_server, output_file, agent_strategy='tool-calling')
        trajectory = json.load(open(output_file, 'r'))[0]
        res = Metrics(trajectory, list(new_funcs.keys()))
        results.append(res.to_dict())
    results_file = os.path.join(output_folder, "metric_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    # ######### CONSOLIDATE METRICS ##########
    func_called = {func: False for func in new_funcs}
    error_in_func = {func: False for func in new_funcs}
    num_calls = {func: 0 for func in new_funcs}
    for res in results:
        for func in new_funcs:
            if res['func_called'][func]:
                func_called[func] = True
                num_calls[func] += res['num_calls'][func]
                if res['error_in_func'][func]:
                    error_in_func[func] = True

    res_new_funcs = []
    for func in new_funcs:
        if not error_in_func[func]:
        # if func_called[func] and not error_in_func[func]:
            res_new_funcs.append(func)
    return res_new_funcs

def test_phase(task_ids, mcp_server, new_funcs, output_folder):
    results = []
    for i in range(len(task_ids)):
        output_file = os.path.join(output_folder, f"test_results_{task_ids[i]}.json")
        print("Running test phase")
        run_tasks([task_ids[i]], mcp_server, output_file, agent_strategy='tool-calling')
        trajectory = json.load(open(output_file, 'r'))[0]
        res = Metrics(trajectory, new_funcs)
        results.append(res)
    results_file = os.path.join(output_folder, "test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)


def main2():
    original_logs = "final_results/tool-calling-none-0.1_range_0-100_user-none-llm_06232025.json"
    fault_analysis_logs = "fault_analysis.json"

    train_tasks = json.load(open(original_logs, 'r'))
    failures = json.load(open(fault_analysis_logs, 'r'))['fault_assignment_analysis']

    lib_gen_experiment_output_folder = "libgen_from_error_experiment_output_trial_2"

    generation_phase_iterations = 3
    generation_phase_chunk_size = 1
    test_after_iterations = 10

    # train_ids = range(0, 50)
    validation_ids = range(50, 80)
    test_ids = range(80, 100)

    mcp_server_before_generation = os.path.normpath('mcp2/retail/retail_server_before_generation_iteration_11.py')

    iteration = 10
    index = 0
    while(iteration < 100):

        # for j in range(test_after_iterations):
            
        iteration += 1
        output_folder = os.path.join(lib_gen_experiment_output_folder, f"iteration_{iteration}")
        os.makedirs(output_folder, exist_ok=True)
        print(f"Iteration {iteration}")


        print("Running generation phase")
        mcp_server_after_generation = os.path.normpath(f'mcp2/retail/retail_server_after_generation_iteration_{iteration}.py')
        open(mcp_server_after_generation, 'w').close()
        generation_output_folder = os.path.join(output_folder, "generation")
        os.makedirs(generation_output_folder, exist_ok=True)
        train_failures = failures[iteration*generation_phase_chunk_size : (iteration+1) * generation_phase_chunk_size]
        train_ids_chunk = [task['task_id'] for task in train_failures]
        train_chunk = [train_tasks[id]['traj'] for id in train_ids_chunk]
        # train_chunk = train_tasks[iteration*generation_phase_chunk_size : (iteration+1) * generation_phase_chunk_size]
        # train_ids_chunk = train_ids[iteration*generation_phase_chunk_size : (iteration+1) * generation_phase_chunk_size]
        success, new_funcs = generation_phase(generation_phase_iterations, train_chunk, train_ids_chunk, train_failures, mcp_server_before_generation, mcp_server_after_generation, generation_output_folder)
        if not success:
            continue

        print("Running validation phase")
        validation_output_folder = os.path.join(output_folder, "validation")
        os.makedirs(validation_output_folder, exist_ok=True)
        filtered_funcs = validation_phase(validation_ids, mcp_server_after_generation, new_funcs, validation_output_folder)
        if len(filtered_funcs) == 0:
            continue

        mcp_server_after_validation = os.path.normpath(f'mcp2/retail/retail_server_after_validation_iteration_{iteration}.py')
        open(mcp_server_after_validation, 'w').close()

        mcp_server_temp = os.path.normpath(f'mcp2/retail/retail_server_temp_iteration_{iteration}.py')
        create_file(mcp_server_before_generation, mcp_server_temp, "")
        for func in filtered_funcs:
            create_file(mcp_server_temp, mcp_server_after_validation, new_funcs[func])
            create_file(mcp_server_after_validation, mcp_server_temp, "")
        
        
        mcp_server_before_generation = f'mcp2/retail/retail_server_before_generation_iteration_{iteration+1}.py'
        create_file(mcp_server_after_validation, mcp_server_before_generation, "")

        # if iteration % test_after_iterations == 0:
        #     break
            

        # print("Running test phase")
        # test_output_folder = os.path.join(lib_gen_experiment_output_folder, "test")
        # os.makedirs(test_output_folder, exist_ok=True)
        # test_phase(test_ids, mcp_server_after_validation, filtered_funcs, test_output_folder)





if __name__ == "__main__":
    main2()


