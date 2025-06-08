import math
import json

letter_to_walls_map = {
    "i": (1, 3),
    "_": (0, 2),
    "p": (1, 2),
    "o": (2, 3),
    "m": (0, 1),
    "l": (0, 3),
    "z": (1, 2, 3),
    "q": (0, 2, 3),
    "s": (0, 1, 3),
    "d": (0, 1, 2),
    "f": (),
    "g": (0, 1, 2, 3),
    "u": (0,),
    "j": (2,),
    "h": (3,),
    "k": (1,),
}


walls_to_letter_map = {
    (1, 3): "i",
    (0, 2): "_",
    (1, 2): "p",
    (2, 3): "o",
    (0, 1): "m",
    (0, 3): "l",
    (1, 2, 3): "z",
    (0, 2, 3): "q",
    (0, 1, 3): "s",
    (0, 1, 2): "d",
    (): "f",
    (0, 1, 2, 3): "g",
    (0,): "u",
    (2,): "j",
    (3,): "h",
    (1,): "k",
}


def lettter_to_walls(letter: str):
    return letter_to_walls_map[letter]


def walls_to_letter(walls=tuple):
    return walls_to_letter_map[walls]


def print_to_file(content):
    with open("actual_map.txt", "w") as file:
        file.write(str(content))
    return content


def read_from_file():
    with open("actual_map.txt") as file:
        print(type(file.read()))
        return json.loads(file.read())


world_width = 18

script = """im_________u_____lik_________k____liiim______liim___hiizh_____liiiid__oip_j____lipoip__u_om_____lip__hm__hmlim____ok___himliiiipu____om__oiiiiii"""

# STRAIGHT_VERTICAL   i   1 3
# STRAIGHT_HORIZONTAL   _   0 2
# TURN_TOP_RIGHT   p   1 2
# TURN_TOP_LEFT   o   2 3
# TURN_DOWN_RIGHT   m   0 1
# TURN_DOWN_LEFT   l   0 3
# END_UP   z   1 2 3
# END_LEFT   q   0 2 3
# END_DOWN   s   0 1 3
# END_RIGHT   d   0 1 2
# NONE   f
# ALL   g   0 1 2 3
# TOP   u   0
# DOWN   j   2
# RIGHT   h   3
# LEFT   k   1


def convert_script_to_world(script=str):
    output = []
    for i, letter in enumerate(script):

        output.append(((i % world_width, math.floor(i / (world_width))), letter))


convert_script_to_world(script)

import pygame
import random


pygame.init()
screen = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()
running = True
max_fps = 100


cat_sprite = pygame.image.load("cattt.jpg")
pressed_key = []


x_of_display = 0
y_of_display = 0


class tile_class:
    def __init__(self, location: tuple, letter: str):
        self.loaded = False
        self.location = location
        self.letter = letter
        self.murs = None
        self.walls = None

    def __str__(self):
        return f"{self.location},{self.letter}"

    def __repr__(self):
        # repr and str are the same because repr is used in iterables (list) and str when it's only called once
        return str(self)

    def loads(self):
        if not self.loaded:
            self.get_walls()
            self.get_murs()
            self.loaded = True

    def get_walls(self) -> tuple:
        if self.walls != None:
            return self.walls
        else:
            try:
                self.walls = letter_to_walls[self.letter]
                return letter_to_walls[self.letter]
            except KeyError:
                self.walls = letter_to_walls["g"]
                return letter_to_walls["g"]  #  f for Null

    def get_murs(self):

        if self.murs != None:
            return self.murs
        else:
            murs = []
            if self.walls == None:
                self.get_walls()
            for orientation in self.walls:

                match orientation:  # 0 is up and it's going counterclockwise (i think(i'm  actually pretty sure))
                    case 0:
                        rect_to_draw = pygame.Rect(
                            tile_size * self.location[0] - x_of_display,
                            tile_size * self.location[1] - y_of_display,
                            tile_size + wall_width,
                            wall_width,
                        )
                    case 1:
                        rect_to_draw = pygame.Rect(
                            tile_size * self.location[0] - x_of_display,
                            tile_size * self.location[1] - y_of_display,
                            wall_width,
                            tile_size + wall_width,
                        )
                    case 2:
                        rect_to_draw = pygame.Rect(
                            tile_size * (self.location[0]) - x_of_display,
                            tile_size * (self.location[1] + 1) - y_of_display,
                            tile_size + wall_width,
                            wall_width,
                        )
                    case 3:
                        rect_to_draw = pygame.Rect(
                            tile_size * (self.location[0] + 1) - x_of_display,
                            tile_size * (self.location[1]) - y_of_display,
                            wall_width,
                            tile_size + wall_width,
                        )
                murs.append(rect_to_draw)
            self.murs = murs
            return murs

    def highlight(self):
        rect_to_draw = pygame.Rect(
            tile_size * self.location[0] - x_of_display,
            tile_size * self.location[1] - y_of_display,
            tile_size,
            tile_size,
        )
        pygame.draw.rect(
            MAP_SURFACE_CONSTANT,
            "green",
            rect_to_draw,
        )


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


