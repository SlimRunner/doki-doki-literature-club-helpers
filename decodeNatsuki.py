import numpy as np
import cv2
import os


def transform_image(file_path: str, out_dir: str):
    img = cv2.imread(file_path)
    assert img is not None

    img = cv2.bitwise_not(img)

    height, width = img.shape[:2]
    halfWidth: float = width / 2
    halfHeight: float = height / 2
    minLength = min(height, width)
    maxLength = max(height, width)

    map_x = np.zeros((height, width), dtype=np.float32)
    map_y = np.zeros((height, width), dtype=np.float32)

    origin = np.array([halfWidth, halfHeight])
    TAU = 2 * np.pi
    PIH = np.pi / 2

    for x in range(width):
        for y in range(height):
            vec = np.array([x, y]) - origin

            radius = np.hypot((x - halfWidth) / minLength, (y - halfHeight) / minLength)
            theta = np.mod(np.arctan2(vec[1], vec[0]) + PIH, TAU)

            map_x[y, x] = width * theta / TAU
            map_y[y, x] = radius * 2 * maxLength

    img = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    out_path = os.path.join(out_dir, "natsuki.decoded.png")

    cv2.imwrite(out_path, img)
    print(f"Transformed image saved to {out_path}")
