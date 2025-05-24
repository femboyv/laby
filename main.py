import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
max_fps = 75

player_sprite = pygame.image.load("91ce98cec1df0f769321571724f1f312.jpg")
background_sprite = pygame.image.load("d011d6bc1effc67ae5c74bbc5ce090c2.jpg")
pressed_key = []


x_of_display = 0
y_of_display = 0

FROM_RIGHT_TOP_TO_MIDDLE_SCREEN_VECTOR = pygame.Vector2(
    screen.get_width() / 2, screen.get_height() / 2
)


class player_class:
    def __init__(self):
        self.x = screen.get_width() / 2
        self.y = screen.get_height() / 2
        self.angle = pygame.math.Vector2(-1, 0)
        self.max_speed = 10
        self.speed = pygame.math.Vector2(0, 0)

        self.tick_to_reach_max_speed = 40
        self.tick_to_slow_down = 10

        self.acceleration_per_tick = pygame.math.Vector2(
            self.max_speed / self.tick_to_reach_max_speed, 0
        )

    def draw_self(
        self,
        sprite: pygame.Surface,
        angle: pygame.math.Vector2,
        x: float,
        y: float,
        width=100,
    ):
        x_relative, y_relative = get_coordinate_relative_to_screen(x, y)
        print(x_relative, y_relative)
        width_ratio = width / pygame.Surface.get_width(sprite)
        resized_sprite = pygame.transform.rotozoom(
            sprite,
            pygame.Vector2.as_polar(angle)[1] * -1 + 180,
            width_ratio,
        )  # *-1 pour aller de clockwise à counterclockwise
        pygame.Surface.blit(
            screen,
            resized_sprite,
            (
                x_relative - (pygame.Surface.get_width(resized_sprite) / 2),
                y_relative - (pygame.Surface.get_height(resized_sprite) / 2),
            ),
        )

    def accelerate(self, angle=float):
        """0 of angle is on right and it goes counterclowkize"""
        if self.speed.length() < self.max_speed:
            self.speed += pygame.math.Vector2.rotate(self.acceleration_per_tick, angle)

    def slow_down(self):
        if self.speed.length() > 0:
            if self.speed.length() > self.max_speed / self.tick_to_slow_down:
                self.speed.scale_to_length(
                    self.speed.length() - self.max_speed / self.tick_to_slow_down
                )
            else:
                self.speed = pygame.Vector2(0, 0)


def get_coordinate_relative_to_screen(x, y):
    x_relative = x - x_of_display
    y_relative = y - y_of_display
    return (x_relative, y_relative)


def display_follow_position(x, y, looseness_distance: float = 0):
    global x_of_display
    global y_of_display
    if looseness_distance == 0:
        x_of_display = x - (screen.get_width() / 2)
        y_of_display = y - (screen.get_height() / 2)
    else:

        distance_to_object = pygame.Vector2(
            x - (x_of_display + screen.get_width() / 2),
            y - (y_of_display + screen.get_height() / 2),
        )
        if distance_to_object.length() > looseness_distance:
            distance_looseness = distance_to_object.copy()
            distance_looseness.scale_to_length(looseness_distance)
            distance_to_object_without_looseness = (
                distance_to_object - distance_looseness
            )
            x_of_display += distance_to_object_without_looseness[0]
            y_of_display += distance_to_object_without_looseness[1]

    pygame.draw.line(
        screen,
        "red",
        (x_of_display + screen.get_width() / 2, y_of_display + screen.get_height() / 2),
        distance_to_object + FROM_RIGHT_TOP_TO_MIDDLE_SCREEN_VECTOR,
    )
    pygame.draw.circle(screen, "blue", (x_of_display, y_of_display), 20)


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


player = player_class()

while running:

    show_image(background_sprite, 0, 0)

    display_follow_position(player.x, player.y, 50)

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
    for key in pressed_key:

        if key == "z":
            player.accelerate(270)
        if key == "q":
            player.accelerate(180)
        if key == "s":
            player.accelerate(90)
        if key == "d":
            player.accelerate(0)

    if not (
        "z" in pressed_key
        or "q" in pressed_key
        or "s" in pressed_key
        or "d" in pressed_key
    ):  # has to be outside of for loop 'cause it don't execute when no key are being pressed
        player.slow_down()

    player.x += player.speed[0]
    player.y += player.speed[1]
    clock.tick(max_fps)
