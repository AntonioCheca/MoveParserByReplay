class Region:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_left_x(self) -> int:
        return self.x

    def get_top_y(self) -> int:
        return self.y

    def get_right_x(self) -> int:
        return self.x + self.width

    def get_bottom_y(self) -> int:
        return self.y + self.height

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height
