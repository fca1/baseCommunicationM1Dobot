from dataclasses import dataclass


@dataclass
class PositionArm:
    x:float
    y:float
    z:float
    r:float
    def __add__(self, other):
        self.x+=other.x
        self.y += other.y
        self.z += other.z
        self.r += other.r
        return self
    def __sub__(self, other):
        self.x-=other.x
        self.y -= other.y
        self.z -= other.z
        self.r -= other.r
        return self
