import exceptions

class board:
    # edge color embedding formula
    def trans(self, color):
        return sorted(color)

    def transinv(self, embedding):
        return sorted(embedding)

    def inboard(self, *value):
        allinside = True

        for i in value:
            allinside *= (0 <= i <= self.size - 1)

        return allinside

    def edge(self, x1, y1, x2, y2):
        return tuple(sorted(((x1, y1), (x2, y2))))

    def edgenbhd(self, x, y):
        nbhd = set()

        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self.inboard(x + i, y + j):
                    nbhd |= {self.edge(x, y, x + i, y + j)}

        return nbhd - {self.edge(x, y, x, y)}

    def __init__(self, size):
        # quick initialization
        self.size = size
        self.turn = 1  # the person who is making the move on this turn
        self.winner = 0
        self.boardvis = [[0 for i in range(size)] for j in range(size)]

        self.boardconn = {}
        self.boardlen = {}

        # making the set of edges
        self.edgeset = set()

        for i in range(size):
            for j in range(size):
                self.edgeset |= self.edgenbhd(i, j)

        # making the connection embedding of the board
        for i in self.edgeset:
            self.boardconn[i] = self.trans([0, 0])
            self.boardlen[i] = 0

    def directedneighbors(self, edge):
        xdiff = edge[0][0] - edge[1][0]
        ydiff = edge[0][1] - edge[1][1]

        new1x, new1y = edge[0][0] + xdiff, edge[0][1] + ydiff
        new2x, new2y = edge[1][0] - xdiff, edge[1][1] - ydiff

        neighbors = set()

        if self.inboard(new1x, new1y):
            neighbors |= {self.edge(edge[0][0], edge[0][1], new1x, new1y)}

        if self.inboard(new1x, new1y):
            neighbors |= {self.edge(edge[1][0], edge[1][1], new2x, new2y)}

        return neighbors

    def edgelenupdate(self, edge):
        def edgerecursion(oldedge, currentedge, weight, depth):
            self.boardlen[currentedge] = weight

            nextedge = self.directedneighbors(currentedge) - {oldedge}
            nextedge = list(nextedge)[0]

            if depth > 0:
                edgerecursion(currentedge, nextedge, weight, depth - 1)

        x1, y1, x2, y2 = edge[0][0], edge[0][1], edge[1][0], edge[1][1]
        color1, color2 = self.boardvis[y1][x1], self.boardvis[y2][x2]

        neighbors = self.directedneighbors(edge)
        weightsum = 0
        newweight = 0

        for i in neighbors:
            weightsum += self.boardlen[i]

        if (color1 == color2):
            newweight = (weightsum + color1)
            for i in neighbors:
                edgerecursion(list(neighbors - {i})[0], edge, newweight, self.boardlen[i])

        return newweight

    def makemove(self, x, y):
        try:
            oldvalue = self.boardvis[y][x]

            if oldvalue == 0 and self.winner == 0:
                self.boardvis[y][x] = self.turn
                maxlen = 0

                for i in self.edgenbhd(x, y):
                    #replacing old edge value with new one
                    oldcolor = self.transinv(self.boardconn[i])
                    oldcolor.remove(oldvalue)
                    newcolor = [oldcolor[0], self.turn]
                    self.boardconn[i] = self.trans(newcolor)

                    #changing edge lengths
                    maxlen = max(maxlen, abs(self.edgelenupdate(i)))

                if maxlen >= 4:
                    self.winner = self.turn

                self.turn *= -1

            elif oldvalue != 0:
                raise exceptions.PositionAlreadyFilled

            elif self.winner != 0:
                raise exceptions.AlreadyWon

        except exceptions.PositionAlreadyFilled:
            print(f'Exception Occurred: attempted to fill a position that was already filled (position {x},{y})')

        except exceptions.AlreadyWon:
            print(f'This board has already been won by player {self.winner}, but player {self.turn} has attempted to make a move')

    def printboard(self):
        sign = {0: 'o', -1: '-', 1: '+'}

        for i in self.boardvis:
            print()
            for j in i:
                print(sign[j], end = ' ')