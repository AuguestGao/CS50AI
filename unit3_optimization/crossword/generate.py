import sys
import itertools

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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        # init a new domains
        new_domains = {}

        # loop over domains
        for var, words in self.domains.items():
            # init value set
            values = set()

            # only add word length == variable length into values
            for word in words:
                if len(word) == var.length:
                    values.add(word)

            # update new_domains
            new_domains[var] = values
        # copy new domains over 
        self.domains = new_domains.copy()
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # init revised to False
        revised = False

        # init empty set as new x domain
        remove_words = set()

        # loop over words in x domain
        for wordx in self.domains[x]:
            
            # get all wordx, wordy overlap result, true = at least 1 overlap
            results = []
            for wordy in self.domains[y]:
                # has overlap
                result = self.crossword.overlaps[wordx, wordy]
                if result == None:
                    results.append(False)
                else:
                    results.append(True)

            # no overlap: add word for removal, update revised
            if not any(results):
                remove_words.add(wordx)
                revised = True
        
        # there are words to be removed
        if not remove_words:
            for word in remove_words:
                self.domains[x].remove(word)
        
        return revised

        

                


        self.domains[x] = x_values

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if arcs is None: use permutations of 2 variables from all possible
        if arcs == None:
            arcs = list(itertools.permutations(self.crossword.variables, 2))

        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                # revised, if x domain is empty, i.e. no solution for x
                if not len(self.domains[x]):
                    return False
                
                varz = self.crossword.neighbors(x) - y
                for var in varz:
                    arcs.append((var, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # if one of assignmengt value is empty, assignmment is then not completed
        return all([len(string) for string in assignment.values()])


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        distinctions = set()
        for x, string in assignment.items():

            # check the length of the word
            if x.length != len(string):
                return False

            # check dictiction
            if string in distinctions:
                return False
            distinctions.add(string)

            # check conflicts
            varz = self.crossword.neighbors(x)
            for v in varz:
                if v in assignment:
                    (i, j) = self.crossword.overlaps(x, v)
                    try:
                        string[i] != assignment[v][j]
                        return False
                    except IndexError:
                        pass
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # unordered
        unordered_domain_values = []

        # get number of eliminations
        for x in self.domains[var]:
            # init number of ruled out count
            num_out= 0
            # if x is assigned to already: pass
            if x in assignment:
                pass
            
            for neighbor in self.crossword.neighbors(var):
                # number of rule out counter + 1 if the choosen x is also be one of the neighbor's domain
                if x in self.domains[neighbor]:
                    num_out += 1
            # append dictionary
            unordered_domain_values.append((num_out, x))
            
        # sort in ascending order
        ordered_domain_values = sorted(unordered_domain_values, key = lambda i : i[0])
        return [i[1] for i in ordered_domain_values]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # get all unassigned variables
        unassigned_variables = self.crossword.variables - set(assignment.keys())

        # get remaining domain size for unassigned_variables, and put them into a list
        unassigned = []
        for var in unassigned_variables:
            unassigned.append((len(self.domains[var]), var))
        
        # sort unordered_unassigned variables in ascending order
        unassigned.sort(key=lambda i: i[0])
        
        # return the variable with minimum remaining value, i.e. the first in the list
        return unassigned[0][1]
            

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # successfully created a crossword 
        if self.assignment_complete(assignment):
            return assignment
        
        # take an unassigned variable
        unassigned = self.select_unassigned_variable(assignment)

        # backtracking
        for value in self.order_domain_values(unassigned, assignment):
            # add unassignment-value in assignment
            assignment[unassigned] = value
            # check assignment is still consistent
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            del assignment[unassigned]
        return False


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
