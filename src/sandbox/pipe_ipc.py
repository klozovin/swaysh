
import sys

named_pipe: str = sys.argv[1]

# TODO: Use selectors for this instead of reopening the file?
while True:
    with open(named_pipe) as named_pipe_file:
        line = named_pipe_file.readline()
        if line:
            print(f"From pipe: {line}")
        else:
            continue
