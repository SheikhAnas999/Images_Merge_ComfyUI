import torch
import torch.nn.functional as F


class ImageGridMerger:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
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
                    ["black", "white", "gray"],
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "merge"
    CATEGORY = "Image"

    def resize(self, img, h, w):
        img = img.permute(0, 3, 1, 2)
        img = F.interpolate(
            img,
            size=(h, w),
            mode="bilinear",
            align_corners=False,
        )
        img = img.permute(0, 2, 3, 1)
        return img

    def make_blank(self, h, w, color):

        if color == "white":
            value = 1.0
        elif color == "gray":
            value = 0.5
        else:
            value = 0.0

        return torch.ones((1, h, w, 3), dtype=torch.float32) * value

    def merge(self, images, columns, spacing, background):

        # IMAGE batch shape:
        # (N,H,W,C)

        count = images.shape[0]

        heights = [images[i].shape[0] for i in range(count)]
        widths = [images[i].shape[1] for i in range(count)]

        target_h = max(heights)
        target_w = max(widths)

        resized = []

        for i in range(count):

            img = images[i].unsqueeze(0)

            if img.shape[1] != target_h or img.shape[2] != target_w:
                img = self.resize(img, target_h, target_w)

            resized.append(img)

        rows = (count + columns - 1) // columns

        blank = self.make_blank(target_h, target_w, background)

        if spacing > 0:
            gap_v = self.make_blank(target_h, spacing, background)
            gap_h = self.make_blank(spacing, 1, background)
        else:
            gap_v = None
            gap_h = None

        canvas_rows = []

        idx = 0

        for r in range(rows):

            current = []

            for c in range(columns):

                if idx < len(resized):
                    current.append(resized[idx])
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