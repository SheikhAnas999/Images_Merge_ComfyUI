import torch


class ImageGridMerger:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_1": ("IMAGE",),
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
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_6": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "merge"
    CATEGORY = "Image"

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
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
        image_6=None,
    ):

        # each image_N input is itself an IMAGE batch of shape (N,H,W,C);
        # flatten every connected slot into a single list of (1,H,W,C) images
        batches = [
            b
            for b in (image_1, image_2, image_3, image_4, image_5, image_6)
            if b is not None
        ]

        images = []
        for batch in batches:
            for i in range(batch.shape[0]):
                images.append(batch[i].unsqueeze(0))

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
            gap_h = self.make_blank(spacing, 1, background)
        else:
            gap_v = None
            gap_h = None

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