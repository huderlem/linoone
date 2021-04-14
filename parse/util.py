#--------------------------------------------------------------------
# linoone: util.py
#
# Provides misc. data parsing functionality for the decomp project
# files.
#--------------------------------------------------------------------

def parse_jasc_file(filepath):
    """
    Parses a JASC palette file into a flat list of RGB colors.
    Returns None if there is any issue parsing the file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 3 or lines[0].strip() != "JASC-PAL" or lines[1].strip() != "0100":
        print('Invalid JASC palette file: %s' % filepath)
        return None

    num_colors = int(lines[2])
    if len(lines) < num_colors + 3:
        print('Invalid JASC palette file: %s' % filepath)
        return None

    palette = []
    for line in lines[3:]:
        pixel = line.strip().split(" ")
        if len(pixel) != 3:
            print('Invalid JASC palette file: %s' % filepath)
            return None

        palette.append(int(pixel[0].strip()))
        palette.append(int(pixel[1].strip()))
        palette.append(int(pixel[2].strip()))

    return palette
