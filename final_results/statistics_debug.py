import json 
import pandas as pd 
import matplotlib.pyplot as plt


l0 = ['calculate',
'get_user_details',
'get_order_details',
'get_product_details',
'find_user_id_by_email',
'find_user_id_by_name_zip',
'list_all_product_types',
'cancel_pending_order',
'get_input_from_user',
'think',
'transfer_to_human_agents',
'modify_pending_order_items',
'exchange_delivered_order_items',
'return_delivered_order_items',
'modify_pending_order_address',
'modify_pending_order_payment',
'modify_user_address',]

l1 = [
'calculate',
'get_user_details',
'get_order_details',
'get_product_details',
'find_user_id_by_email',
'find_user_id_by_name_zip',
'list_all_product_types',
'cancel_pending_order',
'get_input_from_user',
'think',
'transfer_to_human_agents',
'modify_pending_order_items',
'exchange_delivered_order_items',
'return_delivered_order_items',
'modify_pending_order_address',
'modify_pending_order_payment',
'modify_user_address',
'count_available_product_variants',
'get_return_refund_options',
'get_most_expensive_available_variant',
'get_user_payment_methods',
'get_order_tracking_info',
'get_item_tracking_info',
]

l2 = [
'calculate',
'get_user_details',
'get_order_details',
'get_product_details',
'find_user_id_by_email',
'find_user_id_by_name_zip',
'list_all_product_types',
'cancel_pending_order',
'get_input_from_user',
'think',
'transfer_to_human_agents',
'modify_pending_order_items',
'exchange_delivered_order_items',
'return_delivered_order_items',
'modify_pending_order_address',
'modify_pending_order_payment',
'modify_user_address',
'count_available_product_variants',
'get_return_refund_options',
'get_most_expensive_available_variant',
'get_user_payment_methods',
'get_order_tracking_info',
'get_item_tracking_info',
'get_cheapest_available_variant',
'modify_pending_order_addresses_bulk',
'calculate_order_total_excluding_items',
'calculate_refund_total_for_items',
'get_all_items_in_order',
'get_order_total',
'get_order_refund_total',
'get_order_total_after_modification',
'get_item_details_in_order',
'calculate_order_total_with_item_replacement',
'get_item_price_and_options_in_order',
'check_order_modification_status',
'prepare_pending_order_item_modifications',
'suggest_replacement_variant',
'confirm_and_execute_exchange_delivered_order_items',
'return_all_delivered_order_items',
'get_pending_orders_for_user',
'summarize_user_requested_actions',
]

def get_stats(file):
    print(f"Processing {file}...")
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} tasks from {file}")
        
        tools = {}
        for task in data:
            trajectory = task['traj']
            for step in trajectory:
                if step.get('role') == 'tool':
                    tool_name = step.get('name', 'unknown')
                    if tool_name not in tools:
                        tools[tool_name] = {
                            'calls': 0,
                            'success': 0,
                            'failures': 0,
                            'expected_errors': 0,
                        }
                    tools[tool_name]['calls'] += 1
                    content = step.get('content', '')
                    if "Error: Error" in content:
                        tools[tool_name]['failures'] += 1
                    elif "Error:" in content:
                        tools[tool_name]['expected_errors'] += 1
                    else:
                        tools[tool_name]['success'] += 1
        tools = dict(sorted(tools.items()))
        print(f"Found {len(tools)} unique tools in {file}")
        return tools
    except Exception as e:
        print(f"Error processing {file}: {e}")
        return {}


file1 = "tool-calling-l0-4o.json"
file2 = "tool-calling-l0-4.1.json"
file3 = "tool-calling-l1-4o.json"
file4 = "tool-calling-l1-4.1.json"
file5 = "tool-calling-l2-4o.json"
file6 = "tool-calling-l2-4.1.json"

print("Starting analysis...")

tools1 = get_stats(file1)
tools2 = get_stats(file2)
tools3 = get_stats(file3)
tools4 = get_stats(file4)
tools5 = get_stats(file5)
tools6 = get_stats(file6)

print("Analysis complete. Generating tables...")

