import pygame
import random
import math
import json

pygame.init()
screen = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()
running = True
fps = 100


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
        self.max_speed = 5
        self.speed = pygame.math.Vector2(0, 0)

        self.tick_to_reach_max_speed = fps / 2
        self.tick_to_slow_down = fps / 5

        self.acceleration_per_tick = self.max_speed / self.tick_to_reach_max_speed
        self.deceleration_per_tick = self.max_speed / self.tick_to_slow_down

        self.height = 200
        self.width = 100

        self.set_collide_box_to_default()

        self.number_of_sprite = 5
        self.sprites = []
        for sprite_number in range(self.number_of_sprite + 1):
            self.sprites.append(
                pygame.image.load(
                    "character_frame\\pixil-frame-" + str(sprite_number) + ".png"
                )
            )
        self.sprite_to_render_number = 0  # tell what sprite is rendered
        self.time_per_sprite = 0.3
        self.tick_per_sprite = self.time_per_sprite * fps
        self.tick_since_change_of_sprite = 0

    def set_collide_box_to_default(self):
        self.collide_box = pygame.Rect(
            self.x - x_of_display - self.width / 2 + 1,
            self.y - y_of_display - self.height / 2 + 1,
            self.width - 2,
            self.height
            - 2,  # -2 and +1 to have a collide box slighly smaller than the player sprite
        )

    def draw_animation(
        self,
        sprites: list,
        sprite_to_render: int,
        angle: pygame.math.Vector2,
        x: float,
        y: float,
    ):
        sprite = sprites[sprite_to_render]
        if self.tick_since_change_of_sprite != self.tick_per_sprite:
            self.tick_since_change_of_sprite += 1

        elif self.sprite_to_render_number != self.number_of_sprite:
            self.sprite_to_render_number += 1
            self.tick_since_change_of_sprite = 0

        else:
            self.sprite_to_render_number = 0
            self.tick_since_change_of_sprite = 0

        self.x_relative, self.y_relative = get_coordinate_relative_to_screen(x, y)

        resized_sprite = pygame.transform.scale(
            pygame.transform.rotate(
                sprite,
                pygame.Vector2.as_polar(angle)[1] * -1 + 180,
            ),
            (self.width, self.height),
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
    def __init__(self, location: tuple, letter: str):
        self.loaded = False
        self.location = location
        self.letter = letter
        self.murs = None
        self.walls = None
        self.generated = False

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
        self.walls: tuple
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

        murs = []
        if self.walls == None:
            self.get_walls()
        for orientation in self.walls:

            match orientation:  # 0 is up and it's going counterclockwise (i think(i'm  actually pretty sure))
                case 0:
                    mur = pygame.Rect(
                        tile_size * self.location[0] - x_of_display,
                        tile_size * self.location[1] - y_of_display,
                        tile_size + wall_width,
                        wall_width,
                    )
                case 1:
                    mur = pygame.Rect(
                        tile_size * self.location[0] - x_of_display,
                        tile_size * self.location[1] - y_of_display,
                        wall_width,
                        tile_size + wall_width,
                    )
                case 2:
                    mur = pygame.Rect(
                        tile_size * (self.location[0]) - x_of_display,
                        tile_size * (self.location[1] + 1) - y_of_display,
                        tile_size + wall_width,
                        wall_width,
                    )
                case 3:
                    mur = pygame.Rect(
                        tile_size * (self.location[0] + 1) - x_of_display,
                        tile_size * (self.location[1]) - y_of_display,
                        wall_width,
                        tile_size + wall_width,
                    )
            murs.append(mur)
        self.murs = murs
        return murs

    ########### generating the wall at start ###########

    def get_neighbour_tiles(self):
        return (
            get_tile_by_coordinate((self.location[0], self.location[1] - 1)),
            get_tile_by_coordinate((self.location[0], self.location[1] + 1)),
            get_tile_by_coordinate((self.location[0] - 1, self.location[1])),
            get_tile_by_coordinate((self.location[0] + 1, self.location[1])),
        )

    def get_not_generated_neighbour_tiles(self):
        output = []
        tile_in_check: tile_class
        for tile_in_check in self.get_neighbour_tiles():
            if tile_in_check.generated:
                output.append(tile_in_check)

        return output

    def choose_random_valid_tile(self):
        not_generated_neighbour_tiles = self.get_not_generated_neighbour_tiles()
        not_generated_neighbour_tiles_length = (
            self.get_not_generated_neighbour_tiles().__len__()
        )

        if not_generated_neighbour_tiles_length == 0:
            return None

        elif not_generated_neighbour_tiles_length == 1:
            return not_generated_neighbour_tiles[0]

        else:
            return not_generated_neighbour_tiles[
                random.randint(0, not_generated_neighbour_tiles_length - 1)
            ]

    def destroy_wall(self, wall: int):

        list_self_walls = list(self.walls)

        if wall in self.get_walls():

            list_self_walls.remove(wall)

        self.walls = tuple(list_self_walls)

    def check_if_generated(self):  # don't use it, it's bad
        if self.generated == False:
            if self.letter == "f":  # f for null
                return False
            else:
                self.generated = True
                return True
        else:
            return True


# screen shit


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


# key things

key_map = dict(z="up", s="down", d="right", q="left")


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


def get_walls_by_tile(letter: str) -> tuple:
    try:
        return letter_to_walls[letter]
    except KeyError:
        return letter_to_walls["f"]  #  f for Null


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

    letter = get_tile_by_coordinate(tile_position)
    murs_of_tile = []

    walls_to_draw = letter.get_walls()

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

            return tile_class(coordinate, "f")  # "f" for blank

        if (  # when outside of the map
            coordinate[0] > world_width_in_tile - 1
            or coordinate[1] > world_height_in_tile - 1
        ):

            return tile_class(coordinate, "f")  # "f" for blank

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
        return tile_class(coordinate, "f")


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


def closest_to(number: float, first_number: float, second_number: float):
    if abs(number - first_number) == abs(number - second_number):
        return 0
    elif abs(number - first_number) < abs(number - second_number):
        return first_number
    else:
        return second_number


####### function for displaying map #######


def show_map():
    global normal_view
    global carte_view
    normal_view = False
    carte_view = True


def hide_carte():
    global normal_view
    global carte_view
    normal_view = True
    carte_view = False


padding_width_of_carte = 10
padding_height_of_carte = 10


def generate_carte_surface() -> pygame.Surface:
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
                - padding_width_of_carte * 2,
                screen.get_height() - padding_height_of_carte * 2,
            ),
        )
    else:
        scaled_output_surface = pygame.transform.scale(
            output_surface,
            (
                screen.get_width() - padding_width_of_carte * 2,
                screen.get_width() / ratio_of_width_and_height_of_output
                - padding_height_of_carte * 2,
            ),
        )

    return pygame.transform.rotate(
        scaled_output_surface,
        0,
    )


