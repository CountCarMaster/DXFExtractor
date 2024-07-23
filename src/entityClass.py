import numpy as np

def line_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3

    denominator = dx1 * dy2 - dy1 * dx2

    if denominator == 0:
        return None  # 不相交

    dx3, dy3 = x3 - x1, y3 - y1
    t1 = (dx3 * dy2 - dy3 * dx2) / denominator
    t2 = (dx3 * dy1 - dy3 * dx1) / denominator

    if 0 <= t1 <= 1 and 0 <= t2 <= 1:
        intersection_x = x1 + t1 * dx1
        intersection_y = y1 + t1 * dy1
        return (intersection_x, intersection_y)
    else:
        return None

class EntityClassBase:
    def __init__(self, data: np.array):
        self.data = data
        self.xMax, self.yMax = np.max(self.data, axis=0)
        self.xMin, self.yMin = np.min(self.data, axis=0)

class GroundLine(EntityClassBase):
    def __init__(self, data: np.array):
        super().__init__(data)
        if(self.data[0][0] > self.data[-1][0]):
            self.data = self.data[::-1]

    def fit(self, floodY: float):
        tmp = []
        if self.data[0][1] < floodY :
            exit(-1)
        for i in range(self.data.shape[0] - 1):
            if self.data[i][1] >= floodY and self.data[i + 1][1] >= floodY:
                continue
            elif self.data[i][1] < floodY and self.data[i + 1][1] < floodY:
                tmp.append(self.data[i + 1])
            elif self.data[i][1] >= floodY and self.data[i + 1][1] < floodY:
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((floodY - self.data[i + 1][1]) / (self.data[i][1] - self.data[i + 1][1])), floodY]))
                tmp.append(self.data[i + 1])
            else:
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((floodY - self.data[i][1]) / (self.data[i + 1][1] - self.data[i][1])), floodY]))
        self.data = np.array(tmp)

class Pier(EntityClassBase):
    def __init__(self, data: np.array):
        super().__init__(data)
        self.is_under = np.zeros(data.shape[0])

    def fitFlood(self, floodY: float):
        tmp = []
        for i in range(self.data.shape[0] - 1):
            if self.data[i][1] >= floodY and self.data[i + 1][1] >= floodY:
                continue
            elif self.data[i][1] < floodY and self.data[i + 1][1] < floodY:
                tmp.append(self.data[i])
            elif self.data[i][1] >= floodY and self.data[i + 1][1] < floodY:
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((floodY - self.data[i + 1][1]) / (self.data[i][1] - self.data[i + 1][1])), floodY]))
            else:
                tmp.append(self.data[i])
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((floodY - self.data[i][1]) / (self.data[i + 1][1] - self.data[i][1])), floodY]))
        self.data = np.array(tmp)
    def is_underGround(self, x, y, ground: GroundLine):
        ans = None
        for i in range(ground.data.shape[0] + 1):
            if(x >= ground.data[i][0] and x <= ground.data[i + 1][0]):
                ans = i
                break
        yy = ground.data[ans][1] + (ground.data[ans + 1][1] - ground.data[ans][1]) * ((x - ground.data[ans][0]) / (ground.data[ans + 1][0] - ground.data[ans][0]))
        if(y <= yy) :
            return True
        else:
            return False
    def fitGround(self, ground: GroundLine):
        crossTmp = []
        tmp = []
        for i in range(self.data.shape[0]):
            crossTmp.append([])
        for i in range(ground.data.shape[0] - 1):
            lineGround = [ground.data[i][0], ground.data[i][1], ground.data[i + 1][0], ground.data[i + 1][1]]
            for j in range(self.data.shape[0] - 1):
                linePier = [self.data[j][0], self.data[j][1], self.data[j + 1][0], self.data[j + 1][1]]
                crossAns = line_intersection(lineGround, linePier)
                if crossAns is None:
                    continue
                crossTmp[j].append(crossAns)
        for i in range(self.data.shape[0]):
            if(self.is_underGround(self.data[i][0], self.data[i][1], ground) == True):
                for j in crossTmp[i]:
                    tmp.append(j)
            else:
                tmp.append(self.data[i])
                for j in crossTmp[i]:
                    tmp.append(j)
        self.data = np.array(tmp)


