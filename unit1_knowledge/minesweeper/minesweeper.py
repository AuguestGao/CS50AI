import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=5, width=5, mines=3):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # Count == # of cells: all are mines
        if self.count == len(self.cells):
            return self.cells
        else: 
            return False

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count == 0: no mines
        if self.count == 0:
            return self.cells
        else:
            return False
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell not in self.cells, do nothing
        if cell not in self.cells:
            pass
        
        # Otherwise
        # Remove cell from sentence's cells, and decrease count by 1
        self.cells.remove(cell)
        self.count -= 1
        
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            pass
        
        self.cells.remove(cell)
        


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1
        self.moves_made.add(cell)

        # 2
        self.mark_safe(cell)

        # 3 
        # Get cell coordinates
        i, j = cell

        # Get all undertermined cells
        steps = [-1, 0, 1]
        undetermined_cells = []
        for stepi in steps:
            if i + stepi not in range(self.height):
                continue
            for stepj in steps:
                if j + stepj not in range(self.width):
                    continue
                if stepi == 0 and stepj == 0:
                    pass
                step = (i + stepi, j + stepj)
                # Step not in mines or safes i.e. undertermined cells: add to cells 
                if step in (self.mines or self.safes):
                    continue
                undetermined_cells.append(step)
        
        # Add sentence into KB
        self.knowledge.append(Sentence(cells = undetermined_cells, count = count))

        # 4
        # Make inference using new added sentence until no new sentence created
        # Init flag which indicates if a new cycle of inference should be made
        flag = True
        while flag:
            # Check flag to False, until a new sentence is created, i.e. loop again
            flag = False

            # Clean up KB by removing known mine cells and safe cells
            self.prune()

            # Remove first sentence from KB
            try:
                first = self.knowledge.pop(0)
            except IndexError:
                continue

            new_knowledge = []
            # Try to infer from frist sentence and the rest sentences
            for current in self.knowledge:
                # new is subset of first
                if current.cells.issubset(first):
                    new_cells = first.cells - current.cells
                    new_count = first.count - current.count
                elif first.cells.issubset(current):
                    new_cells = current.cells - first.cells
                    new_count = current.count - first.count
                else:
                    continue
                # Create new sentence and add into new KB
                new_knowledge.append(Sentence(cells = new_cells, count = new_count))
                # Update flag due to new sentence created
                flag = True
                # Update KB
            self.knowledge += new_knowledge
                

        # 4 Update KB
        # Inite update flag for while loop
        # update = True
        # while update:
        #     # Set update False until there is a inference
        #     update = False

        #     try: 
        #         # get the first sentence from knowledge
        #         first = self.knowledge.pop(0)
        #         print(f"first: {first}")
        #     except IndexError:
        #         break

        #     # Check first sentence has all mines
        #     if first.known_mines():
        #         mine_cells = first.known_mines()
        #         for cell in mine_cells:
        #             self.mark_mine(cell)
        #             update = True
        #             continue

        #     # Check new sentence has no mine
        #     if first.known_safes():
        #         safe_cells = first.known_safes()
        #         for cell in safe_cells:
        #             self.mark_safe(cell)
        #             update = True
        #             continue

        #     # Compare new sentence one by one with sentences from KB
        #     new_knowledge = []
        #     for sentence in self.knowledge:
        #         print(f"sentence: {sentence}")
        #         if first.issubset(sentence):
        #             print("FIRST is sub of sentence")
        #             update = True
        #             new_cells = sentence.cells - first.sells
        #             new_count = sentence.count - first.count
        #             new_knowledge.append(Sentence(cells = new_cells, count = new_count))
        #         elif sentence.issubset(first):
        #             print("sentence is sub of FIRST")
        #             update = True
        #             new_cells = first.cells - sentence.cells
        #             new_count = first.count - sentence.count
        #             new_knowledge.append(Sentence(cells = new_cells, count = new_count))
        #         else:
        #             print("Not a subset")
        #             pass
            
        #     # Update knowledge by adding new knowledge in if not empty
        #     if new_knowledge: 
        #         self.knowledge += new_knowledge

            print(f"mines: {self.mines}")
        #     # print(f"safes: {self.safes}")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Moves are all safes excludng made_moves
        moves = self.safes - self.moves_made

        # Return a random chosen move
        try:
            return random.choice(list(moves))
        except IndexError:
            return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Init cells repersenting the entrie board
        cells = set()
        for i in range(self.height):
            for j in range(self.width):
                cells.add((i, j))

        # Moves are all cells excludes (moves_made && mines)
        moves = cells - self.moves_made - self.mines
        
        # Return a random chosen move
        try:
            return random.choice(list(moves))
        except IndexError:
            return None


    def prune(self):
        """
        Remove known mine or safe cells
        """
        
        restore_knowledge = []

        while len(self.knowledge):
            sentence = self.knowledge.pop(0)

            # Mark safe cells
            if sentence.known_safes():
                safe_cells = sentence.known_safes()
                for cell in safe_cells:
                    self.mark_safe(cell)
            # Make mine cells
            elif sentence.known_mines():
                mine_cells = sentence.known_mines()
                for cell in mine_cells:
                    self.mark_mine(cell)
            else:
                restore_knowledge.append(sentence)

        # Update KB by removing known mine or safe cells, leaving only the uncertain cells
        self.knowledge += restore_knowledge

    def get_subset():
        """
        Generate subsets of KB to compare each pair of sentences
        """
        subset = []
        for i in range(len(self.knowledge)):
            for j in range(1, len(self.knowledge)):
                sebset.append((self.knowledge[i], self.knowledge[j]))
        return subset

    