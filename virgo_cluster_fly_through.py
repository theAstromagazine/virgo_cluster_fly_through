'''
infos: https://noirlab.edu/public/images/noirlab2521a/
zoom in and information: https://rubinobservatory.org/news/rubin-first-look/cosmic-treasure-chest
asteroid information: https://rubinobservatory.org/news/rubin-first-look/swarm-asteroids
'''


import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pyvips
import math
import os

# -------------------------
# Frame processing helpers
# -------------------------
def process_frame(args):
    """Helper function for parallel processing with separate calc/export resolutions"""
    img, out_dir, frame_params, export_res = args
    x_center, y_center, z, frame_count, W, H, CALC_X, CALC_Y = frame_params
    EXPORT_X, EXPORT_Y = export_res
    
    cw = max(1, int(round(W / z)))
    ch = max(1, int(round(H / z)))
    
    left = max(0, min(int(round(x_center - cw / 2.0)), W - cw))
    top = max(0, min(int(round(y_center - ch / 2.0)), H - ch))
    
    tile = img.crop(left, top, cw, ch)
    # First resize to calculation resolution
    frame = tile.resize(CALC_X / cw, vscale=CALC_Y / ch)
    # Then downscale to export resolution if different
    if (EXPORT_X, EXPORT_Y) != (CALC_X, CALC_Y):
        frame = frame.resize(EXPORT_X / CALC_X, vscale=EXPORT_Y / CALC_Y)
    frame.write_to_file(os.path.join(out_dir, f"frame_{frame_count:06d}.png"))
    return frame_count

# -------------------------
# Motion generator
# -------------------------
def save_zoom_circle_zoom(img, out_dir, CALC_X, CALC_Y, zoom_in_frames, circle_frames, zoom_out_frames,
                         fade_in_frames=30, fade_out_frames=30, max_radius=None, circle_degrees=220,
                         export_res=None):
    """
    Enhanced version with separate calculation and export resolutions
    CALC_X, CALC_Y: Resolution for movement calculations (e.g. 8K)
    export_res: (width, height) tuple for final output resolution (e.g. 4K)
    """
    W, H = img.width, img.height
    os.makedirs(out_dir, exist_ok=True)
    
    # Use calculation resolution for export if not specified
    if export_res is None:
        export_res = (CALC_X, CALC_Y)
        
    # Validate resolutions
    if export_res[0] > CALC_X or export_res[1] > CALC_Y:
        raise ValueError("Export resolution cannot be larger than calculation resolution")
    
    # Initial setup and checks
    fade_in_frames = max(0, min(fade_in_frames, zoom_in_frames))
    fade_out_frames = max(0, min(fade_out_frames, circle_frames))
    
    cx, cy = W / 2.0, H / 2.0
    if max_radius is None:
        max_radius = min((W - CALC_X) / 2.0, (H - CALC_Y) / 2.0)
        if max_radius < 0:
            raise ValueError("CALC_X/CALC_Y larger than image dimensions")
    
    # Pre-calculate constants
    start_z = 1.0
    end_z = float(W) / CALC_X
    total_circle_rad = math.radians(circle_degrees)
    
    # Prepare frame parameters for all frames
    frame_params = []
    frame_count = 1
    
    # Part 1: Zoom IN
    t_zooms = np.linspace(0, 1, zoom_in_frames) if zoom_in_frames > 1 else [0]
    for i, t_zoom in enumerate(t_zooms):
        z = start_z * (end_z / start_z) ** t_zoom
        x_center, y_center = cx, cy
        
        if fade_in_frames > 0 and i >= zoom_in_frames - fade_in_frames:
            fade_i = i - (zoom_in_frames - fade_in_frames)
            fade_t = fade_i / (fade_in_frames - 1) if fade_in_frames > 1 else 1.0
            
            circle_progress = min((fade_t * fade_in_frames) / circle_frames, 1.0)
            r = max_radius * math.sin(math.pi * circle_progress)
            theta = total_circle_rad * circle_progress
            
            cx_circle = cx + r * math.cos(theta)
            cy_circle = cy + r * math.sin(theta)
            
            x_center = (1.0 - fade_t) * cx + fade_t * cx_circle
            y_center = (1.0 - fade_t) * cy + fade_t * cy_circle
        
        frame_params.append((x_center, y_center, z, frame_count, W, H, CALC_X, CALC_Y))
        frame_count += 1
    
    # Part 2: Circle Movement
    t_circles = np.linspace(0, 1, circle_frames) if circle_frames > 1 else [0]
    for i, t_circle in enumerate(t_circles):
        r = max_radius * math.sin(math.pi * t_circle)
        theta = total_circle_rad * t_circle
        x_center = cx + r * math.cos(theta)
        y_center = cy + r * math.sin(theta)
        
        if fade_out_frames > 0 and i >= circle_frames - fade_out_frames:
            fade_i = i - (circle_frames - fade_out_frames)
            fade_t = fade_i / (fade_out_frames - 1) if fade_out_frames > 1 else 1.0
            z = end_z * (1.0 / end_z) ** fade_t
        else:
            z = end_z
        
        frame_params.append((x_center, y_center, z, frame_count, W, H, CALC_X, CALC_Y))
        frame_count += 1
    
    # Part 3: Zoom OUT
    start_z_for_zoom_out = z if fade_out_frames > 0 else end_z
    t_zoom_outs = np.linspace(0, 1, zoom_out_frames) if zoom_out_frames > 1 else [0]
    for t in t_zoom_outs:
        z = start_z_for_zoom_out * (1.0 / start_z_for_zoom_out) ** t
        frame_params.append((cx, cy, z, frame_count, W, H, CALC_X, CALC_Y))
        frame_count += 1
    
    # Process frames in parallel
    num_workers = max(1, mp.cpu_count() - 1)  # Leave one CPU free
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        args = [(img, out_dir, params, export_res) for params in frame_params]
        list(executor.map(process_frame, args))
    
    return frame_count - 1


def main():
    # source image path
    SRC = r"C:\Users\path_to_your_image\virgo_cluster_image.fits"

    # import image
    img = pyvips.Image.new_from_file(SRC, access="random")
    W, H = img.width, img.height
    print("Bildgröße:", W, "x", H)

    # output folder
    OUT = r"C:\Users\output_folder"

    CALC_X, CALC_Y = 7680, 4320      # 8K calculation resolution
    EXPORT_X, EXPORT_Y = 3840, 2160   # 4K export resolution

    # start processing
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
        export_res=(EXPORT_X, EXPORT_Y)  # Export at 4K
    )


if __name__ == "__main__":
    main()