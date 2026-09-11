"""
Generate sample test images of rice grains for testing the Rice Grain Counter.

The script draws synthetic rice-like grains (elongated ellipses with soft edges)
on a dark background, producing realistic-feeling images which the counting
pipeline can detect.

Usage:
    python generate_sample.py

Outputs to the "sample_images" directory.
"""

import os

import cv2
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_images")


def make_grain(center, length, thickness, angle_deg):
    """Create a rotated rectangle as the grain "polygon"."""
    box = cv2.boxPoints(((float(center[0]), float(center[1])), (float(length), float(thickness)), float(angle_deg)))
    box = np.int32(box)
    return box


def render_rice_image(size=(900, 1200), bg_color=(40, 35, 30), num_grains=80, overlap=False):
    """Render an image with randomly placed synthetic rice grains."""
    h, w = size
    img = np.full((h, w, 3), bg_color, dtype=np.uint8)

    length = 70
    thickness = 16
    places = np.zeros((h, w), dtype=np.uint8)

    margin = length
    i = 0
    attempts = 0
    count = 0
    while count < num_grains and attempts < num_grains * 50:
        attempts += 1
        cx = np.random.randint(margin, w - margin)
        cy = np.random.randint(margin, h - margin)
        angle = np.random.randint(0, 180)

        box = make_grain((cx, cy), length, thickness, angle)
        center_x = int(np.mean(box[:, 0]))
        center_y = int(np.mean(box[:, 1]))

        # Check spacing to avoid overlapping grains (unless requested)
        bad = False
        if not overlap:
            probe = cv2.fillPoly(np.zeros((h, w), dtype=np.uint8), [box], 1)
            if cv2.countNonZero(cv2.bitwise_and(probe, places)) > 0:
                bad = True
        if bad:
            continue

        grain_mask = cv2.fillPoly(np.zeros((h, w), dtype=np.uint8), [box], 1)

        # Give the grain a rice-like bright color with slight gradient
        color = (230, 228, 220)
        # Copy a soft-edged version
        soft = cv2.GaussianBlur(grain_mask.astype(np.float32), (0, 0), 4)
        soft = cv2.normalize(soft, None, 0, 1, cv2.NORM_MINMAX)
        bright = np.where(soft > 0.3)[0]
        # Paint the grain with a gradient toward the center
        for ratio, col in [(1.0, (200, 198, 190)), (0.85, (235, 233, 225))]:
            mask_f = (soft * ratio).astype(np.uint8)
            grain_masked = cv2.fillPoly(np.zeros((h, w, 3), dtype=np.uint8), [box], col)
            img = np.where(mask_f[:, :, None] > 0, grain_masked, img)

        places = cv2.bitwise_or(places, grain_mask)
        count += 1

    return img


def render_separated_clean():
    """Clean separated grains on a light background."""
    img = np.full((900, 1200, 3), (248, 246, 240), dtype=np.uint8)
    rng = np.random.default_rng(7)
    length, thickness = 60, 15
    margin = 100
    positions = []
    while len(positions) < 45:
        cx = rng.integers(margin, 1200 - margin)
        cy = rng.integers(margin, 900 - margin)
        pos = (cx, cy)
        ok = True
        for p in positions:
            if abs(p[0] - cx) < 90 and abs(p[1] - cy) < 60:
                ok = False
                break
        if ok:
            positions.append(pos)
    for cx, cy in positions:
        angle = int(rng.integers(0, 180))
        box = cv2.boxPoints(((float(cx), float(cy)), (float(length), float(thickness)), float(angle)))
        box = np.int32(box)
        shade = int(rng.integers(190, 225))
        cv2.fillPoly(img, [box], (shade, shade, shade))  # light grayish rice
        # soft shading
        if rng.random() > 0.5:
            inner = cv2.boxPoints(((float(cx), float(cy)), (length * 0.6, thickness * 0.6), float(angle)))
            cv2.fillPoly(img, [np.int32(inner)], (225, 224, 220))

    # slight blur for realism
    img = cv2.GaussianBlur(img, (0, 0), 1.5)
    return img


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Sample images will be saved to: {os.path.abspath(OUTPUT_DIR)}")

    images = {
        "sample_separated_45_grains.jpg": (render_separated_clean(), True),
        "sample_dark_80_grains.jpg": (render_rice_image(num_grains=80, overlap=False), True),
        "sample_overlapping_120_grains.jpg": (render_rice_image(num_grains=120, overlap=True), False),
    }

    for name, (img, _) in images.items():
        path = os.path.join(OUTPUT_DIR, name)
        cv2.imwrite(path, img)
        print(f"  OK {name}")


if __name__ == "__main__":
    main()