import pygame
from typing import Literal

pygame.init()
screen = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()
running = True
max_fps = 100

player_sprite = pygame.transform.scale(
    pygame.image.load("91ce98cec1df0f769321571724f1f312.jpg"), (100, 100)
)
background_sprite = pygame.image.load("d011d6bc1effc67ae5c74bbc5ce090c2.jpg")
pressed_key = []


x_of_display = 0
y_of_display = 0


class player_class:
    def __init__(self):
        self.x = screen.get_width() / 2
        self.y = screen.get_height() / 2
        self.angle = pygame.math.Vector2(-1, 0)
        self.max_speed = 7.5
        self.speed = pygame.math.Vector2(0, 0)

        self.tick_to_reach_max_speed = max_fps / 2
        self.tick_to_slow_down = max_fps / 5

        self.acceleration_per_tick = self.max_speed / self.tick_to_reach_max_speed
        self.deceleration_per_tick = self.max_speed / self.tick_to_slow_down

    def draw_self(
        self,
        sprite: pygame.Surface,
        angle: pygame.math.Vector2,
        x: float,
        y: float,
    ):
        x_relative, y_relative = get_coordinate_relative_to_screen(x, y)

        resized_sprite = pygame.transform.rotate(
            sprite,
            pygame.Vector2.as_polar(angle)[1] * -1 + 180,
        )  # *-1 pour aller de clockwise à counterclockwise
        pygame.Surface.blit(
            screen,
            resized_sprite,
            (
                x_relative - (pygame.Surface.get_width(resized_sprite) / 2),
                y_relative - (pygame.Surface.get_height(resized_sprite) / 2),
            ),
        )

    def accelerate(self, direction: str):
        global moved_this_tick
        match direction:
            case "right":
                self.speed[0] += self.acceleration_per_tick
            case "left":
                self.speed[0] -= self.acceleration_per_tick
            case "down":
                self.speed[1] += self.acceleration_per_tick
            case "up":
                self.speed[1] -= self.acceleration_per_tick
        if self.speed != pygame.Vector2(0, 0):  # otherwise clamp raise an error
            self.speed = self.speed.clamp_magnitude(0, self.max_speed)
        moved_this_tick = True

    def decelerate(self, direction: str):

        if self.speed.length() < self.deceleration_per_tick and not moved_this_tick:
            self.speed = pygame.Vector2(0, 0)
        else:
            match direction:
                case "right":
                    if self.speed[0] > 0:

                        self.speed[0] -= self.deceleration_per_tick
                case "left":
                    if self.speed[0] < 0:

                        self.speed[0] += self.deceleration_per_tick
                case "down":
                    if self.speed[1] > 0:

                        self.speed[1] -= self.deceleration_per_tick
                case "up":
                    if self.speed[1] < 0:

                        self.speed[1] += self.deceleration_per_tick


def get_coordinate_relative_to_screen(x, y):
    x_relative = x - x_of_display
    y_relative = y - y_of_display
    return (x_relative, y_relative)


def set_rect_center_at(rectangle: pygame.Rect, x: float, y: float):
    return rectangle.move(x - rectangle.width / 2, y - rectangle.height / 2)


def screen_follow_position(x: float, y: float, strength: float):
    global x_of_display
    global y_of_display
    x_at_corner = x - screen.get_width() / 2
    y_at_corner = y - screen.get_height() / 2
    if x_of_display != x_at_corner or y_of_display != y_at_corner:
        distance_to_object = pygame.Vector2(
            x - (x_of_display + x_at_corner),
            y - (y_of_display + y_at_corner),
        )

        x_of_display = x_of_display - (x_of_display - x_at_corner) * (
            (1 / distance_to_object.length()) * strength
        )
        y_of_display = y_of_display - (y_of_display - y_at_corner) * (
            (1 / distance_to_object.length()) * strength
        )


def show_image(sprite: pygame.Surface, x, y):
    x_relative, y_relative = get_coordinate_relative_to_screen(x, y)
    pygame.Surface.blit(
        screen,
        sprite,
        (
            x_relative - (pygame.Surface.get_width(sprite) / 2),
            y_relative - (pygame.Surface.get_height(sprite) / 2),
        ),
    )


key_map = dict(z="up", s="down", d="right", q="left")


def key_mapping(key: str):
    return key_map[key]


case_size = 200
wall_width = 20


def show_wall(x_case: int, y_case: int, is_bottom: bool):
    if is_bottom:
        pygame.draw.rect(
            screen,
            "white",
            pygame.Rect(
                case_size * x_case - x_of_display,
                case_size * y_case - y_of_display,
                wall_width,
                case_size,
            ),
        )
    else:
        pygame.draw.rect(
            screen,
            "white",
            pygame.Rect(
                case_size * x_case - x_of_display,
                case_size * y_case - y_of_display,
                case_size,
                wall_width,
            ),
        )


player = player_class()


while running:
    show_image(background_sprite, 0, 0)
    print(player.x, player.y)
    show_wall(0, 0, False)
    show_wall(0, 0, True)

    screen_follow_position(player.x, player.y, 150)

    player.draw_self(player_sprite, player.angle, player.x, player.y)
    pygame.display.flip()
    screen.fill("black")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pressed_key.append(pygame.key.name(event.key))
        if event.type == pygame.KEYUP:
            pressed_key.pop(pressed_key.index(pygame.key.name(event.key)))

    not_pressed_key = ["z", "q", "s", "d"]
    moved_this_tick = False
    for key in pressed_key:
        player.accelerate(key_mapping(key))
        not_pressed_key.pop(not_pressed_key.index(key))

    for key in not_pressed_key:
        player.decelerate(key_mapping(key))

    player.x += player.speed[0]
    player.y += player.speed[1]
    clock.tick_busy_loop(max_fps)