def show_image(sprite: pygame.Surface, area: tuple | pygame.Rect):
    if isinstance(area, pygame.Rect):
        sprite = pygame.transform.scale(sprite, (area.width, area.height))
    x_relative, y_relative = get_coordinate_relative_to_screen(area.x, area.y)
    pygame.Surface.blit(
        screen,
        sprite,
        (
            x_relative - (pygame.Surface.get_width(sprite) / 2),
            y_relative - (pygame.Surface.get_height(sprite) / 2),
        ),
    )


key_map = dict()


def key_mapping(key: str):
    try:
        return key_map[key]
    except KeyError:
        return "nothing mapped"


letter_to_walls = {
    "i": (1, 3),
    "_": (0, 2),
    "p": (1, 2),
    "o": (2, 3),
    "m": (0, 1),
    "l": (0, 3),
    "z": (1, 2, 3),
    "q": (0, 2, 3),
    "s": (0, 1, 3),
    "d": (0, 1, 2),
    "f": (),
    "g": (0, 1, 2, 3),
    "u": (0,),
    "j": (2,),
    "h": (3,),
    "k": (1,),
}


tile_size = 200
wall_width = 20


scripted_map = [
    ((0, 0), "i"),
    ((1, 0), "m"),
    ((2, 0), "_"),
    ((3, 0), "_"),
    ((4, 0), "_"),
    ((5, 0), "_"),
    ((6, 0), "_"),
    ((7, 0), "_"),
    ((8, 0), "_"),
    ((9, 0), "_"),
    ((10, 0), "_"),
    ((11, 0), "u"),
    ((12, 0), "_"),
    ((13, 0), "_"),
    ((14, 0), "_"),
    ((15, 0), "_"),
    ((16, 0), "_"),
    ((17, 0), "l"),
    ((0, 1), "i"),
    ((1, 1), "k"),
    ((2, 1), "_"),
    ((3, 1), "_"),
    ((4, 1), "_"),
    ((5, 1), "_"),
    ((6, 1), "_"),
    ((7, 1), "_"),
    ((8, 1), "_"),
    ((9, 1), "_"),
    ((10, 1), "_"),
    ((11, 1), "k"),
    ((12, 1), "_"),
    ((13, 1), "_"),
    ((14, 1), "_"),
    ((15, 1), "_"),
    ((16, 1), "l"),
    ((17, 1), "i"),
    ((0, 2), "i"),
    ((1, 2), "i"),
    ((2, 2), "m"),
    ((3, 2), "_"),
    ((4, 2), "_"),
    ((5, 2), "_"),
    ((6, 2), "_"),
    ((7, 2), "_"),
    ((8, 2), "_"),
    ((9, 2), "l"),
    ((10, 2), "i"),
    ((11, 2), "i"),
    ((12, 2), "m"),
    ((13, 2), "_"),
    ((14, 2), "_"),
    ((15, 2), "_"),
    ((16, 2), "h"),
    ((17, 2), "i"),
    ((0, 3), "i"),
    ((1, 3), "z"),
    ((2, 3), "h"),
    ((3, 3), "_"),
    ((4, 3), "_"),
    ((5, 3), "_"),
    ((6, 3), "_"),
    ((7, 3), "_"),
    ((8, 3), "l"),
    ((9, 3), "i"),
    ((10, 3), "i"),
    ((11, 3), "i"),
    ((12, 3), "i"),
    ((13, 3), "d"),
    ((14, 3), "_"),
    ((15, 3), "_"),
    ((16, 3), "o"),
    ((17, 3), "i"),
    ((0, 4), "p"),
    ((1, 4), "_"),
    ((2, 4), "j"),
    ((3, 4), "_"),
    ((4, 4), "_"),
    ((5, 4), "_"),
    ((6, 4), "_"),
    ((7, 4), "l"),
    ((8, 4), "i"),
    ((9, 4), "p"),
    ((10, 4), "o"),
    ((11, 4), "i"),
    ((12, 4), "p"),
    ((13, 4), "_"),
    ((14, 4), "_"),
    ((15, 4), "u"),
    ((16, 4), "_"),
    ((17, 4), "o"),
    ((0, 5), "m"),
    ((1, 5), "_"),
    ((2, 5), "_"),
    ((3, 5), "_"),
    ((4, 5), "_"),
    ((5, 5), "_"),
    ((6, 5), "l"),
    ((7, 5), "i"),
    ((8, 5), "p"),
    ((9, 5), "_"),
    ((10, 5), "_"),
    ((11, 5), "h"),
    ((12, 5), "m"),
    ((13, 5), "_"),
    ((14, 5), "_"),
    ((15, 5), "h"),
    ((16, 5), "m"),
    ((17, 5), "l"),
    ((0, 6), "i"),
    ((1, 6), "m"),
    ((2, 6), "_"),
    ((3, 6), "_"),
    ((4, 6), "_"),
    ((5, 6), "_"),
    ((6, 6), "o"),
    ((7, 6), "k"),
    ((8, 6), "_"),
    ((9, 6), "_"),
    ((10, 6), "_"),
    ((11, 6), "h"),
    ((12, 6), "i"),
    ((13, 6), "m"),
    ((14, 6), "l"),
    ((15, 6), "i"),
    ((16, 6), "i"),
    ((17, 6), "i"),
    ((0, 7), "i"),
    ((1, 7), "p"),
    ((2, 7), "u"),
    ((3, 7), "_"),
    ((4, 7), "_"),
    ((5, 7), "_"),
    ((6, 7), "_"),
    ((7, 7), "o"),
    ((8, 7), "m"),
    ((9, 7), "_"),
    ((10, 7), "_"),
    ((11, 7), "o"),
    ((12, 7), "i"),
    ((13, 7), "i"),
    ((14, 7), "i"),
    ((15, 7), "i"),
    ((16, 7), "i"),
    ((17, 7), "i"),
]


