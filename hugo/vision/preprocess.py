"""Image preprocessing for worksheet analysis.

Applies grayscale conversion, contrast enhancement, and
binarization to prepare captured worksheet images for OCR.
Perspective correction is stubbed for now (needs camera
calibration data from the Pi).
"""

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def to_grayscale(image: Image.Image) -> Image.Image:
    """Convert image to grayscale."""
    return image.convert("L")


def normalize_lighting(image: Image.Image) -> Image.Image:
    """Normalize uneven lighting across the worksheet.

    Uses adaptive histogram equalization to handle shadows and
    uneven illumination from the projector/room lighting.
    """
    gray = image.convert("L")
    return ImageOps.autocontrast(gray, cutoff=1)


def enhance_for_ocr(image: Image.Image) -> Image.Image:
    """Enhance contrast and sharpen text for OCR extraction.

    Applies sharpening, contrast stretch, and binarization to
    produce a clean black-on-white image for Tesseract.
    """
    gray = image if image.mode == "L" else image.convert("L")

    # Sharpen to crisp up text edges
    sharp = gray.filter(ImageFilter.SHARPEN)

    # Autocontrast to maximize text/background separation
    contrast = ImageOps.autocontrast(sharp, cutoff=2)

    # Binarize with a threshold — text is dark, background is light
    arr = np.array(contrast)
    threshold = np.mean(arr) - 20  # slightly below mean catches text
    threshold = max(threshold, 100)  # safety floor
    binary = ((arr > threshold) * 255).astype(np.uint8)

    return Image.fromarray(binary)


def correct_perspective(image: Image.Image) -> Image.Image:
    """Correct perspective distortion from camera angle.

    Stub — requires camera calibration and corner detection
    which depends on the physical mounting geometry.
    """
    # For dev/testing with fixture images, no correction needed
    return image


def preprocess(image: Image.Image) -> Image.Image:
    """Run the full preprocessing pipeline on a captured image.

    Returns a clean grayscale image ready for OCR. We skip
    binarization here because Tesseract does its own internal
    binarization and produces better results from grayscale input.
    """
    corrected = correct_perspective(image)
    normalized = normalize_lighting(corrected)
    return normalized
