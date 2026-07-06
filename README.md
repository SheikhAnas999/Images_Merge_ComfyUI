# Images_Merge_ComfyUI

A ComfyUI custom node that merges a batch of images into a single grid canvas, with configurable columns, spacing, and background color.

## Node: Image Grid Merger

**Inputs**

| Name      | Type  | Description                                      |
|-----------|-------|---------------------------------------------------|
| images    | IMAGE | Batch of images to arrange into a grid            |
| columns   | INT   | Number of columns in the grid (default: 3)        |
| spacing   | INT   | Pixel gap between grid cells (default: 10)        |
| background| enum  | Fill color for gaps/empty cells: black, white, gray |

**Output**

| Name  | Type  | Description        |
|-------|-------|---------------------|
| image | IMAGE | The merged grid image |

Images of differing sizes are resized to match the largest image in the batch before being placed on the grid.

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/SheikhAnas999/Images_Merge_ComfyUI.git
```

Restart ComfyUI (or use ComfyUI-Manager's "Install via Git URL").

## Update

```bash
cd ComfyUI/custom_nodes/Images_Merge_ComfyUI
git pull
```

## Requirements

No extra dependencies — this node only relies on `torch`, which ComfyUI already provides.

## License

MIT — see [LICENSE](LICENSE).
