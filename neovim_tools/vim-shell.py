#!/usr/bin/env python3
import code
import json
import yaml
from neovim import attach


def reattach():
    nvim = attach('socket', path='/tmp/nvimsocket')
    environment=globals()
    environment["nvim"] = nvim
    environment["buffers"] = nvim.buffers
    environment["current"] = nvim.current


def get_selected_pos():
    _, start_line, start_col, _ = nvim.eval('getpos("\'<")')
    _, end_line, end_col, _ = nvim.eval('getpos("\'>")')

    return start_line, start_col, end_line, end_col


def get_selected_pos_as_indices():
    start_line, start_col, end_line, end_col = get_selected_pos()

    return start_line - 1, start_col - 1, end_line - 1, end_col - 1


def get_selected(decoder="text"):
    start_line, start_col, end_line, end_col = get_selected_pos_as_indices()

    if start_line == end_line:
        blob = current.buffer[start_line][start_col:end_col + 1]
    else:
        blob = "\n".join(
            [current.buffer[start_line][start_col:]]
            + [current.buffer[i] for i in range(start_line + 1, end_line)]
            + [current.buffer[end_line][:end_col + 1]]
        )

    if decoder == "json":
        return json.loads(blob)
    elif decoder == "yaml":
        return yaml.load(blob)
    elif decoder == "text":
        return blob
    elif decoder == "eval":
        return eval(blob)
    elif decoder == "exec":
        return exec(blob, globals())
    else:
        raise "Unknown decoder"


def replace_selected(blob):
    if type(blob) is list:
        lines = blob
    else:
        lines = blob.splitlines()

    if len(lines) == 0:
        return

    start_line, start_col, end_line, end_col = get_selected_pos_as_indices()
    num_unedited_lines = end_line - start_line + 1
    diff = len(lines) - num_unedited_lines

    prefix = current.buffer[start_line][:start_col]
    suffix = current.buffer[end_line][end_col + 1:]

    if diff > 0:
        current.buffer.append([""] * diff, end_line)
    elif diff < 0:
        for i in range(-diff):
            current.buffer[start_line + 1] = None

    end_line += diff

    if start_line == end_line:
        current.buffer[start_line] = prefix + lines[0] + suffix
    else:
        current.buffer[start_line] = prefix + lines[0]
        for i, line in enumerate(lines[1:-1]):
            current.buffer[start_line + i] = lines[i]
        current.buffer[end_line] = lines[-1] + suffix


reattach()
code.interact(local=globals())