def generate_map(script: list = None, width: int = 50, height: int = 50):

    if script != None:
        world_width_in_tile, world_height_in_tile = (
            check_for_max_width_and_height_of_map(script)
        )
        world_tiles = []
        for coordinate_and_letter in script:
            world_tiles.append(
                tile_class(coordinate_and_letter[0], coordinate_and_letter[1])
            )

        return (world_tiles, world_width_in_tile, world_height_in_tile)

    else:

        world_tiles = []

        position = (0, 0)

        for _ in range(height):  # height
            for _ in range(width):  # width
                world_tiles.append(tile_class(position, generate_random_letter()))
                position = (position[0] + 1, position[1])

            position = (0, position[1] + 1)

        return (world_tiles, width, height)


def generate_random_letter():
    possibility = "ujhk_if"  # only tile with 2 walls or less
    return possibility[random.randrange(possibility.__len__())]


def check_for_max_width_and_height_of_map(map) -> tuple[int, int]:
    return (map[len(map) - 1][0][0] + 1, map[len(map) - 1][0][1])


tile_map, world_width_in_tile, world_height_in_tile = generate_map(scripted_map)


def get_murs_of_coordinate(tile_position: tuple):

    global number_of_tile_rendered
    letter = get_tile_by_coordinate(tile_position)
    murs_of_tile = []

    walls_to_draw = letter.get_walls()

    number_of_tile_rendered += 1

    for wall in walls_to_draw:

        murs_of_tile.append(get_mur_from_wall(tile_position, wall))
    return murs_of_tile


def get_mur_from_wall(tile_position: tuple, orientation: int):

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


def get_tile_by_coordinate(coordinate: tuple):
    if coordinate[0] >= 0 and coordinate[1] >= 0:
        coordinate_in_map = int(coordinate[0] + coordinate[1] * world_width_in_tile)

        try:
            tile = tile_map[coordinate_in_map]
            tile: tile_class
        except IndexError:

            return tile_class(coordinate, "g")  # "f" for blank

        if (  # when outside of the map
            coordinate[0] > world_width_in_tile - 1
            or coordinate[1] > world_height_in_tile - 1
        ):

            return tile_class(coordinate, "g")  # "f" for blank

        if tile.location != coordinate:
            raise ValueError(
                "the coordinate of the output (%d,%d) weren't the coordinate of the input (%d,%d)"
                % (
                    tile_map[coordinate_in_map][0][0],
                    tile_map[coordinate_in_map][0][1],
                    coordinate[0],
                    coordinate[1],
                )
            )

        return tile
    else:
        return tile_class(coordinate, "g")


