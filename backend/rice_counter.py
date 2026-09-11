"""
Rice Grain Counter - Image Processing Module

This module contains the computer vision pipeline for detecting and counting
individual rice grains in uploaded images.

Algorithm Overview:
1. Load and optionally resize the image
2. Convert to grayscale
3. Apply noise reduction (Gaussian blur + bilateral filter)
4. Apply adaptive thresholding for segmentation
5. Morphological operations to clean up the binary mask
6. Use distance transform + watershed to separate touching grains
7. Find contours and filter by area, aspect ratio, and shape
8. Draw annotations and return results

All thresholds are configurable for different rice varieties.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class RiceConfig:
    """Configuration for rice grain detection thresholds."""
    max_image_dim: int = 1500
    gaussian_kernel: Tuple[int, int] = (5, 5)
    gaussian_sigma: float = 0
    bilateral_d: int = 9
    bilateral_sigma_color: float = 75
    bilateral_sigma_space: float = 75
    adaptive_block_size: int = 25
    adaptive_c: int = 10
    morph_kernel_size: Tuple[int, int] = (3, 3)
    morph_iterations_open: int = 2
    morph_iterations_close: int = 2
    min_grain_area: int = 150
    max_grain_area: int = 8000
    min_aspect_ratio: float = 1.2
    max_aspect_ratio: float = 8.0
    min_solidity: float = 0.4
    distance_thresh_ratio: float = 0.45
    watershed_dilate_iter: int = 3
    color_label: Tuple[int, int, int] = (0, 200, 255)  # BGR - warm orange
    color_contour: Tuple[int, int, int] = (0, 180, 0)   # BGR - green
    font_scale: float = 0.35
    font_thickness: int = 1


DEFAULT_CONFIG = RiceConfig()


def load_image(image_bytes: bytes) -> np.ndarray:
    """Decode image bytes into an OpenCV numpy array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. File may be corrupted or unsupported.")
    return img


def resize_if_needed(img: np.ndarray, max_dim: int) -> np.ndarray:
    """Resize image if either dimension exceeds max_dim, preserving aspect ratio."""
    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return img
    scale = max_dim / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def preprocess(img: np.ndarray, cfg: RiceConfig) -> np.ndarray:
    """Convert to grayscale and apply noise reduction."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Gaussian blur to reduce high-frequency noise
    blurred = cv2.GaussianBlur(gray, cfg.gaussian_kernel, cfg.gaussian_sigma)
    # Bilateral filter preserves edges while smoothing flat regions
    filtered = cv2.bilateralFilter(blurred, cfg.bilateral_d,
                                   cfg.bilateral_sigma_color, cfg.bilateral_sigma_space)
    return filtered


def segment(gray: np.ndarray, cfg: RiceConfig) -> np.ndarray:
    """Apply adaptive thresholding to create a binary mask of rice grains."""
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        cfg.adaptive_block_size,
        cfg.adaptive_c
    )
    return binary


def morphological_clean(binary: np.ndarray, cfg: RiceConfig) -> np.ndarray:
    """Apply morphological opening then closing to remove noise and fill holes."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, cfg.morph_kernel_size)
    # Opening: remove small noise blobs
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel,
                               iterations=cfg.morph_iterations_open)
    # Closing: fill small holes inside grains
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel,
                               iterations=cfg.morph_iterations_close)
    return cleaned


def separate_touching_grains(mask: np.ndarray, cfg: RiceConfig) -> np.ndarray:
    """
    Use distance transform + watershed to separate grains that touch each other.

    Steps:
    1. Compute distance transform of the binary mask
    2. Find foreground peaks using a threshold on the distance map
    3. Use these as seeds for watershed segmentation
    4. Return a label mask where each grain has a unique label
    """
    # Distance transform: each pixel gets its distance to the nearest background pixel
    dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    dist_norm = cv2.normalize(dist_transform, None, 0, 1.0, cv2.NORM_MINMAX)

    # Threshold the distance map to find definite foreground regions (grain centers)
    _, sure_fg = cv2.threshold(dist_norm, cfg.distance_thresh_ratio, 255, cv2.THRESH_BINARY)
    sure_fg = sure_fg.astype(np.uint8)

    # Dilate the mask to get the "unknown" border region
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    sure_bg = cv2.dilate(mask, kernel, iterations=cfg.watershed_dilate_iter)

    # Unknown region = sure background minus sure foreground
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Label markers for watershed
    num_labels, markers = cv2.connectedComponents(sure_fg)
    # Watershed requires markers to start from 1 (not 0)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Apply watershed
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    markers = cv2.watershed(mask_3ch, markers)

    return markers


