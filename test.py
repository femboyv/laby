import math

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


def letter_to_all_data(letter: str):
    return letter


def print_to_file(content):
    with open("actual_map.txt", "w") as file:
        file.write(str(content))


output = []
world_width = 18
"i________k____k__iim___im_hik__lii_o"
for i, letter in enumerate(
    """
    im_________u_____l
    ik_________k____li
    iim______liim___hi
    ish_____liiiid__oi
    p_j____lipoip__u_o
    m_____lip__hm__hml
    im____ok___himliii
    ipu____om__oiiiiii
    
    """
):
    print()
    output.append(
        (
            (i % world_width, math.floor(i / (world_width))),
            letter_to_all_data(letter),
        )
    )

print(output)
print_to_file(output)