def get_all_point_in_rect(position_start: tuple, position_end: tuple):
    # could add position_end[1]+1 to include the point on the edge or not
    all_point = []
    for y in range(position_start[1], position_end[1]):
        for x in range(position_start[0], position_end[0]):
            all_point.append((x, y))
    return all_point


zoom_level = 1


def set_width_and_height_of_screen_in_tiles():
    return int((math.ceil(screen.get_width() / tile_size) + 1) * zoom_level), int(
        (math.ceil(screen.get_height() / tile_size) + 1) * zoom_level
    )


def get_tiles_at_screen():
    x_of_display_in_tile = math.floor((x_of_display / tile_size))
    y_of_display_in_tile = math.floor((y_of_display / tile_size))

    return get_all_point_in_rect(
        (x_of_display_in_tile, y_of_display_in_tile),
        (
            width_of_screen_in_tile + x_of_display_in_tile,
            height_of_screen_in_tile + y_of_display_in_tile,
        ),
    )


def draw_all_wall(walls_to_draw: list):

    output_surface = pygame.Surface(
        (world_width_in_tile * tile_size, world_height_in_tile * tile_size)
    )
    for wall in walls_to_draw:
        pygame.draw.rect(output_surface, "white", wall)
    pygame.Surface.blit(
        screen, pygame.transform.scale(output_surface, screen.get_size()), (0, 0)
    )


murs_rendered = []


def closest_to(number: float, first_number: float, second_number: float):
    if abs(number - first_number) == abs(number - second_number):
        return 0
    elif abs(number - first_number) < abs(number - second_number):
        return first_number
    else:
        return second_number


width_decalage_of_map_by_screen = 10
height_decalage_of_map_by_screen = 10


def generate_map_surface() -> pygame.Surface:
    output_surface = pygame.Surface(
        (
            world_width_in_tile * tile_size + wall_width,
            world_height_in_tile * tile_size + wall_width,
        )
    )

    for tile in tile_map:
        tile: tile_class
        for mur in tile.get_murs():
            pygame.draw.rect(output_surface, "white", mur)
    ratio_of_width_and_height_of_output = (output_surface.get_width() + wall_width) / (
        output_surface.get_height() + wall_width
    )

    if ratio_of_width_and_height_of_output < (screen.get_width() / screen.get_height()):
        scaled_output_surface = pygame.transform.scale(
            output_surface(
                screen.get_height() * ratio_of_width_and_height_of_output
                - width_decalage_of_map_by_screen * 2,
                screen.get_height() - height_decalage_of_map_by_screen * 2,
            ),
        )
    else:
        scaled_output_surface = pygame.transform.scale(
            output_surface,
            (
                screen.get_width() - width_decalage_of_map_by_screen * 2,
                screen.get_width() / ratio_of_width_and_height_of_output
                - height_decalage_of_map_by_screen * 2,
            ),
        )

    return (
        pygame.transform.rotate(
            scaled_output_surface,
            0,
        ),
        screen.get_width() / output_surface.get_width(),
    )


MAP_SURFACE_CONSTANT, ratio = generate_map_surface()
MAP_SURFACE_CONSTANT: pygame.Surface


def get_tile_below_mouse():
    return (
        math.floor(pygame.mouse.get_pos()[0] / (tile_size * ratio)),
        math.floor(pygame.mouse.get_pos()[1] / (tile_size * ratio)),
    )


while running:

    murs_rendered = []

    number_of_tile_rendered = 0

    width_of_screen_in_tile, height_of_screen_in_tile = (
        set_width_and_height_of_screen_in_tiles()
    )
    tiles_at_screen = get_tiles_at_screen()

    for tile_position in tiles_at_screen:

        murs_rendered += get_murs_of_coordinate(
            tile_position
        )  # += used to merge the two lists insted of adding a list in a list with append

    draw_all_wall(murs_rendered)

    if pygame.mouse.get_focused():
        print(get_tile_by_coordinate(get_tile_below_mouse()))
        get_tile_by_coordinate(get_tile_below_mouse()).highlight()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP and event.key in pressed_key:
            pressed_key.pop(pressed_key.index(pygame.key.name(event.key)))

    pygame.display.flip()
    screen.fill("black")
    clock.tick_busy_loop(max_fps)
