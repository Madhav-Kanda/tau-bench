import json
import os
import subprocess
from glob import glob

from termcolor import colored

import lib_gen as lib_gen
from libgen_utils import *

def run_tasks(task_ids, mcp_server, output_file, agent_strategy='tool-calling', new_func_name=None):
    open(output_file, 'w').close()
    agent_model = os.environ.get("LIBGEN_AGENT_MODEL", os.environ.get("OPENAI_MODEL", "none"))
    user_model = os.environ.get("LIBGEN_USER_MODEL", agent_model)
    command = [
        "python", "run.py",
        "--agent-strategy", agent_strategy,
        "--env", "retail",
        "--model", agent_model,
        "--model-provider", "openai",
        "--user-model", user_model,
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


def generate_func(tasks, task_ids, mcp_server_before_generation, new_mcp_server, output_folder):
    tools = get_tools(mcp_server_before_generation)
    old_library = Library(tools).get_funcs()
    ######### GET NEW FUNC CANDIDATES #######
    def_flag = False
    doc_trial = 0
    while not def_flag and doc_trial < 2:
        doc_trial += 1
        new_func_name, new_func_def = lib_gen.get_new_func(tasks, old_library)
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


def generation_phase(num_iterations, tasks, task_ids, mcp_server_before_generation, new_mcp_server, output_folder):
    num_new_funcs = num_iterations
    temp_mcp_server = os.path.normpath('mcp/retail_server_temp.py')
    open(temp_mcp_server, 'w').close()
    create_file(mcp_server_before_generation, temp_mcp_server, "")
    overall_success = False 
    new_funcs = {}
    for i in range(num_new_funcs):
        print(f"Generation iteration {i+1}")
        success, new_func_name, new_func_def = generate_func(tasks, task_ids, temp_mcp_server, new_mcp_server, output_folder)
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
        if func_called[func] and not error_in_func[func]:
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
    original_logs = os.environ.get("LIBGEN_ORIGINAL_LOGS")
    if original_logs is None or not os.path.exists(original_logs):
        candidates = sorted(glob("results/*.json"), key=os.path.getmtime, reverse=True)
        if len(candidates) > 0:
            original_logs = candidates[0]
        else:
            raise FileNotFoundError("Set LIBGEN_ORIGINAL_LOGS to a prior tau-bench results JSON, or place one under results/.")
    lib_gen_experiment_output_folder = "libgen_experiment_output_trial_7"
    # original_mcp_server = os.path.normpath('mcp/retail_server.py')
    # mcp_server_before_generation = os.path.normpath('mcp/retail_server_initial.py')
    # open(mcp_server_before_generation, 'w').close()
    # create_file(original_mcp_server, mcp_server_before_generation, '')

    generation_phase_iterations = 3
    generation_phase_chunk_size = 5
    test_after_iterations = 6

    train_ids = range(0, 50)
    validation_ids = range(50, 80)
    test_ids = range(80, 100)
    train_tasks = json.load(open(original_logs, 'r'))

    mcp_server_before_generation = os.path.normpath('mcp/retail_server_before_generation_iteration_6.py')

    iteration = 5
    while(iteration < 10):

        for j in range(test_after_iterations):
            iteration += 1
            output_folder = os.path.join(lib_gen_experiment_output_folder, f"iteration_{iteration}")
            os.makedirs(output_folder, exist_ok=True)
            print(f"Iteration {iteration}")


            print("Running generation phase")
            mcp_server_after_generation = os.path.normpath(f'mcp/retail_server_after_generation_iteration_{iteration}.py')
            open(mcp_server_after_generation, 'w').close()
            generation_output_folder = os.path.join(output_folder, "generation")
            os.makedirs(generation_output_folder, exist_ok=True)
            train_chunk = train_tasks[iteration*generation_phase_chunk_size : (iteration+1) * generation_phase_chunk_size]
            train_ids_chunk = train_ids[iteration*generation_phase_chunk_size : (iteration+1) * generation_phase_chunk_size]
            success, new_funcs = generation_phase(generation_phase_iterations, train_chunk, train_ids_chunk, mcp_server_before_generation, mcp_server_after_generation, generation_output_folder)
            if not success:
                continue

            print("Running validation phase")
            validation_output_folder = os.path.join(output_folder, "validation")
            os.makedirs(validation_output_folder, exist_ok=True)
            filtered_funcs = validation_phase(validation_ids, mcp_server_after_generation, new_funcs, validation_output_folder)
            if len(filtered_funcs) == 0:
                continue

            mcp_server_after_validation = os.path.normpath(f'mcp/retail_server_after_validation_iteration_{iteration}.py')
            open(mcp_server_after_validation, 'w').close()

            mcp_server_temp = os.path.normpath(f'mcp/retail_server_temp_iteration_{iteration}.py')
            create_file(mcp_server_before_generation, mcp_server_temp, "")
            for func in filtered_funcs:
                create_file(mcp_server_temp, mcp_server_after_validation, new_funcs[func])
                create_file(mcp_server_after_validation, mcp_server_temp, "")
            
            
            mcp_server_before_generation = f'mcp/retail_server_before_generation_iteration_{iteration+1}.py'
            create_file(mcp_server_after_validation, mcp_server_before_generation, "")

            if iteration % test_after_iterations == 0:
                break
            

        print("Running test phase")
        test_output_folder = os.path.join(lib_gen_experiment_output_folder, "test")
        os.makedirs(test_output_folder, exist_ok=True)
        test_phase(test_ids, mcp_server_after_validation, filtered_funcs, test_output_folder)

def main():
    original_logs = "final_results/tool-calling-none-0.1_range_0-100_user-none-llm_06232025.json"
    improved_logs_folder = "improved_logs"
    original_mcp_server = os.path.normpath('mcp/retail_server.py')
    old_mcp_server = os.path.normpath('mcp/retail_server_test.py')
    new_mcp_server = os.path.normpath('mcp/retail_server_test2.py')
    train_ids = range(0, 50)
    validation_ids = range(50, 80)
    test_ids = range(80, 100)
    train_tasks = json.load(open(original_logs, 'r'))

    open(old_mcp_server, 'w').close()
    create_file(original_mcp_server, old_mcp_server, '')

    train_generation_phase_chunk_size = 5
    i = -train_generation_phase_chunk_size
    iteration = 0
    while(True):
        iteration += 1
        print(iteration)
        i+=train_generation_phase_chunk_size
        
        ######### TASKS AND TOOLS #######
        tools = get_tools(old_mcp_server)
        old_library = Library(tools).get_funcs()
        tasks = train_tasks[i:i+train_generation_phase_chunk_size]
        task_ids = train_ids[i:i+train_generation_phase_chunk_size]


        ######### GET NEW FUNC CANDIDATES #######
        def_flag = False
        doc_trial = 0
        while not def_flag and doc_trial < 2:
            doc_trial += 1
            new_func_name, new_func_def = lib_gen.get_new_func(tasks, old_library)
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
        break_flag = False
        while(break_flag or trial < 5):
            trial += 1
            ########## IMPROVE TRAJECTORIES ##########
            new_library = old_library + [new_func_def]
            open(new_mcp_server, 'w').close()
            create_file(old_mcp_server, new_mcp_server, new_func_def)

            

            traj_results = []
            index = -1
            for j in range(train_generation_phase_chunk_size):
                print(colored(task_ids[j], 'green'))
                output_file = run_train_chunk([task_ids[j]], new_mcp_server, new_func_name)
                trajectory = json.load(open(output_file, 'r'))[0]
                res = Metrics(trajectory, [new_func_name])
                traj_results.append(res.error_in_func[new_func_name])
                
                print(colored(f'Trajectory check results: {traj_results[j]}', 'cyan'))
                if traj_results[j] == True:
                    break_flag = False
                    index = j
                    break     
            if index==-1:
                break_flag = True
            if break_flag:
                break      
            
            print("wrong trajectory", task_ids[index])
            new_trajectory = trajectory
            improved_func_def, explanation = lib_gen.correct_func_from_traj(old_library, new_func_def, new_trajectory, new_func_def_history)
            new_func_def = improved_func_def

            print(colored(f'Corrected proposed function: {new_func_def}', 'green'))
            print(colored(f'Explanation: {explanation}', 'red'))

            new_func_def_history.append({"role": "user", "content": f'Failed Trajectory: \n{new_trajectory}'})
            new_func_def_history.append({"role": "assistant", "content": f'Corrected function: \n{new_func_def}, Explanation: \n{explanation}'})

        ########## UPDATE LIBRARY ##########
        if break_flag:
            create_file(new_mcp_server, old_mcp_server, "")
            run_test(test_ids, new_mcp_server)


if __name__ == "__main__":
    main2()