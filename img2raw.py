#!/usr/bin/env python3

# Image to Raw Bitmap Data Converter
# Copyright (C) 2017 Ingo Ruhnke <grumbel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
import sys
import random
import itertools
import argparse
import random
import numpy
import math
from PIL import Image


def quantize(img, levels, floydsteinberg):
    """Takes a grayscale image and reduces it's number of colors to
    'levels'. Resulting pixel are in [0, levels), not [0, 256)."""
    q = 255 / levels

    pixels = numpy.zeros([img.size[0] + 2, img.size[1] + 2])
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            p = img.getpixel((x, y))
            pixels[x+1][y+1] = p

    for y in range(1, pixels.shape[1] - 1):
        for x in range(1, pixels.shape[0] - 1):
            oldpixel = pixels[x, y]
            newpixel = math.floor(oldpixel / q)
            pixels[x][y] = newpixel
            if floydsteinberg:
                quant_error = oldpixel - (newpixel * q)
                pixels[x+1][y  ] += quant_error * 7/16
                pixels[x-1][y+1] += quant_error * 3/16
                pixels[x  ][y+1] += quant_error * 5/16
                pixels[x+1][y+1] += quant_error * 1/16

    out = Image.new("L", img.size)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            p = pixels[x+1][y+1]
            out.putpixel((x, y), int(p))

    return out


def img2data(img, levels, dither, magic):
    img = quantize(img, levels, floydsteinberg=dither)

    levels = levels - 1

    zipdata = []
    for y in range(0, 48):
        for x in range(0, 84):
            p = img.getpixel((x, y))
            zipdata.append(([0] * (levels - p)) + ([1] * p))

    data = []
    for l in range(levels):
        for x in range(0, 84):
            for y in range(0, 6):
                v = 0
                for b in range(0, 8):
                    p = zipdata[((y*8+b) * 84) + x]
                    v |= (p[int(magic[0] * x + magic[1] * (y*8+b) + l) % levels]) << b

                    # Moire pattern
                    # v |= (p[int(x * (y*8+b) + l) % levels]) << b

                    # v |= (p[(x*5 + 3*(y*8+b)*48 + l) % levels]) << b
                data.append(v)
    return data


def img2grayscale(img, rotate):
    if img.size != (84, 48):
        w, h = img.size
        if w > h: # landscape
            nh = int(w * 55 / 84)
            img = img.crop((0, (h - nh) // 2, w, nh + (h - nh) // 2))
        else: # portrait
            nw = int(h * (84 / 55))
            img = img.crop(((w - nw) // 2, 0, nw + (w - nw) // 2, h))

        img = img.resize((84, 48), resample=Image.LANCZOS)

    img = img.rotate(rotate, expand=False)

    return img.convert("L")


def MagicValue(text):
    m = re.match(r"(\d+),(\d+)", text)
    if m is None:
        raise argparse.ArgumentTypeError("invalid format for --magic: '{}', expected \"X,Y\"".format(args.format))
    else:
        return (int(m.group(1)), int(m.group(2)))

def parse_args():
    parser = argparse.ArgumentParser(description='Convert image to raw bitmap data')
    parser.add_argument('FILE', action='store', type=str, nargs=1,
                        help='image file to load')
    parser.add_argument('-l', '--levels', metavar="NUM", type=int, default=16,
                        help='Number of levels of grayscale to use')
    parser.add_argument('-f', '--format', metavar="FMT", type=str, default="raw",
                        help='Output format (raw, C)')
    parser.add_argument('-r', '--rotate', metavar="ANGLE", type=int, default=0,
                        help='Rotate output by ANGLE')
    parser.add_argument('-d', '--dither', action='store_true', default=False,
                        help='Use Floyd-Steinberg dithering')
    parser.add_argument('-m', '--magic', metavar="X,Y", type=MagicValue, default=None,
                        help='Magic values to determine the flicker pattern')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.magic is None:
        if args.levels > 9:
            magic = (5, 3)
        else:
            magic = (1, 1)
    else:
        magic = args.magic

    img = Image.open(args.FILE[0])
    img = img2grayscale(img, args.rotate)

    data = img2data(img, args.levels, args.dither, magic)

    if args.format == "raw":
        sys.stdout.buffer.write(bytes(data))
    elif args.format == "C" or args.format == "c":
        print("byte bitmap[] =")
        print("{")
        print(", ".join(["0x{:02x}".format(v) for v in data]))
        print("};")
    else:
        raise argparse.ArgumentTypeError("invalid format '{}'".format(args.format))


if __name__ == "__main__":
    main()


# EOF #
