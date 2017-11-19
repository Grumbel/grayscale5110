#!/usr/bin/env python3

import sys
import random
import itertools
from PIL import Image

img = Image.open("pic2.png")

def make_thresholds(n):
    t = [i * 255 // (n+1) for i in range(1, (n+1))]
    result = []
    for i in range(n):
        result.append(t)
        t = [t[-1]] + t[0:-1]
    return result


lst = []
thresholdss = make_thresholds(12)
for thresholds in thresholdss:
    for x in range(0, 84):
        for y in range(0, 6):
            value = 0
            for b in range(0, 8):
                p = img.getpixel((x, y * 8 + b))
                threshold = thresholds[(b*3+x*5) % len(thresholdss)]
                value |= (1 if (p > threshold) else 0) << b
            lst.append(value)


sys.stderr.write("{}\n".format(len(bytes(lst))))
sys.stdout.buffer.write(bytes(lst))


# EOF #