def create_comparison_table():
    """Create a comprehensive comparison table for all libraries and models"""
    
    # Get all unique tools across all experiments
    all_tools = set()
    for tools_dict in [tools1, tools2, tools3, tools4, tools5, tools6]:
        all_tools.update(tools_dict.keys())
    all_tools = sorted(list(all_tools))
    
    print(f"Found {len(all_tools)} unique tools across all experiments")
    
    # Create DataFrame
    data = []
    
    for tool in all_tools:
        row = {'Tool': tool}
        
        # L0 data
        l0_4o = tools1.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        l0_41 = tools2.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        
        # L1 data
        l1_4o = tools3.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        l1_41 = tools4.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        
        # L2 data
        l2_4o = tools5.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        l2_41 = tools6.get(tool, {'calls': 0, 'success': 0, 'failures': 0, 'expected_errors': 0})
        
        # Add columns for each experiment
        row.update({
            'L0_GPT4o_Calls': l0_4o['calls'],
            'L0_GPT4o_Success': l0_4o['success'],
            'L0_GPT4o_Failures': l0_4o['failures'],
            'L0_GPT4o_ExpectedErrors': l0_4o['expected_errors'],
            'L0_GPT4o_SuccessRate': f"{l0_4o['success']/l0_4o['calls']*100:.1f}%" if l0_4o['calls'] > 0 else "0%",
            
            'L0_GPT4.1_Calls': l0_41['calls'],
            'L0_GPT4.1_Success': l0_41['success'],
            'L0_GPT4.1_Failures': l0_41['failures'],
            'L0_GPT4.1_ExpectedErrors': l0_41['expected_errors'],
            'L0_GPT4.1_SuccessRate': f"{l0_41['success']/l0_41['calls']*100:.1f}%" if l0_41['calls'] > 0 else "0%",
            
            'L1_GPT4o_Calls': l1_4o['calls'],
            'L1_GPT4o_Success': l1_4o['success'],
            'L1_GPT4o_Failures': l1_4o['failures'],
            'L1_GPT4o_ExpectedErrors': l1_4o['expected_errors'],
            'L1_GPT4o_SuccessRate': f"{l1_4o['success']/l1_4o['calls']*100:.1f}%" if l1_4o['calls'] > 0 else "0%",
            
            'L1_GPT4.1_Calls': l1_41['calls'],
            'L1_GPT4.1_Success': l1_41['success'],
            'L1_GPT4.1_Failures': l1_41['failures'],
            'L1_GPT4.1_ExpectedErrors': l1_41['expected_errors'],
            'L1_GPT4.1_SuccessRate': f"{l1_41['success']/l1_41['calls']*100:.1f}%" if l1_41['calls'] > 0 else "0%",
            
            'L2_GPT4o_Calls': l2_4o['calls'],
            'L2_GPT4o_Success': l2_4o['success'],
            'L2_GPT4o_Failures': l2_4o['failures'],
            'L2_GPT4o_ExpectedErrors': l2_4o['expected_errors'],
            'L2_GPT4o_SuccessRate': f"{l2_4o['success']/l2_4o['calls']*100:.1f}%" if l2_4o['calls'] > 0 else "0%",
            
            'L2_GPT4.1_Calls': l2_41['calls'],
            'L2_GPT4.1_Success': l2_41['success'],
            'L2_GPT4.1_Failures': l2_41['failures'],
            'L2_GPT4.1_ExpectedErrors': l2_41['expected_errors'],
            'L2_GPT4.1_SuccessRate': f"{l2_41['success']/l2_41['calls']*100:.1f}%" if l2_41['calls'] > 0 else "0%",
        })
        
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

def create_summary_table():
    """Create a summary table showing overall statistics per library/model combination"""
    
    experiments = [
        ('L0_GPT4o', tools1),
        ('L0_GPT4.1', tools2),
        ('L1_GPT4o', tools3),
        ('L1_GPT4.1', tools4),
        ('L2_GPT4o', tools5),
        ('L2_GPT4.1', tools6)
    ]
    
    summary_data = []
    
    for exp_name, tools_dict in experiments:
        total_calls = sum(tool['calls'] for tool in tools_dict.values())
        total_success = sum(tool['success'] for tool in tools_dict.values())
        total_failures = sum(tool['failures'] for tool in tools_dict.values())
        total_expected_errors = sum(tool['expected_errors'] for tool in tools_dict.values())
        unique_tools_used = len([tool for tool in tools_dict.values() if tool['calls'] > 0])
        
        summary_data.append({
            'Experiment': exp_name,
            'Total_Calls': total_calls,
            'Total_Success': total_success,
            'Total_Failures': total_failures,
            'Total_Expected_Errors': total_expected_errors,
            'Success_Rate': f"{total_success/total_calls*100:.1f}%" if total_calls > 0 else "0%",
            'Failure_Rate': f"{total_failures/total_calls*100:.1f}%" if total_calls > 0 else "0%",
            'Expected_Error_Rate': f"{total_expected_errors/total_calls*100:.1f}%" if total_calls > 0 else "0%",
            'Unique_Tools_Used': unique_tools_used
        })
    
    return pd.DataFrame(summary_data)

def create_library_comparison_table():
    """Create a table comparing tools available in each library"""
    
    # Create a set of all tools
    all_tools = set()
    all_tools.update(l0)
    all_tools.update(l1)
    all_tools.update(l2)
    all_tools = sorted(list(all_tools))
    
    comparison_data = []
    for tool in all_tools:
        comparison_data.append({
            'Tool': tool,
            'L0': 'Yes' if tool in l0 else 'No',
            'L1': 'Yes' if tool in l1 else 'No',
            'L2': 'Yes' if tool in l2 else 'No'
        })
    
    return pd.DataFrame(comparison_data)

# Generate all tables
print("=== LIBRARY TOOL AVAILABILITY COMPARISON ===")
library_comparison = create_library_comparison_table()
print(library_comparison.to_string(index=False))

print("\n\n=== EXPERIMENT SUMMARY STATISTICS ===")
summary_table = create_summary_table()
print(summary_table.to_string(index=False))

print("\n\n=== DETAILED TOOL USAGE COMPARISON ===")
detailed_comparison = create_comparison_table()
print(detailed_comparison.to_string(index=False))

# Save tables to CSV files
library_comparison.to_csv('library_tool_comparison.csv', index=False)
summary_table.to_csv('experiment_summary.csv', index=False)
detailed_comparison.to_csv('detailed_tool_usage.csv', index=False)

print("\n\nTables saved to CSV files:")
print("- library_tool_comparison.csv")
print("- experiment_summary.csv") 
print("- detailed_tool_usage.csv")