############    ############    ############


############ carte initialization ############
carte_surface = generate_carte_surface()
print(carte_surface.get_size())
normal_view = True
carte_view = False

############    ############    ############

murs_rendered = []  # important inalization


def debugging():
    central_tile = tile_class((0, 0), "z")

    for adjacent_tile in central_tile.get_neighbour_tiles():
        adjacent_tile.check_if_generated()

    get_tile_by_coordinate((0, 0)).destroy_wall(1)


debugging()
while running:
    if normal_view:

        murs_rendered = []

        number_of_tile_rendered = 0

        screen_follow_position(player.x, player.y, 0.75)

        tiles_at_screen = get_tiles_at_screen()
        for tile_position in tiles_at_screen:
            murs_rendered += get_tile_by_coordinate(
                tile_position
            ).get_murs()  # += used to merge the two lists insted of adding a list in a list with append
        draw_all_wall(murs_rendered)

        player.draw_animation(
            player.sprites,
            player.sprite_to_render_number,
            player.angle,
            player.x,
            player.y,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    show_map()
                else:
                    pressed_key.append(pygame.key.name(event.key))

            elif event.type == pygame.KEYUP and event.key != pygame.K_m:

                pressed_key.pop(pressed_key.index(pygame.key.name(event.key)))

        not_pressed_key = ["z", "q", "s", "d"]
        moved_this_tick = False
        for key in pressed_key:
            player.accelerate(key_mapping(key))
            if key in not_pressed_key:
                not_pressed_key.pop(not_pressed_key.index(key))

        for key in not_pressed_key:
            player.decelerate(key_mapping(key))

        if player.speed.x == 0:
            player.set_collide_box_to_default()
        else:
            player.collide_box.x = (
                player.x_relative
                + closest_to(
                    player.speed.x, player.max_speed * 2.1, -player.max_speed * 2.1
                )
                - (player.width / 2)
            ) + 1  # +1 because the collide box is slighly smaller than the player
            player.collide_box.y = player.y_relative - player.height / 2 + 1

            index_of_mur_colliding = player.collide_box.collidelist(murs_rendered)

            if index_of_mur_colliding == -1:
                player.x += player.speed.x

            else:
                player.speed.x = 0

                mur_colliding = murs_rendered[index_of_mur_colliding]
                mur_colliding: pygame.Rect

                if mur_colliding.x > player.x_relative:

                    player.x = mur_colliding.x + x_of_display - player.width / 2
                else:

                    player.x = (
                        mur_colliding.x
                        + x_of_display
                        + mur_colliding.width
                        + player.width / 2
                    )

        if player.speed.y == 0:
            player.set_collide_box_to_default()

        else:
            player.collide_box.x = player.x_relative - player.width / 2 + 1

            player.collide_box.y = (
                player.y_relative
                - (player.height / 2)
                + closest_to(
                    player.speed.y, player.max_speed * 2.1, -player.max_speed * 2.1
                )
                + 1
            )  # +1 because the collide box is slighly smaller than the player

            index_of_mur_colliding = player.collide_box.collidelist(murs_rendered)

            if index_of_mur_colliding == -1:
                player.y += player.speed.y
            else:
                player.speed.y = 0

                mur_colliding = murs_rendered[index_of_mur_colliding]
                mur_colliding: pygame.Rect

                if mur_colliding.y > player.y_relative:

                    player.y = mur_colliding.y + y_of_display - player.height / 2
                else:

                    player.y = (
                        (mur_colliding.y + y_of_display)
                        + mur_colliding.height
                        + player.height / 2
                    )

    if carte_view:
        pygame.Surface.blit(
            screen,
            carte_surface,
            (padding_width_of_carte, padding_height_of_carte),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    hide_carte()
                else:
                    pressed_key.append(pygame.key.name(event.key))

            elif event.type == pygame.KEYUP and event.key != pygame.K_m:
                pressed_key.pop(pressed_key.index(pygame.key.name(event.key)))

    pygame.display.flip()
    screen.fill("black")
    clock.tick_busy_loop(fps)

"""
bug report:


padding a little heigh for collision between player and wall


"""
