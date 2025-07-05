import random
from typing import List, Tuple, Optional

# Тип цвета: RGB float (0..1)
Color = Tuple[float, float, float]

# Примеры базовых цветов
BASE_COLORS: List[Color] = [
    (1.0, 0.0, 0.0),  # Красный
    (0.0, 1.0, 0.0),  # Зелёный
    (0.0, 0.0, 1.0),  # Синий
    (1.0, 1.0, 0.0),  # Жёлтый
    (1.0, 0.0, 1.0),  # Пурпурный
    (0.0, 1.0, 1.0),  # Голубой
]

# Размеры экрана (логика)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DELETE_ZONE = (0, 0, 100, 100)  # x, y, w, h — зона удаления (например, левый верхний угол)

class Ball:
    def __init__(self, x: float, y: float, radius: float, color: Color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.in_inventory = False

    def move(self):
        if not self.in_inventory:
            self.x += self.vx
            self.y += self.vy
            # Отскок от границ экрана (опционально, можно убрать)
            if self.x < self.radius:
                self.x = self.radius
                self.vx *= -1
            if self.x > SCREEN_WIDTH - self.radius:
                self.x = SCREEN_WIDTH - self.radius
                self.vx *= -1
            if self.y < self.radius:
                self.y = self.radius
                self.vy *= -1
            if self.y > SCREEN_HEIGHT - self.radius:
                self.y = SCREEN_HEIGHT - self.radius
                self.vy *= -1

    def is_inside(self, px: float, py: float) -> bool:
        return (self.x - px) ** 2 + (self.y - py) ** 2 <= self.radius ** 2

    def is_in_delete_zone(self) -> bool:
        x, y, w, h = DELETE_ZONE
        return x <= self.x <= x + w and y <= self.y <= y + h

class Inventory:
    def __init__(self):
        self.balls: List[Ball] = []

    def add(self, ball: Ball):
        ball.in_inventory = True
        self.balls.append(ball)

    def remove(self, ball: Ball):
        if ball in self.balls:
            self.balls.remove(ball)
            ball.in_inventory = False

class GameLogic:
    def __init__(self):
        self.balls: List[Ball] = []
        self.inventory = Inventory()

    def spawn_ball(self, x: float, y: float, radius: float = 20.0, color: Optional[Color] = None):
        if color is None:
            color = random.choice(BASE_COLORS)
        self.balls.append(Ball(x, y, radius, color))

    def move_balls(self):
        for ball in self.balls:
            ball.move()

    def pick_ball(self, px: float, py: float) -> Optional[Ball]:
        # "Всасывание" шарика мышкой (по координате)
        for ball in self.balls:
            if not ball.in_inventory and ball.is_inside(px, py):
                self.inventory.add(ball)
                return ball
        return None

    def drop_ball(self, x: float, y: float) -> Optional[Ball]:
        # "Выплёвывание" шарика из инвентаря
        if self.inventory.balls:
            ball = self.inventory.balls.pop(0)
            ball.x = x
            ball.y = y
            ball.in_inventory = False
            return ball
        return None

    def mix_balls(self):
        # Смешивание цветов при касании
        for i, ball1 in enumerate(self.balls):
            if ball1.in_inventory:
                continue
            for j, ball2 in enumerate(self.balls):
                if i >= j or ball2.in_inventory:
                    continue
                if self._balls_touch(ball1, ball2):
                    new_color = self._mix_colors(ball1.color, ball2.color)
                    ball1.color = new_color
                    ball2.color = new_color

    def delete_balls_in_zone(self):
        # Удаление шариков в зоне удаления
        self.balls = [ball for ball in self.balls if not ball.is_in_delete_zone()]

    @staticmethod
    def _balls_touch(ball1: Ball, ball2: Ball) -> bool:
        dx = ball1.x - ball2.x
        dy = ball1.y - ball2.y
        dist_sq = dx * dx + dy * dy
        r_sum = ball1.radius + ball2.radius
        return dist_sq <= r_sum * r_sum

    @staticmethod
    def _mix_colors(c1: Color, c2: Color) -> Color:
        # Математическое смешивание: усреднение RGB-компонент
        r = (c1[0] + c2[0]) / 2
        g = (c1[1] + c2[1]) / 2
        b = (c1[2] + c2[2]) / 2
        return (r, g, b) 