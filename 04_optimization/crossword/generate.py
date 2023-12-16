import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains.keys():
            for word in self.domains[v].copy():
                if v.length != len(word):
                    self.domains[v].remove(word)



    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False

        overlap = self.crossword.overlaps[x,y]
        if overlap is None:
            return revision
        
        for xvalue in self.domains[x].copy():
            posible_overlaps = [ word[overlap[1]] for word in self.domains[y]]

            if xvalue[overlap[0]] not in posible_overlaps:
                self.domains[x].remove(xvalue)
                revision = True

        return revision


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

            while len(arcs) > 0:
                arc = arcs.pop()
                if self.revise(arc[0], arc[1]):
                    if len(self.domains[arc[0]]) == 0:
                        return False
                    
                    new_arcs = self.crossword.neighbors(arc[0])
                    new_arcs.remove(arc[1])

                    for nei in new_arcs:
                        arcs.append((nei,arc[0]))
            
            return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        Output = True

        unassigned = [x for x in self.domains.keys() if x not in assignment.keys()]
        if len(unassigned) > 0:
            Output = False
        
        return Output


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Length of words is checked in node consistency
        for v1 in assignment.keys():
            for v2 in assignment.keys():
                if v1 != v2:
                    # check for different words
                    if assignment[v1] == assignment[v2]:
                        return False
                    
                    # check for conflicts
                    arc = self.crossword.overlaps[v1,v2]

                    if arc is not None:
                        if assignment[v1][arc[0]] != assignment[v2][arc[1]]:
                            return False
        

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        possibilities = [x for x in self.domains[var] if x not in assignment.keys()]
        ordered = []
        nei = self.crossword.neighbors(var)

        while len(possibilities) > 0:
            ruledout = 10000
            selected = None
            for possibility in possibilities:
                count = 0
                for neibghor in nei:
                    over = self.crossword.overlaps[var,neibghor]
                    for yword in self.domains[neibghor]:
                        if possibility[over[0]] != yword[over[1]]:
                            count += 1

                if count < ruledout:
                    ruledout = count
                    selected = possibility
            
            ordered.append(selected)
            possibilities.remove(selected)

        
        return(ordered)




    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        choices = []
        value = 10000000

        for v in self.domains.keys():
            if v not in assignment.keys():
                if len(self.domains[v]) < value:
                    value = len(self.domains[v])
                    choices = [v]
                elif len(self.domains[v]) == value:
                    choices.append(v)
        
        if len(choices) == 1:
            return choices[0]
        
        degree = 0
        for var in choices.copy():
            if len(self.crossword.neighbors(var)) > degree:
                choices = [var]
            elif len(self.crossword.neighbors(var)) == degree:
                choices.append(var)
        
        return choices[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):

            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)

                if result is not None:
                    return result
                else:
                    assignment[var] = None
            else:
                assignment[var] = None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
