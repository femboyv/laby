import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()
running = True
max_fps = 100


background_sprite = pygame.image.load("d011d6bc1effc67ae5c74bbc5ce090c2.jpg")
cat_sprite = pygame.image.load("cattt.jpg")
pressed_key = []


x_of_display = 0
y_of_display = 0


class player_class:
    def __init__(self):
        self.x = 125
        self.y = 125

        self.angle = pygame.math.Vector2(-1, 0)
        self.max_speed = 7.5
        self.speed = pygame.math.Vector2(0, 0)

        self.tick_to_reach_max_speed = max_fps / 2
        self.tick_to_slow_down = max_fps / 5

        self.acceleration_per_tick = self.max_speed / self.tick_to_reach_max_speed
        self.deceleration_per_tick = self.max_speed / self.tick_to_slow_down

        self.height = 100

        self.collide_box = pygame.Rect(
            self.x + screen.get_width() / 2 - self.height / 2,
            self.y + screen.get_height() / 2 - self.height / 2,
            self.height,
            self.height,
        )

        self.sprite = pygame.transform.scale(
            pygame.image.load("cattt.jpg"),
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
                self.speed.x += self.acceleration_per_tick
            case "left":
                self.speed.x -= self.acceleration_per_tick
            case "down":
                self.speed.y += self.acceleration_per_tick
            case "up":
                self.speed.y -= self.acceleration_per_tick
        if self.speed != pygame.Vector2(0, 0):  # otherwise clamp raise an error
            self.speed = self.speed.clamp_magnitude(0, self.max_speed)
        moved_this_tick = True

    def decelerate(self, direction: str):
        if self.speed.length() < self.deceleration_per_tick and not moved_this_tick:
            self.speed = pygame.Vector2(0, 0)
        if abs(self.speed.x) < (
            self.deceleration_per_tick / 5
        ):  # the divider is twikeable (but 5 is good)
            self.speed.x = 0
        if abs(self.speed.y) < (
            self.deceleration_per_tick / 5
        ):  # the divider is twikeable (but 5 is good)
            self.speed.y = 0

        match direction:
            case "right":
                if self.speed.x > 0:

                    self.speed.x -= self.deceleration_per_tick
            case "left":
                if self.speed.x < 0:

                    self.speed.x += self.deceleration_per_tick
            case "down":
                if self.speed.y > 0:

                    self.speed.y -= self.deceleration_per_tick
            case "up":
                if self.speed.y < 0:

                    self.speed.y += self.deceleration_per_tick


class tile_class:
    def __init___(self, location: tuple, letter: str):
        self.location = location
        self.letter = letter
        self.murs = None
        self.walls = None

    def get_walls(self) -> tuple:
        if self.walls != None:
            return self.walls
        else:
            try:
                self.walls = letter_to_walls[self.letter]
                return letter_to_walls[self.letter]
            except KeyError:
                self.walls = letter_to_walls["f"]
                return letter_to_walls["f"]  #  f for Null

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
                murs.append(rect_to_draw)
            self.murs = murs
            return murs


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


key_map = dict(z="up", s="down", d="right", q="left")


def key_mapping(key: str):
    return key_map[key]


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


def get_walls_by_tile(letter: str) -> tuple:
    try:
        return letter_to_walls[letter]
    except KeyError:
        return letter_to_walls["f"]  #  f for Null


tile_size = 200
wall_width = 20


def read_map_file():
    with open("actual_map.txt") as file:
        return file.read()


scripted_map = read_map_file()


def generate_map(script=None, width=50, height=50):

    if script != None:
        world_width_in_tile, world_height_in_tile = (
            check_for_max_width_and_height_of_map(script)
        )
        return (script, world_width_in_tile, world_height_in_tile)

    else:

        wall_map = []

        position = (0, 0)

        for _ in range(height):  # height
            for _ in range(width):  # width
                wall_map.append((position, generate_random_tile()))
                position = (position[0] + 1, position[1])

            position = (0, position[1] + 1)

        return (wall_map, width, height)


def generate_random_tile():
    possibility = "ujhk_if"  # only tile with 2 walls or less
    return possibility[random.randrange(possibility.__len__())]


def check_for_max_width_and_height_of_map(map) -> tuple[int, int]:
    return (map[len(map) - 1][0][0] + 1, map[len(map) - 1][0][1])


tile_map, world_width_in_tile, world_height_in_tile = generate_map(
    scripted_map,
    18,
    3,
)

print(world_width_in_tile, world_height_in_tile)


print(tile_map)


def get_murs_of_coordinate(tile_position: tuple):

    global number_of_tile_rendered
    letter = get_tile_by_coordinate(tile_position)

    murs_of_tile = []

    walls_to_draw = get_walls_by_tile(letter)

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
            tile_and_position = tile_map[coordinate_in_map]
        except IndexError:
            return "f"  # "f" for blank

        if (  # when outside of the map
            coordinate[0] > world_width_in_tile - 1
            or coordinate[1] > world_height_in_tile - 1
        ):
            return "f"  # "f" for blank

        if tile_and_position[0] != coordinate:
            raise ValueError(
                "the coordinate of the output (%d,%d) weren't the coordinate of the input (%d,%d)"
                % (
                    tile_map[coordinate_in_map][0][0],
                    tile_map[coordinate_in_map][0][1],
                    coordinate[0],
                    coordinate[1],
                )
            )

        return tile_and_position[1]


def get_all_point_in_rect(position_start: tuple, position_end: tuple):
    # could add position_end[1]+1 to include the point on the edge or not
    all_point = []
    for y in range(position_start[1], position_end[1]):
        for x in range(position_start[0], position_end[0]):
            all_point.append((x, y))
    return all_point


width_of_screen_in_tile = math.ceil(screen.get_width() / tile_size) + 1
height_of_screen_in_tile = math.ceil(screen.get_height() / tile_size) + 1


def get_tiles_at_screen():
    x_of_display_in_tile = math.floor(x_of_display / tile_size)
    y_of_display_in_tile = math.floor(y_of_display / tile_size)

    return get_all_point_in_rect(
        (x_of_display_in_tile, y_of_display_in_tile),
        (
            width_of_screen_in_tile + x_of_display_in_tile,
            height_of_screen_in_tile + y_of_display_in_tile,
        ),
    )


def draw_all_wall(walls_to_draw: list):
    for wall in walls_to_draw:
        pygame.draw.rect(screen, "white", wall)


player = player_class()


def set_tile_in_map(position: tuple, tile: tuple):
    position_in_map = int(position[0] * position[1] / 2)
    tile_map[position_in_map] = (position, tile)


murs_rendered = []


def closest_to(number: float, first_number: float, second_number: float):
    if abs(number - first_number) == abs(number - second_number):
        return 0
    elif abs(number - first_number) < abs(number - second_number):
        return first_number
    else:
        return second_number


def show_map():
    global normal_view
    global map_view
    normal_view = False
    map_view = True


def hide_map():
    global normal_view
    global map_view
    normal_view = True
    map_view = False


def define_map_surface() -> pygame.Surface:
    output_surface = pygame.Surface(
        (world_width_in_tile * tile_size, world_height_in_tile * tile_size)
    )
    all_murs = []
    for tile in tile_map:
        for wall in get_walls_by_tile(tile[1]):
            all_murs.append(get_mur_from_wall(tile[0], wall))
            pygame.draw.rect(output_surface, "white", get_mur_from_wall(tile[0], wall))

    return pygame.transform.rotate(
        pygame.transform.scale(
            output_surface,
            (
                pygame.math.clamp(
                    min(screen.get_width(), screen.get_height())
                    * (world_width_in_tile / world_height_in_tile),
                    0,
                    min(screen.get_width(), screen.get_height()),
                ),
                pygame.math.clamp(
                    min(screen.get_width(), screen.get_height())
                    * (world_height_in_tile / world_width_in_tile),
                    0,
                    min(screen.get_width(), screen.get_height()),
                ),
            ),
        ),
        0,
    )


map_surface = define_map_surface()

normal_view = True
map_view = False

while running:
    if normal_view:
        murs_rendered = []

        number_of_tile_rendered = 0

        tiles_at_screen = get_tiles_at_screen()
        for tile_position in tiles_at_screen:

            murs_rendered += get_murs_of_coordinate(
                tile_position
            )  # += used to merge the two lists insted of adding a list in a list with append

        draw_all_wall(murs_rendered)

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
                if event.key == pygame.K_m:
                    show_map()
                else:
                    pressed_key.append(pygame.key.name(event.key))

            if event.type == pygame.KEYUP and event.key != pygame.K_m:

                pressed_key.pop(pressed_key.index(pygame.key.name(event.key)))

        not_pressed_key = ["z", "q", "s", "d"]
        moved_this_tick = False
        for key in pressed_key:
            player.accelerate(key_mapping(key))
            not_pressed_key.pop(not_pressed_key.index(key))

        for key in not_pressed_key:
            player.decelerate(key_mapping(key))

        if player.speed.x != 0:

            player.collide_box.x = (
                player.x_relative
                + closest_to(player.speed.x, player.max_speed, -player.max_speed)
                - player.height / 2
            )
            player.collide_box.y = (
                player.y_relative
                - player.height / 2
                + closest_to(player.speed.x, player.max_speed, -player.max_speed)
            )

            if player.collide_box.collidelist(murs_rendered) == -1:
                player.x += player.speed.x
            else:
                player.speed.x = 0

        if player.speed.y != 0:

            player.collide_box.x = (
                player.x_relative
                + closest_to(player.speed.x, player.max_speed, -player.max_speed)
                - player.height / 2
            )
            player.collide_box.y = (
                player.y_relative
                - player.height / 2
                + closest_to(player.speed.x, player.max_speed, -player.max_speed)
            )

            if player.collide_box.collidelist(murs_rendered) == -1:
                player.y += player.speed.y
            else:
                player.speed.y = 0

    if map_view:
        pygame.Surface.blit(screen, map_surface, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                hide_map()

    pygame.display.flip()
    screen.fill("black")
    clock.tick_busy_loop(max_fps)

"""
bug report:
reading the file need json load but idk syntax
bug at map showing only part of the screen
bug at map when holding key and pressing map key
bug at collision for vertical collision


"""
