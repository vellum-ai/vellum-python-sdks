import json
import os
import sys
import traceback

from python_file_merging.nodes import merge_python_files

STOP_SIGNAL = "--vellum-input-stop--"

input_raw = ""
while STOP_SIGNAL not in input_raw:
    # os/read they come in chunks of idk length, not as lines
    input_raw += os.read(0, 100_000_000).decode("utf-8")

split_input = input_raw.split(f"\n{STOP_SIGNAL}\n")
input_json = split_input[0]
input_data = json.loads(input_json)

try:
    result = merge_python_files(input_data["originalFileMap"], input_data["generatedFileMap"])
    print(json.dumps(result))  # noqa T201

    # manually flushing here just incase since -u slower
    sys.stdout.flush()
except Exception:
    # need to catch exception and print even with -u or it doesn't get flushed
    traceback.print_exc()
    sys.stderr.flush()
    exit(1)
