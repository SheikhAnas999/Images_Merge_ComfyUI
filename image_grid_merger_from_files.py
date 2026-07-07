import os
import hashlib

import numpy as np
import torch
from PIL import Image, ImageOps

import folder_paths


NONE_OPTION = "none"


def _input_image_choices():
    input_dir = folder_paths.get_input_directory()
    files = [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]
    return sorted(files)


class ImageGridMergerFromFiles:
    """Upload up to 6 images directly on the node and merge them into one grid image."""

    @classmethod
    def INPUT_TYPES(cls):
        files = _input_image_choices()
        optional_files = [NONE_OPTION] + files

        return {
            "required": {
                "image_1": (files, {"image_upload": True}),
                "columns": (
                    "INT",
                    {
                        "default": 3,
                        "min": 1,
                        "max": 10,
                        "step": 1,
                    },
                ),
                "spacing": (
                    "INT",
                    {
                        "default": 10,
                        "min": 0,
                        "max": 100,
                    },
                ),
                "background": (
                    ["white", "black", "gray"],
                ),
            },
            "optional": {
                "image_2": (optional_files, {"image_upload": True}),
                "image_3": (optional_files, {"image_upload": True}),
                "image_4": (optional_files, {"image_upload": True}),
                "image_5": (optional_files, {"image_upload": True}),
                "image_6": (optional_files, {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "merge"
    CATEGORY = "Image"

    @staticmethod
    def load_image(filename):
        image_path = folder_paths.get_annotated_filepath(filename)
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)

        if img.mode == "I":
            img = img.point(lambda i: i * (1 / 255))
        img = img.convert("RGB")

        arr = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(arr).unsqueeze(0)

    def make_blank(self, h, w, color):

        if color == "white":
            value = 1.0
        elif color == "gray":
            value = 0.5
        else:
            value = 0.0

        return torch.ones((1, h, w, 3), dtype=torch.float32) * value

    def place_on_canvas(self, img, h, w, color):
        # keep the original image untouched; center it on a padded
        # canvas instead of stretching it to fill the cell
        img_h, img_w = img.shape[1], img.shape[2]

        if img_h == h and img_w == w:
            return img

        canvas = self.make_blank(h, w, color)
        y_off = (h - img_h) // 2
        x_off = (w - img_w) // 2
        canvas[:, y_off:y_off + img_h, x_off:x_off + img_w, :] = img
        return canvas

    def merge(
        self,
        image_1,
        columns,
        spacing,
        background,
        image_2=NONE_OPTION,
        image_3=NONE_OPTION,
        image_4=NONE_OPTION,
        image_5=NONE_OPTION,
        image_6=NONE_OPTION,
    ):

        filenames = [
            f
            for f in (image_1, image_2, image_3, image_4, image_5, image_6)
            if f and f != NONE_OPTION
        ]

        images = [self.load_image(f) for f in filenames]

        count = len(images)

        columns = min(columns, count)

        heights = [img.shape[1] for img in images]
        widths = [img.shape[2] for img in images]

        target_h = max(heights)
        target_w = max(widths)

        placed = []

        for img in images:
            placed.append(self.place_on_canvas(img, target_h, target_w, background))

        rows = (count + columns - 1) // columns

        blank = self.make_blank(target_h, target_w, background)

        if spacing > 0:
            gap_v = self.make_blank(target_h, spacing, background)
        else:
            gap_v = None

        canvas_rows = []

        idx = 0

        for r in range(rows):

            current = []

            for c in range(columns):

                if idx < len(placed):
                    current.append(placed[idx])
                else:
                    current.append(blank)

                idx += 1

                if c != columns - 1 and spacing > 0:
                    current.append(gap_v)

            row = torch.cat(current, dim=2)

            canvas_rows.append(row)

            if r != rows - 1 and spacing > 0:

                separator = self.make_blank(
                    spacing,
                    row.shape[2],
                    background,
                )

                canvas_rows.append(separator)

        merged = torch.cat(canvas_rows, dim=1)

        return (merged,)

    @classmethod
    def IS_CHANGED(
        cls,
        image_1,
        columns,
        spacing,
        background,
        image_2=NONE_OPTION,
        image_3=NONE_OPTION,
        image_4=NONE_OPTION,
        image_5=NONE_OPTION,
        image_6=NONE_OPTION,
    ):
        m = hashlib.sha256()
        for f in (image_1, image_2, image_3, image_4, image_5, image_6):
            if f and f != NONE_OPTION:
                path = folder_paths.get_annotated_filepath(f)
                with open(path, "rb") as fh:
                    m.update(fh.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(
        cls,
        image_1,
        image_2=NONE_OPTION,
        image_3=NONE_OPTION,
        image_4=NONE_OPTION,
        image_5=NONE_OPTION,
        image_6=NONE_OPTION,
    ):
        for f in (image_1, image_2, image_3, image_4, image_5, image_6):
            if f and f != NONE_OPTION:
                if not folder_paths.exists_annotated_filepath(f):
                    return "Invalid image file: {}".format(f)

        return True
