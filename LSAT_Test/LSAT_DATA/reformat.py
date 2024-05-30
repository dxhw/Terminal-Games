import json
from collections import defaultdict

# Sample input JSON data (you can replace this with reading from a file)
QUESTION_PATH = "/Users/dorenhsiao-wecksler/Documents/LSAT_DATA/"
RC_TEST = QUESTION_PATH + "test_rc.json"
RC_TRAIN = QUESTION_PATH + "train_rc.json"
RC_VAL = QUESTION_PATH + "val_rc.json"

def combine_json_files(file_paths):
    combined_data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data = json.load(f)
            combined_data.extend(data)
    return combined_data
    
input_json = combine_json_files([RC_TEST, RC_TRAIN, RC_VAL])

# Step 1: Create a dictionary to hold grouped data
grouped_data = defaultdict(list)
context_dict = defaultdict()

# Step 2: Process each entry to extract the context ID and group the entries
for entry in input_json:
    # Split the id_string and remove the last part
    parts = entry["id_string"].rsplit('_', 1)
    context_id = parts[0]
    
    # Create a question entry
    question_entry = {
        "question": entry["question"],
        "answers": entry["answers"],
        "label": entry["label"],
        "id_string": entry["id_string"]
    }
    
    # Append the question entry to the corresponding context_id group
    grouped_data[context_id].append(question_entry)
    if context_id not in context_dict:
        context_dict[context_id] = entry["context"]


# Step 3: Reorganize the data into the desired format
output_json = [
    {
        "context_id": context_id,
        "context": context_dict[context_id],
        "questions": questions
    }
    for context_id, questions in grouped_data.items()
]

# Step 4: Output the JSON data (you can also write this to a file)
# output_json_str = json.dumps(output_json, indent=4)
# print(output_json_str)

# To write the output to a file, use:
with open('/Users/dorenhsiao-wecksler/Documents/LSAT_DATA/all_rc.json', 'w') as f:
    json.dump(output_json, f, indent=4)
