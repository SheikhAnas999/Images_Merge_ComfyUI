from .image_grid_merger import ImageGridMerger

NODE_CLASS_MAPPINGS = {
    "ImageGridMerger": ImageGridMerger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageGridMerger": "Image Grid Merger",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]