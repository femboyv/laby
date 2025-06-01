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
    return (letter, letter_to_walls[letter])


output = []
world_width = 18

for i, letter in enumerate("i________k____k__iim___im_hik__lii_o"):
    print()
    output.append(
        (
            (math.floor(i / (world_width / 2)), int(i % (world_width / 2) + i % 2)),
            letter_to_all_data(letter),
        )
    )

print(output)
