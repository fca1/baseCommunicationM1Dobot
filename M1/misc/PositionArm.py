import math
from dataclasses import dataclass
import pickle
import json

@dataclass(unsafe_hash=True)
class PositionArm:
    x: float = 0
    y: float = 0
    z: float = 0
    r: float = 0

    def __add__(self, other):
        s = self.copy()
        s.x += other.x
        s.y += other.y
        s.z += other.z
        s.r += other.r
        return s

    def __sub__(self, other):
        s = self.copy()
        s.x -= other.x
        s.y -= other.y
        s.z -= other.z
        s.r -= other.r
        return s

    def __neg__(self):
        s = PositionArm()
        s.x = -self.x
        s.y = -self.y
        s.z = -self.z
        s.r = -self.r
        return s

    @staticmethod
    def load(file):
        with open(file, mode="r") as f:
            dct = json.loads(f.readline())
            return PositionArm(dct["x"],dct["y"], dct["z"], dct["r"])


    def save(self, file):
        dct = { "x":self.x,
                "y":self.y,
                "z":self.z,
                "r":self.r}
        with open(file, mode="w") as f:
            x = json.dumps(dct)
            f.write(x)

    def copy(self):
        return PositionArm(self.x, self.y, self.z, self.r)

    def distance(self, other) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
