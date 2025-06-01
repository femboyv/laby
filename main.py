import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()
running = True
max_fps = 100


background_sprite = pygame.image.load("d011d6bc1effc67ae5c74bbc5ce090c2.jpg")
pressed_key = []


x_of_display = 0
y_of_display = 0


class player_class:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.angle = pygame.math.Vector2(-1, 0)
        self.max_speed = 7.5
        self.speed = pygame.math.Vector2(0, 0)

        self.tick_to_reach_max_speed = max_fps / 2
        self.tick_to_slow_down = max_fps / 5

        self.acceleration_per_tick = self.max_speed / self.tick_to_reach_max_speed
        self.deceleration_per_tick = self.max_speed / self.tick_to_slow_down

        self.height = 100
        self.rect = pygame.Rect(0, 0, self.height, self.height)

        self.collide_box = self.rect

        self.sprite = pygame.transform.scale(
            pygame.image.load("91ce98cec1df0f769321571724f1f312.jpg"),
            (self.height, self.height),
        )

    def draw_self(
        self,
        sprite: pygame.Surface,
        angle: pygame.math.Vector2,
        x: float,
        y: float,
    ):
        self.x_relative, self.y_relative = get_coordinate_relative_to_screen(x, y)

        resized_sprite = pygame.transform.rotate(
            sprite,
            pygame.Vector2.as_polar(angle)[1] * -1 + 180,
        )  # *-1 pour aller de clockwise à counterclockwise
        pygame.Surface.blit(
            screen,
            resized_sprite,
            (
                self.x_relative - (pygame.Surface.get_width(resized_sprite) / 2),
                self.y_relative - (pygame.Surface.get_height(resized_sprite) / 2),
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

    def update_collision_box(self):
        self.rect.x = self.x_relative
        self.rect.y = self.y_relative
        self.collide_box = self.rect
        self.collide_box.x += self.speed.x
        self.collide_box.y += self.speed.y
        pygame.draw.rect(screen, "red", self.rect)

    def handle_movement(self):
        self.update_collision_box()
        if collide_with_wall(self.rect):
            self.speed.x = 0
        if collide_with_wall(self.rect):
            self.speed.y = 0
        self.x += self.speed.x
        self.y += self.speed.y


def get_coordinate_relative_to_screen(x, y):
    x_relative = x - x_of_display
    y_relative = y - y_of_display
    return (x_relative, y_relative)


def set_rect_center_at(rectangle: pygame.Rect, x: float, y: float):
    rectangle.x = x - rectangle.width / 2
    rectangle.y = y - rectangle.height / 2
    return rectangle


def screen_follow_position(x: float, y: float, strength: float):
    global x_of_display
    global y_of_display
    x_at_corner = x - screen.get_width() / 2
    y_at_corner = y - screen.get_height() / 2

    if x_of_display != x_at_corner or y_of_display != y_at_corner:
        distance_to_object = pygame.Vector2(
            x_at_corner - x_of_display,
            y_at_corner - y_of_display,
        )

        x_of_display = x_of_display + (x_at_corner - x_of_display) * (
            distance_to_object.length() / screen.get_width() * strength
        )
        y_of_display = y_of_display + (y_at_corner - y_of_display) * (
            distance_to_object.length() / screen.get_height() * strength
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


type_of_wall = dict(
    STRAIGHT_VERTICAL=("i", (1, 3)),
    STRAIGHT_HORIZONTAL=("_", (0, 2)),
    TURN_TOP_RIGHT=("p", (1, 2)),
    TURN_TOP_LEFT=("o", (2, 3)),
    TURN_DOWN_RIGHT=("m", (0, 1)),
    TURN_DOWN_LEFT=("l", (0, 3)),
    END_UP=("z", (1, 2, 3)),
    END_LEFT=("q", (0, 2, 3)),
    END_DOWN=("s", (0, 1, 3)),
    END_RIGHT=("d", (0, 1, 2)),
    NONE=("f", ()),
    ALL=("g", (0, 1, 2, 3)),
    TOP=("f", (0,)),
    DOWN=("f", (2,)),
    RIGHT=("f", (3,)),
    LEFT=("f", (1,)),
)


tile_size = 200
wall_width = 20
map_tile_height = 50
map_tile_width = 50


def generate_map():

    wall_map = []

    position = (0, 0)

    for y in range(map_tile_height):  # height
        for _ in range(int(map_tile_width / 2)):  # width
            wall_map.append((position, generate_random_tile()))
            position = (position[0] + 2, position[1])

        position = (y % 2, position[1] + 1)

    return wall_map


def generate_random_tile():
    list_of_type = list(type_of_wall)
    return type_of_wall[list_of_type[random.randrange(list_of_type.__len__())]]


wall_map = generate_map()


def get_walls_by_position(tile_position: tuple):
    global number_of_tile_rendered
    letter = get_tile_by_position(tile_position)
    walls_of_tile = []

    wall_to_draw = letter[1]

    number_of_tile_rendered += 1
    for wall in wall_to_draw:
        walls_of_tile.append(get_walls_by_letter(tile_position, wall))
    return walls_of_tile


def get_walls_by_letter(tile_position: tuple, orientation: int):

    match orientation:  # 0 is up and it's going counterclockwise (i think)
        case 0:
            rect_to_draw = pygame.Rect(
                tile_size * tile_position[0] - x_of_display,
                tile_size * tile_position[1] - y_of_display,
                tile_size + wall_width,
                wall_width,
            )
        case 1:
            rect_to_draw = pygame.Rect(
                tile_size * tile_position[0] - x_of_display,
                tile_size * tile_position[1] - y_of_display,
                wall_width,
                tile_size + wall_width,
            )
        case 2:
            rect_to_draw = pygame.Rect(
                tile_size * (tile_position[0]) - x_of_display,
                tile_size * (tile_position[1] + 1) - y_of_display,
                tile_size + wall_width,
                wall_width,
            )
        case 3:
            rect_to_draw = pygame.Rect(
                tile_size * (tile_position[0] + 1) - x_of_display,
                tile_size * (tile_position[1]) - y_of_display,
                wall_width,
                tile_size + wall_width,
            )

    return rect_to_draw


def get_tile_by_position(position: tuple):
    position_in_map = int(position[0] * position[1] / 2)
    tile = wall_map[position_in_map][1]
    return tile


def get_all_point_in_rect(position_start: tuple, position_end: tuple):
    # could add position_end[1]+1 to include the point on the edge or not
    all_point = []
    for y in range(position_start[1], position_end[1]):
        for x in range(position_start[0], position_end[0]):
            all_point.append((x, y))
    return all_point


tile_width_of_screen = math.ceil(screen.get_width() / tile_size) + 1
tile_height_of_screen = math.ceil(screen.get_height() / tile_size) + 1


def get_tiles_at_screen():
    x_of_display_in_tile = math.floor(x_of_display / tile_size)
    y_of_display_in_tile = math.floor(y_of_display / tile_size)
    return get_all_point_in_rect(
        (x_of_display_in_tile, y_of_display_in_tile),
        (
            tile_width_of_screen + x_of_display_in_tile,
            tile_height_of_screen + y_of_display_in_tile,
        ),
    )


def draw_all_wall(walls_to_draw: list):
    for wall in walls_to_draw:
        pygame.draw.rect(screen, "white", wall)


player = player_class()


def set_tile_in_map(position: tuple, tile: tuple):
    position_in_map = int(position[0] * position[1] / 2)
    wall_map[position_in_map] = (position, tile)


walls_rendered = []


def collide_with_wall(
    collide_box: pygame.Rect = player.collide_box,
    rects_to_collide_with: list = walls_rendered,
):

    print(collide_box.collidelist(rects_to_collide_with))
    if collide_box.collidelist(rects_to_collide_with) == -1:
        return False
    else:
        return True


while running:

    walls_rendered = []

    number_of_tile_rendered = 0

    set_tile_in_map((0, 1), type_of_wall["NONE"])
    set_tile_in_map((0, 2), type_of_wall["NONE"])
    set_tile_in_map((1, 1), type_of_wall["NONE"])
    set_tile_in_map((1, 2), type_of_wall["NONE"])

    tiles_at_screen = get_tiles_at_screen()

    for tile_position in tiles_at_screen:
        walls_rendered += get_walls_by_position(
            tile_position
        )  # += used to merge the two lists insted of adding a list in a list with append

    draw_all_wall(walls_rendered)

    player.rect = set_rect_center_at(
        player.rect, player.x - x_of_display, player.y - y_of_display
    )

    if number_of_tile_rendered != tiles_at_screen.__len__():
        raise ValueError(
            "number_of_rendered_tiles can't be more than number of tiles_at_screen"
        )

    screen_follow_position(player.x, player.y, 0.75)

    player.draw_self(player.sprite, player.angle, player.x, player.y)

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

    player.handle_movement()

    pygame.display.flip()
    screen.fill("black")

    clock.tick_busy_loop(max_fps)
