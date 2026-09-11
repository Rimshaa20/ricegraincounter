import os
import numpy as np
import cv2
from rice_counter import (load_image, resize_if_needed, preprocess, segment,
                          morphological_clean, separate_touching_grains)

d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_images")
name = "sample_separated_45_grains.jpg"
path = os.path.join(d, name)
with open(path, "rb") as f:
    data = f.read()

img = load_image(data)
img = resize_if_needed(img, 1500)
h, w = img.shape[:2]
print("size:", w, "x", h)
print("mean pixel:", img.mean())

gray = preprocess(img, __import__('rice_counter').RiceConfig())
binary = segment(gray, __import__('rice_counter').RiceConfig())
clean = morphological_clean(binary, __import__('rice_counter').RiceConfig())

print("binary white px:", np.count_nonzero(binary == 255), "/", binary.size)
print("clean white px:", np.count_nonzero(clean == 255), "/", clean.size)

markers = separate_touching_grains(clean, __import__('rice_counter').RiceConfig())
print("markers uniq:", np.unique(markers))

# save debug stages
for nm, arr in [("gray.jpg", gray), ("binary.jpg", binary), ("clean.jpg", clean),
                ("dist.jpg", None)]:
    if arr is not None:
        cv2.imwrite(os.path.join(d, "dbg_" + nm), arr)