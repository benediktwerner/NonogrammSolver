#!/usr/bin/env python3

import os
import sys
import itertools
from z3 import Int, Bool, And, Or, Not, If, Implies, sat, Solver, simplify


class Nonogramm:
    def __init__(self, width, height, rows, cols):
        self.width = width
        self.height = height
        self.rows = tuple(tuple(x) for x in rows)
        self.cols = tuple(tuple(x) for x in cols)
        self.grid = self.__gen_grid()

        self.dimensions = (width, height)
        self.__possible_lines = {}

    def __gen_grid(self):
        grid = []
        for x in range(self.width):
            grid.append([Bool("{}_{}".format(x, y)) for y in range(self.height)])
        return grid

    def __grid(self, axis, line, cell):
        return self.grid[line if axis == 0 else cell][line if axis == 1 else cell]

    def __generate_line_constraints(self, axis, line_index):
        variables = []
        line = (self.cols if axis == 0 else self.rows)[line_index]
        breakpoints = [line[0]]

        for x in line[1:]:
            breakpoints.append(breakpoints[-1] + 1 + x)

        for i in range(self.dimensions[1 - axis]):
            variables.append(Int("{}_{}_{}".format(axis, line_index, i)))
            curr_cell = self.__grid(axis, line_index, i)

            if i == 0:
                yield variables[i] == If(curr_cell, 1, 0)
            else:
                prev_cell = self.__grid(axis, line_index, i-1)
                yield variables[i] == variables[i-1] + If(Or(curr_cell, prev_cell), 1, 0)
                yield And(prev_cell, Not(curr_cell)) == Or(*(variables[i-1] == b for b in breakpoints))

        yield variables[-1] == breakpoints[-1] + If(curr_cell, 0, 1)

    def __gen_axis_constraints(self, axis):
        for i in range(self.dimensions[axis]):
            yield from self.__generate_line_constraints(axis, i)

    def gen_constraints(self):
        return itertools.chain(self.__gen_axis_constraints(0), self.__gen_axis_constraints(1))


def load_file(filename):
    index = -1
    rows = []
    cols = []

    with open(filename) as f:
        try:
            for line in f:
                line = line.strip()

                if not line or line[0] == "#":
                    continue

                if index < 0:
                    width, height = map(int, line.split(" "))
                elif index < height:
                    rows.append([int(x) for x in line.split(" ")])
                elif index < height + width:
                    cols.append([int(x) for x in line.split(" ")])
                else:
                    break

                index += 1
        except ValueError:
            return None

    if len(rows) != height or len(cols) != width:
        return None
    return Nonogramm(width, height, rows, cols)


if len(sys.argv) != 2 or sys.argv[1] in ("-h", "help"):
    print("Usage:", sys.argv[0], "NONOGRAMM-FILE")
    exit(1)
elif not os.path.isfile(sys.argv[1]):
    print("'{}' is not a valid file".format(sys.argv[1]))
    exit(1)

nonogramm = load_file(sys.argv[1])

if not nonogramm:
    print("'{}' doesn't contain a valid nonogramm".format(sys.argv[1]))
    exit(2)

solver = Solver()

print("Generating constraints ...")

for constraint in nonogramm.gen_constraints():
    solver.add(simplify(constraint))

print("Solving...")

if solver.check() == sat:
    print("Solved:")
    model = solver.model()

    for y in range(nonogramm.height):
        for x in range(nonogramm.width):
            print("#" if model[nonogramm.grid[x][y]] else ".", end="")
        print()
else:
    print("Unsolvable!")
