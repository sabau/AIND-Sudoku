assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    """Cross product of elements in a and elements in b."""
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)

# Define row units
row_units = [cross(r, cols) for r in rows]
# Define colums units
column_units = [cross(rows, c) for c in cols]
# Define 3x3 subsquare units
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
# Define diagonal units
diagonal_units = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, cols[::-1])]]
# Merge all the units
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - {s}) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        values(dict): the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist:
        possible_naked = {}
        for u in unit:
            if len(values[u]) == 2:
                # if is a new couple of values, I'll add it to the dictionary
                if values[u] not in possible_naked:
                    possible_naked[values[u]] = u
                # otherwise we have two naked twins
                else:
                    # Eliminate the naked twins as possibilities for their peers in that specific unit
                    for c_unit in unit:
                        if c_unit != u and c_unit != possible_naked[values[u]]:
                            values = assign_value(values, c_unit, values[c_unit].replace(values[u][0], ''))
                            values = assign_value(values, c_unit, values[c_unit].replace(values[u][1], ''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    alldigits = '123456789'
    sudoku = dict(zip(boxes, grid))

    for k in sudoku:
        if sudoku[k] == '.':
            sudoku = assign_value(sudoku, k, alldigits)
    return sudoku


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """
    clean all the unfeasible possibilities for peers of assigned boxes
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): the values dictionary with elimination processed through peers.
    """
    for b in boxes:
        if len(values[b]) == 1:
            for p in peers[b]:
                values = assign_value(values, p, values[p].replace(values[b], ''))
    return values


def only_choice(values):
    """
    if only one box of a unit have available a certain digit, assign this digit to this box
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): the values dictionary after filling in only choices.
    """
    for unit in unitlist:
        for d in '123456789':
            # array of boxes for the digit d
            destinations = [b for b in unit if d in values[b]]
            if len(destinations) == 1:
                values = assign_value(values, destinations[0], d)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Process in chain: eliminate,
        # then only_choice on the eliminate resulting values,
        # then naked_twins on the only_choice resulting values
        values = naked_twins(only_choice(eliminate(values)))

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Using depth-first search and constraint propagation, create a search tree and solve the sudoku.
    Try all possible values in the process.
    Args:
        values(dict): A sudoku in dictionary form.
    Returns:
        The values dictionary containing a solved sudoku or False if sudoku could not be solved
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    # Check if this solution is unsolvable
    if values is False:
        return False

    # Check if we found a solutio, all boxes have one digit
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    min = 10
    minKey = None
    for v in values:
        if 1 < len(values[v]) < min:
            min = len(values[v])
            minKey = v

    for digit in values[minKey]:
        new_values = dict(values)
        assignments_bck = assignments.copy()
        new_values = assign_value(new_values, minKey, digit)
        new_values = search(new_values)
        if new_values != False:
            return new_values
        assignments = assignments_bck.copy()
    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
