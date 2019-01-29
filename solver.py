#!/usr/bin/env python3

import os
import sys

UNKNOWN, FREE, FILLED = range(3)


class Nonogramm:
    def __init__(self, width, height, rows, cols):
        self.width = width
        self.height = height
        self.rows = tuple(tuple(x) for x in rows)
        self.cols = tuple(tuple(x) for x in cols)
        self.grid = [[UNKNOWN]*height for _ in range(width)]

        self.dimensions = (width, height)

    def __get(self, axis, line_index, cell_index):
        if axis == 0:
            return self.grid[line_index][cell_index]
        return self.grid[cell_index][line_index]

    def __set(self, axis, line_index, cell_index, value):
        if axis == 0:
            self.grid[line_index][cell_index] = value
        else:
            self.grid[cell_index][line_index] = value

    def __prefill(self, axis, line_index):
        hints = (self.cols if axis == 0 else self.rows)[line_index]
        space = self.dimensions[1 - axis] - sum(hints) - len(hints) + 1
        if space < max(hints):
            total = 0
            for hint in hints:
                if hint > space:
                    for i in range(total+space, total+hint):
                        self.__set(axis, line_index, i, FILLED)
                total += hint + 1

    def solve(self):
        for x in range(self.width):
            self.__prefill(0, x)

        for y in range(self.height):
            self.__prefill(1, y)

    def print_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                print((".", "X", "#")[self.grid[x][y]], end="")
            print()

    @staticmethod
    def from_file(filename):
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


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "help"):
        print("Usage:", sys.argv[0], "NONOGRAMM-FILE")
        exit(1)
    elif not os.path.isfile(sys.argv[1]):
        print("'{}' is not a valid file".format(sys.argv[1]))
        exit(1)

    nonogramm = Nonogramm.from_file(sys.argv[1])

    if nonogramm is None:
        print("'{}' doesn't contain a valid nonogramm".format(sys.argv[1]))
        exit(2)

    print("Solving...")
    nonogramm.solve()
    nonogramm.print_grid()


if __name__ == "__main__":
    main()
