is_verbose = None

def array_as_hex(arr):
    return [hex(i) for i in arr]

def print_v(*args):
    if is_verbose:
        print(*args)
