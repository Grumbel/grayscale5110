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


def zzip(lst):
    p = len(lst) // 2
    l1 = lst[0:p]
    l2 = reversed(lst[p:])
    result = []
    for z in itertools.zip_longest(l1, l2):
        if z[0] is not None: result.append(z[0])
        if z[1] is not None: result.append(z[1])
    return result


def make_thresholds(n):
    t = [i * 255 // (n+1) for i in range(1, (n+1))]
    result = []
    for i in range(n):
        result.append(t)
        t = [t[-1]] + t[0:-1]

    result = [zzip(r) for r in result]
    return result


def img2data(img, levels):
    data = []
    thresholdss = make_thresholds(levels - 1)
    # random.shuffle(thresholdss)
    for thresholds in thresholdss:
        for x in range(0, 84):
            for y in range(0, 6):
                value = 0
                for b in range(0, 8):
                    p = img.getpixel((x, y * 8 + b))
                    threshold = thresholds[((y * 8 + b)*2 + x*3) % len(thresholds)] # [(b*1+x*4) % len(thresholdss)]
                    # threshold = thresholds[random.randint(0, len(thresholdss)-1)]
                    value |= (1 if (p > threshold) else 0) << b
                data.append(value)
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
    parser.add_argument('-l', '--levels', metavar="NUM", type=int, default=12,
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
