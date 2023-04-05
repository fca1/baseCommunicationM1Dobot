from dataclasses import dataclass
import pickle


@dataclass
class PositionArm:
    x: float = 0
    y: float = 0
    z: float = 0
    r: float = 0

    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        self.r += other.r
        return self

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        self.r -= other.r
        return self

    def load(self,file):
        return pickle.dump(self,file=file)

    def save(self,file):
        return pickle.load(file)