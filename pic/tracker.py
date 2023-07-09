import os

pvol_path = "/data/gem/"
directories = [] # This is to iterate over all directories
ez_val = [] # Tracking what was the last time we checked 
ncycles = [] # Number of cycles. Each index corresponds to number of cycles of a simulation
max_val = [] # Maximum value among the simulations at every checkpoint step. max_val[0] is at 10, [1] is at 20, etc.
finished = False

# Gets center element from Ez file
def maxSearch(file_path):
    with open(file_path, "r") as file:
        center_row = 63
        center_column = 31
        array_val = []

        for line_number, line in enumerate(file):
            values = line.strip().split()
            array_val.append([float(value) for value in values]
            if line_number == center_row and len(array_values[-1]) > center_column:
                element = array_val[center_row][center_column]
                break
    return abs(element)

def checkDone():
    pass

# Here we check how many folders exists
entries = os.listdir(pvol_path)
for entry in entries:
    entry_path = os.path.join(folder_path, entry)
    if os.path.isdir(entry_path):
        directories.append(entry)

# Here we parse the number of cycles
for file, index in enumerate(directories):
    ez_val.append(10)
    file_path = pvol_path + str(index) + "/" + str(index) + ".inp"
    target_key = "ncycles"
    
    # Find the ncycles for that simulation
    with open(file_path, "r") as file:
        for line in file:
            if target_key in line:
            # Extract the value associated with ncycles
                value = line.split("=")[1].strip()
                ncycles.append(value)
                break
        else:
        # Handle the case when the target key is not found
            value = 0

# Here we start processing
while finished = False:
    for file, index in enumerate(directories):        
        file_path = pvol_path + str(index) + "/Ez_" + str(ez_val[index]) + ".spic"
        # Check if this file exists
        if os.path.exists(file_path):
            ez_val[index] = ez_val + 10
            pic_center_value = maxSearch(file_path)
        else:
            ez = ez_val[index] + 10

    checkDone()
    sleep(5)
