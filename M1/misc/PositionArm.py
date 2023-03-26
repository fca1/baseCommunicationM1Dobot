from dataclasses import dataclass


@dataclass
class PositionArm:
    x: float = 400
    y: float = 0
    z: float = 230
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
