from enum import IntEnum
import matplotlib.pyplot as plt

from math import sin, cos, radians, sqrt, pi
from shapely.geometry import Polygon


# define Python user-defined exceptions
class NotAllowedError(Exception):
    """Raised when performing not allowed operation."""
    pass


class Symmetry(IntEnum):
    none = 360
    twofold = 180
    threefold = 120
    fourfold = 90
    sixfold = 60


class ShapeGenerator(object):
    def __init__(self, radius: float, rotations: Symmetry, container=None):
        self._radius = radius
        self._rotations = rotations
        self._shape = None
        self._ready = True
        self._shapes = []
        self._container_coords = container
        if container is None:
            self._container = None
        else:
            self._container = Polygon(container)

    @property
    def current_shape(self):
        return self._shape


    def _get_first_n_shapes(self, n):
        """Use this function only for generating datasets, not for actual runs!!!
        """
        return [self._get_shape() for _ in range(n)]

    def new_shape(self):
        """Generate new shape and return it."""
        if self._ready:
            self._ready = False
            self._shape = self._get_shape()
            return self._shape
        else:
            raise NotAllowedError("Shape generator is not ready, submit previous shape position")

    def place_shape(self, x: float, y: float, rotation: int):
        """Place shape to have its position at given coordinates.

        x, y: coordinates of the first point of the shape (shape[0])
        rotation: rotation of the shape in degrees (must be allowed by symmetry)
        """
        if self._shape is None:
            raise NotAllowedError("There is no shape to place, get a new shape first")

        s = self._rotate_shape(self._shape, rotation)
        s = self._translate_shape(s, x, y)

        # check for corners outside the radius
        for corner in s:
            if self._container is None:
                distance = round(sqrt(corner[0] * corner[0] + corner[1] * corner[1]), 12)  # round to 12 decimal places because of floating point arithmetics problems)
                if distance > self._radius:
                    raise NotAllowedError(f"You can't place a shape outside of the circle of radius {self._radius}!")

        if self._container is not None:
            pol = Polygon(s)
            difference_area = pol.difference(self._container).area
            if difference_area > 0.000000000001:
                raise NotAllowedError(f"You can't place a shape outside of the container {self._container_coords}!")

        # check collisions using shapely library
        current_shape = Polygon(s)
        other_shapes = [Polygon(x) for x in self._shapes]
        for x in other_shapes:
            ar = current_shape.intersection(x).area
            if ar > 0.0000000002:
                print('-------------------------------------------------------overlap area:', ar)
            if ar > 0.00000001:
                raise NotAllowedError(f"You can't place a shape so it overlaps with other shape! Intersection area is", current_shape.intersection(x).area)

        self._shapes.append(s)
        self._shape = None
        self._ready = True

    def show_results(self, savename=None):
        f = plt.figure()
        # add circle
        ax = f.gca()
        ax.set_aspect(1)
        circle = plt.Circle((0, 0), self._radius, color='#aaa', alpha=0.5)
        ax.add_patch(circle)
        # add shapes
        for s in self._shapes:
            s = s + [s[0]]    # in order to close the loop
            xs, ys = zip(*s)  # zip to x and y
            plt.plot(xs, ys, alpha=0.75)
        if savename is None:
            plt.show()
        else:
            plt.savefig(f"{savename}.png", dpi=900)

    def print_results(self):
        print(f"Number of shapes: {len(self._shapes)}")
        print(f"Filled area: {self.filled_area}")

    @property
    def filled_area(self):
        polygons = [Polygon(x) for x in self._shapes]
        area = sum([x.area for x in polygons])  # total area of shapes
        if self._container is None:
            ratio = area / (pi * self._radius * self._radius)
        else:
            ratio = area / self._container.area
        # return value between 0 - 1
        return ratio
    
    @property
    def placed_shapes(self):
        return len(self._shapes)

    def _get_shape(self):
        raise NotImplementedError("You need to override this method")

    def _translate_shape(self, shape, x, y):
        """"""
        translated = []
        dx = x - shape[0][0]
        dy = y - shape[0][1]
        for corner in shape:
            translated.append([corner[0] + dx, corner[1] + dy])
        return translated

    def _rotate(self, point, angle, center_point=(0, 0)):
        """Rotates a point around center_point(origin by default).
        Angle is in degrees.
        Rotation is counter-clockwise.
        """
        angle_rad = radians(angle % 360)
        # Shift the point so that center_point becomes the origin
        new_point = (point[0] - center_point[0], point[1] - center_point[1])
        new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                     new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
        # Reverse the shifting we have done
        new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
        return new_point

    def _rotate_shape(self, shape, angle):
        """Rotates the current shape around first point.
        Rotation is counter-clockwise.
        Angle is in degrees.
        """
        if angle % int(self._rotations) > 0:
            raise NotAllowedError(f"Rotation of {angle}° is not allowed in {self._rotations} symmetry.")
        rotated = []
        center = shape[0]
        for corner in shape:
            rotated.append(self._rotate(corner, angle, center))
        return rotated


# SFG competition placer interface:
class Placer(object):
    def __init__(self, sg: ShapeGenerator):
        self._sg = sg
    
    def run(self):
        # do some magic
        return self._sg
