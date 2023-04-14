import math
from dataclasses import dataclass
import pickle


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

    @staticmethod
    def load(file):
        with open(file,mode="rb") as f:
            return pickle.load(f)

    def save(self,file):
        with open(file,mode="wb") as f:
            return pickle.dump(self,file=f)

    def copy(self):
        return PositionArm(self.x,self.y,self.z,self.r)

    def distance(self,other) -> float :
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
