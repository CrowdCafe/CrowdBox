import math
from shapely.geometry import LineString

# -----------------------------------------------------------------------------------------------
# Polygons Geometry
# -----------------------------------------------------------------------------------------------
class Edge:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def getLength(self):
        return math.hypot(self.point2['x'] - self.point1['x'], self.point2['y'] - self.point1['y'])


class Polygon:
    def __init__(self, points):
        self.points = points

    def offset(self, distance):
        self.points.append(self.points[0])
        line = LineString(self.getSequence())
        offset = line.parallel_offset(distance, 'right', join_style=1)
        # return list(offset.coords)
        self.setSequence(list(offset.coords))
        return self

    def setSequence(self, sequence):
        self.points = [{'x': point[0], 'y': point[1]} for point in sequence]
        return self

    def getPoints(self):
        return self.points

    def getArea(self):
        total = 0.0
        N = len(self.points)

        for i in range(N):
            v1 = self.points[i]
            v2 = self.points[(i + 1) % N]
            total += v1['x'] * v2['y'] - v1['y'] * v2['x']

        return abs(total / 2)

    def getPerimeter(self):
        p = 0.0
        for i in range(1, len(self.points)):
            edge = Edge(self.points[i - 1], self.points[i])
            p += edge.getLength()
        return p

    def getCenter(self):
        x = [p['x'] for p in self.points]
        y = [p['y'] for p in self.points]

        return {
        'x': (max(x) + min(x)) / 2,
        'y': (max(y) + min(y)) / 2
        }

    def getScaled(self, multiplier_x, multiplier_y):  # multiplier x and y
        return [{'x': 1.0 * point['x'] * multiplier_x, 'y': 1.0 * point['y'] * multiplier_y} for point in self.points]

    def scale(self, multiplier_x, multiplier_y):  # multiplier x and y
        self.points = self.getScaled(multiplier_x, multiplier_y)
        return self


    def getSequence(self):
        return [(point['x'], point['y']) for point in self.points]

    def enlargeAbs(self, delta):
        center = self.getCenter()
        new_points = []
        for point in self.points:
            x = point['x'] - center['x']
            y = point['y'] - center['y']
            z = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

            if z > 0:
                fi = math.acos(1.0 * abs(x) / abs(z))

                point['x'] = 1.0 * math.copysign(1, x) * round((z + delta) * math.cos(fi), 2) + center['x']
                point['y'] = 1.0 * math.copysign(1, y) * round((z + delta) * math.sin(fi), 2) + center['y']
            new_points.append(point)
        self.points = new_points
        return self

    def enlargeRel(self, multiplier):
        center = self.getCenter()
        self.points = [{'x': multiplier * (point['x'] - center['x']) + center['x'],
                        'y': multiplier * (point['y'] - center['y']) + center['y']} for point in self.points]
        return self

    def getCorners(self):  # 1 - left top,2,3,4
        # if we imagine a rectangle around polygon, here we calculate diagonal length of such a rectangle
        xs = [point['x'] for point in self.points]
        ys = [point['y'] for point in self.points]
        return [{
                'x': int(min(xs)),
                'y': int(min(ys))
                }, {
                'x': int(max(xs)),
                'y': int(max(ys))
                }]

    def getAreaDiagonalLength(self):
        corners = self.getCorners()
        edge = Edge(corners[0], corners[1])
        return edge.getLength()