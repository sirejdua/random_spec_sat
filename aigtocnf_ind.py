#!/usr/bin/env python
import click
import re
from subprocess import check_call

import funcy as fn
from aiger import parser

def get_map(lines):
    def parse_line(line):
        parse = re.match('^c\s(\d+)\s->\s(\d+).*', line)
        if parse is None:
            return None
        return parse.groups()

    return dict(filter(None, map(parse_line, lines)))
        

def get_n_inputs(lines):
    count = 0
    for l in lines:
        if l.startswith('c'):
            break
        if l.startswith('i'):
            count += 1
    return count


@click.command()
@click.argument('aag_path', type=click.Path(exists=True))
@click.argument('cnf_path', type=click.Path(exists=False))
def main(aag_path, cnf_path):
    check_call(f"./../aiger-1.9.9/aigtocnf -m {aag_path} {cnf_path}", shell=True)

    aag = parser.load(str(aag_path))

    # Unused inputs are dropped, so we need to first
    # build a map between aiger inputs and cnf variables.
    with open(cnf_path, 'r') as f:
        var_mapping = get_map(f.readlines())
    
    # Project map onto inputs and take values.
    counting_vars = fn.project(var_mapping, map(str, aag.inputs)).values()

    # Write special comment to indicate the counting variables
    data = [f"c ind {' '.join(counting_vars)} 0\n"]
    with open(cnf_path, 'r') as f:
        data += f.readlines()
    with open(cnf_path, 'w') as f:
        f.writelines(data)

if __name__ == '__main__':
    main()
