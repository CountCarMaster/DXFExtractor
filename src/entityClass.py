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
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((self.data[i][1] - floodY) / (self.data[i][1] - self.data[i + 1][1])), floodY]))
                tmp.append(self.data[i + 1])
            else:
                tmp.append(np.array([self.data[i][0] + (self.data[i + 1][0] - self.data[i][0]) * ((floodY - self.data[i][1]) / (self.data[i + 1][1] - self.data[i][1])), floodY]))
        self.data = np.array(tmp)
    def is_abovePier(self, pierList):
        for point in self.data:
            k = 0
            for pier in pierList:
                if point[0] < pier.xMin or point[0] > pier.xMax:
                    k += 1
                    continue
                tmp = []
                for i in range(pier.data.shape[0] - 1):
                    tmp.append(pier.data[i])
                    if point[0] < min(pier.data[i][0], pier.data[i + 1][0]) or point[0] > max(pier.data[i][0], pier.data[i + 1][0]):
                        continue
                    yy = pier.data[i][1] + (pier.data[i + 1][1] - pier.data[i][1]) * ((point[0] - pier.data[i][0]) / (pier.data[i + 1][0] - pier.data[i][0]))
                    if yy < point[1]:
                        tmp.append(point)
                tmp.append(pier.data[-1])
                pierList[k].data = np.array(tmp)
                k += 1
        return pierList

class Pier(EntityClassBase):
    def __init__(self, data: np.array):
        super().__init__(data)
        self.is_under = np.zeros(data.shape[0])
        self.beforeGround = None
        self.is_main = True
        self.fittings = []

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
        for i in range(ground.data.shape[0]):
            if(x >= ground.data[i][0] and x <= ground.data[i + 1][0]):
                ans = i
                break
        # print(x)
        # print(ground.data)
        # print(ans)
        if ans == None:
            return True
        yy = ground.data[ans][1] + (ground.data[ans + 1][1] - ground.data[ans][1]) * ((x - ground.data[ans][0]) / (ground.data[ans + 1][0] - ground.data[ans][0]))
        if(y <= yy) :
            return True
        else:
            return False
    def fitGround(self, ground: GroundLine):
        crossTmp = []
        tmp = []
        hajime = None
        flag = False
        for i in range(self.data.shape[0]):
            if self.is_underGround(self.data[i][0], self.data[i][1], ground) == False:
                flag = True
                break
        if flag == False:
            return False
        for i in range(self.data.shape[0]):
            crossTmp.append([])
        for i in range(ground.data.shape[0] - 1):
            lineGround = [ground.data[i][0], ground.data[i][1], ground.data[i + 1][0], ground.data[i + 1][1]]
            for j in range(self.data.shape[0] - 1):
                linePier = [self.data[j][0], self.data[j][1], self.data[j + 1][0], self.data[j + 1][1]]
                crossAns = line_intersection(lineGround, linePier)
                if crossAns is None:
                    continue
                crossTmp[j].append([i, crossAns])
        for i in range(self.data.shape[0]):
            if hajime is None and len(crossTmp[i]) % 2 == 1:
                hajime = crossTmp[i][-1][0]
            elif hajime is not None and len(crossTmp[i]) % 2 == 0 and len(crossTmp[i]) > 0:
                if hajime < crossTmp[i][0][0]:
                    for kk in range(hajime + 1, crossTmp[i][0][0] + 1):
                        tmp.append(ground.data[kk])
                else:
                    for kk in range(hajime + 1, crossTmp[i][0][0] + 1, -1):
                        tmp.append(ground.data[kk])
                hajime = crossTmp[i][-1][0]
            elif hajime is not None and len(crossTmp[i]) % 2 == 1:
                if hajime < crossTmp[i][0][0]:
                    for kk in range(hajime + 1, crossTmp[i][0][0] + 1):
                        tmp.append(ground.data[kk])
                else:
                    for kk in range(hajime + 1, crossTmp[i][0][0] + 1, -1):
                        tmp.append(ground.data[kk])
                hajime = None

            if self.is_underGround(self.data[i][0], self.data[i][1], ground) == True :
                for j in crossTmp[i]:
                    tmp.append(j[1])
            else:
                tmp.append(self.data[i])
                for j in crossTmp[i]:
                    tmp.append(j[1])
        self.data = np.array(tmp)


