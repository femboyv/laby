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

    print(output)


convert_script_to_world(script)
