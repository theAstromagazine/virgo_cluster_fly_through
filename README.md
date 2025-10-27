# Virgo Cluster Fly-Through Generator

Create fly-through animations of the Virgo Cluster image from NOIRLab. (Image Export)

## About
This script generates a smooth fly-through animation of the Virgo Cluster image, featuring:
- Initial zoom-in
- circle movement (degree adjustable)
- Final zoom-out
- f.e. 8K calculation with 4K export capability (adjustable)

## Source Image
- NOIRLab Image: [Virgo Cluster](https://noirlab.edu/public/images/noirlab2521a/)
- Manual zoom-in and Read more about: [Rubin First Look](https://rubinobservatory.org/news/rubin-first-look/cosmic-treasure-chest)

## Requirements
- Python 3.8+
- libvips (system dependency)
- Python packages (see requirements.txt)

## Installation

1. Install libvips:
```bash
# Windows (using chocolatey):
choco install vips
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```python
python virgo_cluster_fly_through.py
```

## Parameters
Adjust these in the script:
```python
SRC = r"C:\Users\path_to_your_image\virgo_cluster_image.fits"   # Input image path
OUT = r"C:\Users\output_folder"  # Output folder
CALC_X, CALC_Y = 7680, 4320        # 8K calculation
EXPORT_X, EXPORT_Y = 3840, 2160    # 4K export

save_zoom_circle_zoom(
    img=img,
    out_dir=OUT,
    CALC_X=CALC_X,
    CALC_Y=CALC_Y,
    zoom_in_frames=2500,
    circle_frames=5000,
    zoom_out_frames=2500,
    fade_in_frames=300,
    fade_out_frames=300,
    max_radius=None,
    circle_degrees=200,
    export_res=(EXPORT_X, EXPORT_Y)
)

## License
MIT License - see LICENSE file