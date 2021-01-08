import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

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
        # If number of surrounding cell = number of mines, means all cells are mines
        # Else if number of mines surrounding is 0, means there is no mines
        # Else ...........

        if len(self.cells) == self.count:
            return self.cells
        elif self.count == 0:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Remove itself from the knowledge if it is a mine, 
        # if the cell is not inside the knowledge, does nothing
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If a cell is known to be safe, remove itself from the knowledge
        # Else, if it is not inside knowledge, do nothing
        if cell in self.cells:
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
        # Cleans up the knowledge to ensure that all mines in current knowledge and
        # all safe positions are updated before a new statement is checked
        def check_knowledge():
            update = False
            mines = set()
            safes = set()

            # Record known mines & known safes to be updated
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                    continue
                
                if sentence.known_mines() is not None:
                    for cell in sentence.known_mines():
                        mines.add(cell)
                    update = True
            
                if sentence.known_safes() is not None:
                    for cell in sentence.known_safes():
                        safes.add(cell)
                    update = True
            
            # Update the records. If there is an update, run another
            # check to ensure that no more updates can be found
            if update == True:
                for cell in mines:
                    self.mark_mine(cell)
                for cell in safes:
                    self.mark_safe(cell)
                check_knowledge()

        def check_and_add_sentence(sentence):
            check_knowledge()       # Called since a new statement is about to be checked

            # Check if sentence is already added before
            if sentence in self.knowledge:
                return

            # Check if new sentence is empty, do not do anything
            if len(sentence.cells) == 0:
                return
            
            # Check if sentence knows all are mines
            if sentence.known_mines() is not None:
                for cell in sentence.known_mines():
                    self.mark_mine(cell)
                return
            
            # Check if sentence knows if all are safe
            if sentence.known_safes() is not None:
                for cell in sentence.known_safes():
                    self.mark_safe(cell)
                return

            # Add sentence into knowledge
            self.knowledge.append(sentence)
            
            # Check for subsets
            for info in self.knowledge:
                # Remove knowledge if empty to save on memory
                # Easier to debug if print out knowledge
                if len(info.cells) == 0:
                    self.knowledge.remove(info)
                    continue

                cell_difference = None
                count_difference = None

                # If there is a subset, get the difference
                if info.cells.issubset(sentence.cells):
                    cell_difference = sentence.cells.difference(info.cells)
                    count_difference = sentence.count - info.count
                elif sentence.cells.issubset(info.cells):
                    cell_difference = info.cells.difference(sentence.cells)
                    count_difference = info.count - sentence.count
                
                # If there is a subset, check the new sentence as well.
                if cell_difference is not None and count_difference is not None:
                    new_sentence = Sentence(cell_difference, count_difference)
                    # print(f"new sentence: {new_sentence}")
                    check_and_add_sentence(new_sentence)

        # Mark that the cell as a moved is made.
        # And since the move is made, the cell should be added as safe
        self.moves_made.add(cell)
        self.safes.add(cell)

        # Add all surrounding into a statement
        cell_row, cell_col = cell   # Get row and col for current cell
        new_set = set()
        for row in range(cell_row - 1, cell_row + 2):
            for col in range(cell_col - 1, cell_col + 2):
                
                # Ignore if is ownself
                if (row, col) == cell:
                    continue
                # Skip if out of index
                elif (row < 0 or row >= self.width or col < 0 or col >= self.height):
                    continue
                # Skip if already known is a safe cell
                elif (row, col) in self.safes:
                    continue
                # Skip if already known is a mine
                elif (row, col) in self.mines:
                    count -= 1
                    continue

                new_set.add((row, col))
        new_sentence = Sentence(new_set, count)
        check_and_add_sentence(new_sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # print(f"Safes: {self.safes.difference(self.moves_made)}")
        # print(f"Mines: {self.mines}")
        # my_string = "\n".join(map(str, self.knowledge))
        # print(f"Knowledge = {my_string}")
        for cell in self.safes:
            if cell in self.moves_made:
                continue
            else:
                # print(cell)
                return cell
        # print(f"None {len(self.safes)}, {len(self.moves_made)}")
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            if len(self.moves_made) + len(self.mines) == self.height * self.width:
                return None
            
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            cell = (i, j)

            if cell not in self.moves_made and cell not in self.mines:
                # print(cell)
                return cell