def filter_grains(markers: np.ndarray, mask: np.ndarray, cfg: RiceConfig) -> List[dict]:
    """
    Filter detected grain regions by area, aspect ratio, and solidity.

    Returns a list of dicts with keys: contour, area, bbox, center, label_id
    """
    unique_labels = np.unique(markers)
    # Label -1 is the watershed boundary, label 1 is background
    candidates = []
    for label_id in unique_labels:
        if label_id <= 1:
            continue

        grain_mask = np.uint8(markers == label_id) * 255

        # Only consider grains that overlap with the original binary mask
        grain_mask = cv2.bitwise_and(grain_mask, mask)
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        # Take the largest contour in this label region
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)

        if area < cfg.min_grain_area or area > cfg.max_grain_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = max(w, h) / max(min(w, h), 1)

        if aspect_ratio > cfg.max_aspect_ratio or aspect_ratio < cfg.min_aspect_ratio:
            continue

        # Solidity = contour area / convex hull area (filters concave junk)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = area / max(hull_area, 1)
        if solidity < cfg.min_solidity:
            continue

        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = x + w // 2, y + h // 2

        candidates.append({
            "contour": cnt,
            "area": area,
            "bbox": (x, y, w, h),
            "center": (cx, cy),
            "label_id": int(label_id),
        })

    return candidates


def draw_annotations(img: np.ndarray, grains: List[dict], cfg: RiceConfig) -> np.ndarray:
    """Draw numbered contours and bounding boxes on the annotated image."""
    annotated = img.copy()
    for i, grain in enumerate(grains):
        num = i + 1
        # Draw contour outline
        cv2.drawContours(annotated, [grain["contour"]], -1, cfg.color_contour, 2)
        # Draw a small circle at the grain center
        cx, cy = grain["center"]
        cv2.circle(annotated, (cx, cy), 3, cfg.color_label, -1)
        # Draw the grain number near the center
        text = str(num)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX,
                                       cfg.font_scale, cfg.font_thickness)
        tx = cx - tw // 2
        ty = cy - th // 2
        # White background for readability
        cv2.rectangle(annotated, (tx - 1, ty - th - 1), (tx + tw + 1, ty + 3),
                      (255, 255, 255), -1)
        cv2.putText(annotated, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                    cfg.font_scale, (0, 0, 200), cfg.font_thickness, cv2.LINE_AA)

    return annotated


def count_rice_grains(image_bytes: bytes, config: RiceConfig = None) -> dict:
    """
    Main pipeline: takes raw image bytes, returns grain count + annotated image.

    Returns dict with keys:
        total_count: int
        annotated_image_bytes: bytes (JPEG encoded)
        message: str
    """
    cfg = config or DEFAULT_CONFIG

    # 1. Decode image
    img = load_image(image_bytes)
    original = img.copy()

    # 2. Resize for consistency and performance
    img = resize_if_needed(img, cfg.max_image_dim)

    # 3. Preprocess: grayscale + noise reduction
    gray = preprocess(img, cfg)

    # 4. Segment: adaptive threshold
    binary = segment(gray, cfg)

    # 5. Clean up with morphological operations
    cleaned = morphological_clean(binary, cfg)

    # 6. Separate touching grains
    markers = separate_touching_grains(cleaned, cfg)

    # 7. Filter detections by shape/size constraints
    grains = filter_grains(markers, cleaned, cfg)

    # 8. Draw annotations on a copy of the (resized) image
    annotated = draw_annotations(img, grains, cfg)

    count = len(grains)

    # Encode the annotated image to JPEG bytes for sending to frontend
    _, buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
    annotated_bytes = buf.tobytes()

    msg = f"{count} rice grain{'s' if count != 1 else ''} detected"

    return {
        "total_count": count,
        "annotated_image_bytes": annotated_bytes,
        "message": msg,
    }
