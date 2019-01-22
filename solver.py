#!/usr/bin/env python3

import os
import sys
import itertools
from z3 import Bool, And, Or, If, sat, Solver, simplify


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
            grid.append([Bool("({},{})".format(x, y)) for y in range(self.height)])
        return grid

    def __generate_possible(self, values, size):
        if (values, size) in self.__possible_lines:
            return self.__possible_lines[(values, size)]

        result = []
        space = size - sum(values) - len(values) + 1

        for perm in permutations(len(values) + 1, space):
            pos = []
            for i, x in enumerate(perm):
                if i != 0:
                    if i > 1:
                        pos.append(False)
                    pos += [True] * values[i-1]
                pos += [False] * x
            result.append(pos)

        self.__possible_lines[(values, size)] = result
        return result

    def __gen_axis_constraints(self, axis):
        for a in range(self.dimensions[axis]):
            valid = False
            for pos in self.__generate_possible(self.rows[a] if axis else self.cols[a], self.dimensions[1-axis]):
                equal = True
                for b in range(self.dimensions[1-axis]):
                    equal = And(equal, (self.grid[b if axis else a][a if axis else b] == pos[b]))
                valid = Or(valid, equal)
            yield simplify(valid)

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


def permutations(buckets, balls):
    if buckets == 1:
        return [[balls]]
    if balls == 0:
        return [[0]*buckets]

    result = []
    for x in range(balls+1):
        for perm in permutations(buckets - 1, balls - x):
            result.append([x] + perm)
    return result


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
    solver.add(constraint)

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
