from libgen_utils import * 

new_funcs = {'a' : 'A', 'b' : 'B', 'c' : 'C'}
filtered_funcs = {'a', 'b'}

file1 = 'mcp/retail_server.py'
file2 = 'temp1.py'
file3 = 'temp2.py'


create_file(file1, file2, "")
for func in filtered_funcs:
    create_file(file2, file3, new_funcs[func])
    create_file(file3, file2, "")