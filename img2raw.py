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


import sys
import random
import itertools
import argparse
import random
from PIL import Image


def make_thresholds(n):
    return [i * 255 // (n+1) for i in range(1, (n+1))]


def img2data(img, levels):
    data = []
    thresholds = make_thresholds(levels - 1)

    zipdata = []
    imgs = []
    for threshold in thresholds:
        out = Image.new("L", size=img.size)
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                p = img.getpixel((x, y))
                out.putpixel((x, y), p - 128 + threshold)
        out = out.convert(mode="1", dither=Image.NONE) # FLOYDSTEINBERG)
        imgs.append(out)

    for y in range(0, 48):
        for x in range(0, 84):
            zipdata.append([0 if out.getpixel((x, y)) <= 128 else 1
                            for out in imgs])

    data = []
    for t in range(len(thresholds)):
        for x in range(0, 84):
            for y in range(0, 6):
                p = 0
                for b in range(0, 8):
                    p |= (zipdata[((y*8+b) * 84) + x][(x*5 + 3*(y*8+b)*48 + t) % len(thresholds)]) << b
                    # p |= (zipdata[((y*8+b) * 84) + x][(x*0 + 0*(y*8+b)*48 + t) % len(thresholds)]) << b
                data.append(p)
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
    return parser.parse_args()


def main():
    args = parse_args()

    img = Image.open(args.FILE[0])
    img = img2grayscale(img, args.rotate)
    data = img2data(img, args.levels)

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
