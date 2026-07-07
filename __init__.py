from .image_grid_merger import ImageGridMerger
from .image_grid_merger_from_files import ImageGridMergerFromFiles

NODE_CLASS_MAPPINGS = {
    "ImageGridMerger": ImageGridMerger,
    "ImageGridMergerFromFiles": ImageGridMergerFromFiles,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageGridMerger": "Image Grid Merger",
    "ImageGridMergerFromFiles": "Image Grid Merger (Upload)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]