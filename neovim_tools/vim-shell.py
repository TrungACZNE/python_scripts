#!/usr/bin/env python3
"""
Helpers for the neovim python client
Run this file to start an interactive python shell that can interact with
a running neovim process through the $NVIM_LISTEN_ADDRESS socket
See reattach() for the exposed variables
"""
import code
import json
import os
import yaml
from neovim import attach


identity = lambda x: x


def throw(*args, **kwargs):
    raise "Inappropriate action"


FORMAT = {
    "text": {
        "encoder": identity,
        "decoder": identity
    },
    "json": {
        "encoder": lambda text: json.dumps(text, sort_keys=True, indent=4),
        "decoder": json.loads
    },
    "yaml": {
        "encoder": yaml.dump,
        "decoder": yaml.load,
    },
    "eval": {
        "encoder": eval,
        "decoder": throw,
    },
    "exec": {
        "encoder": lambda blob: exec(blob, globals()),
        "decoder": throw,
    }
}


def encode(data, encoder):
    if type(encoder) == str:
        if encoder in FORMAT:
            return FORMAT[encoder]["encoder"](data)
        else:
            raise "Unknown encoder " + encoder
    else:
        # custom encoder function
        return encoder(data)


def decode(data, decoder):
    if type(decoder) == str:
        if decoder in FORMAT:
            return FORMAT[decoder]["decoder"](data)
        else:
            raise "Unknown decoder " + decoder
    else:
        # custom decoder function
        return decoder(data)


def reattach():
    """
    Attach to a running neovim process
    Exposes some global variables for ease of use
    Call again if detached (neovim process restarts)
    """
    nvim = attach('socket', path=os.environ.get("NVIM_LISTEN_ADDRESS", '/tmp/nvimsocket'))
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


def selected(decoder="text"):
    """
    Return the selected text, decoded using decoder
    """
    start_line, start_col, end_line, end_col = get_selected_pos_as_indices()

    if start_line == end_line:
        blob = current.buffer[start_line][start_col:end_col + 1]
    else:
        blob = "\n".join(
            [current.buffer[start_line][start_col:]]
            + [current.buffer[i] for i in range(start_line + 1, end_line)]
            + [current.buffer[end_line][:end_col + 1]]
        )

    return decode(blob, decoder)


def transform(data, encoder="text"):
    """
    Transform selected text into blob (multiple line string or array of lines)
    """
    blob = encode(data, encoder)
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
            current.buffer[start_line + i + 1] = lines[i + 1]
        current.buffer[end_line] = lines[-1] + suffix


def transform_lines(fun):
    """
    Transform selected text, line by line, using fun
    """
    transform(list(map(fun, selected().splitlines())))


reattach()
code.interact(local=globals())
