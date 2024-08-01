import modules.scripts as scripts
import gradio as gr
from modules import images, shared
from modules.processing import process_images, Processed
from modules.shared import opts, state
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops, ImageOps
import numpy as np
import random
import os

class SomeImageEffectsScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.overlay_files = []
        self.update_overlay_files()

    def update_overlay_files(self):
        # Print current working directory and script location
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
        
        # Try multiple potential locations for the overlays directory
        potential_dirs = [
            os.path.join(scripts.basedir(), "overlays"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlays"),
            os.path.join(os.getcwd(), "overlays"),
        ]
        
        for overlay_dir in potential_dirs:
            print(f"Checking for overlays in: {overlay_dir}")
            if os.path.exists(overlay_dir):
                self.overlay_files = [f for f in os.listdir(overlay_dir) if self.is_image_file(f)]
                print(f"Found {len(self.overlay_files)} overlay files in {overlay_dir}")
                return
        
        print("Overlay directory not found in any of the checked locations.")


    def is_image_file(self, filename):
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def title(self):
        return "Advanced Image Effects"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("Some Image Effects", open=False):
                save_original = gr.Checkbox(label="Save Original Image", value=True)
                
                with gr.Row():
                    enable_grain = gr.Checkbox(label="Enable Grain", value=False)
                    enable_vignette = gr.Checkbox(label="Enable Vignette", value=False)
                    enable_random_blur = gr.Checkbox(label="Enable Random Blur", value=False)
                    enable_color_offset = gr.Checkbox(label="Enable Color Offset", value=False)
                      
                with gr.Row():
                    grain_intensity = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=0.3, label="Grain Intensity")
                
                with gr.Row():
                    vignette_intensity = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=0.3, label="Vignette Intensity")
                    vignette_feather = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=0.3, label="Vignette Feather")
                    vignette_roundness = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=0.5, label="Vignette Roundness")
                
                with gr.Row():
                    blur_max_size = gr.Slider(minimum=0.0, maximum=0.5, step=0.05, value=0.2, label="Max Blur Size (% of image)")
                    blur_strength = gr.Slider(minimum=0.0, maximum=10.0, step=0.5, value=3.0, label="Blur Strength")
                
                with gr.Row():
                    color_offset_x = gr.Slider(minimum=-50, maximum=50, step=1, value=0, label="Color Offset X")
                    color_offset_y = gr.Slider(minimum=-50, maximum=50, step=1, value=0, label="Color Offset Y")
                
                with gr.Row():
                    enable_overlay = gr.Checkbox(label="Enable Overlay", value=False)
                    overlay_file = gr.Dropdown(label="Overlay File", choices=self.overlay_files)
                    overlay_fit = gr.Dropdown(label="Overlay Fit", choices=["stretch", "fit_out"], value="stretch")
                
                with gr.Row():
                    overlay_opacity = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=0.5, label="Overlay Opacity")
                    overlay_blend_mode = gr.Dropdown(label="Overlay Blend Mode", choices=[
                        "normal", "multiply", "screen", "overlay", "darken", "lighten",
                        "color_dodge", "color_burn", "hard_light", "soft_light", "difference",
                        "exclusion", "hue", "saturation", "color", "luminosity"
                    ], value="normal")

                with gr.Row():
                    enable_luminosity = gr.Checkbox(label="Enable Luminosity Adjustment", value=False)
                    luminosity_factor = gr.Slider(minimum=-1.0, maximum=1.0, step=0.05, value=0, label="Luminosity Factor")

                with gr.Row():
                    enable_contrast = gr.Checkbox(label="Enable Contrast Adjustment", value=False)
                    contrast_factor = gr.Slider(minimum=0.0, maximum=2.0, step=0.05, value=1, label="Contrast Factor")

                with gr.Row():
                    enable_hue = gr.Checkbox(label="Enable Hue Adjustment", value=False)
                    hue_factor = gr.Slider(minimum=-180, maximum=180, step=1, value=0, label="Hue Shift")

                with gr.Row():
                    enable_saturation = gr.Checkbox(label="Enable Saturation Adjustment", value=False)
                    saturation_factor = gr.Slider(minimum=0.0, maximum=2.0, step=0.05, value=1, label="Saturation Factor")

        return [save_original, enable_grain, enable_vignette, enable_random_blur, enable_color_offset,
                grain_intensity, vignette_intensity, vignette_feather, vignette_roundness,
                blur_max_size, blur_strength, color_offset_x, color_offset_y,
                enable_overlay, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode,
                enable_luminosity, luminosity_factor, enable_contrast, contrast_factor,
                enable_hue, hue_factor, enable_saturation, saturation_factor]

    def process(self, p, *args):
        enabled_effects = []
        if args[1]:  # enable_grain
            enabled_effects.append("Grain")
        if args[2]:  # enable_vignette
            enabled_effects.append("Vignette")
        if args[3]:  # enable_random_blur
            enabled_effects.append("Random Blur")
        if args[4]:  # enable_color_offset
            enabled_effects.append("Color Offset")
        if args[13]:  # enable_overlay
            enabled_effects.append("Overlay")
        if args[18]:  # enable_luminosity
            enabled_effects.append("Luminosity")
        if args[20]:  # enable_contrast
            enabled_effects.append("Contrast")
        if args[22]:  # enable_hue
            enabled_effects.append("Hue")
        if args[24]:  # enable_saturation
            enabled_effects.append("Saturation")
        
        if enabled_effects:
            p.extra_generation_params["Some Image Effects"] = ", ".join(enabled_effects)

 
    def postprocess_image(self, p, pp, *args):
        save_original, enable_grain, enable_vignette, enable_random_blur, enable_color_offset, \
        grain_intensity, vignette_intensity, vignette_feather, vignette_roundness, \
        blur_max_size, blur_strength, color_offset_x, color_offset_y, \
        enable_overlay, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode, \
        enable_luminosity, luminosity_factor, enable_contrast, contrast_factor, \
        enable_hue, hue_factor, enable_saturation, saturation_factor = args

        if hasattr(pp, 'image'):
            if save_original:
                self.save_original_image(pp.image)
            pp.image = self.add_effects(pp.image, *args)
        elif hasattr(pp, 'images'):
            for i, image in enumerate(pp.images):
                if save_original:
                    self.save_original_image(image)
                pp.images[i] = self.add_effects(image, *args)


    def add_effects(self, img, save_original, enable_grain, enable_vignette, enable_random_blur, enable_color_offset,
                    grain_intensity, vignette_intensity, vignette_feather, vignette_roundness,
                    blur_max_size, blur_strength, color_offset_x, color_offset_y,
                    enable_overlay, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode):
        if enable_grain:
            img = self.add_grain(img, grain_intensity)
        
        if enable_vignette:
            img = self.add_vignette(img, vignette_intensity, vignette_feather, vignette_roundness)
        
        if enable_random_blur:
            img = self.add_random_blur(img, blur_max_size, blur_strength)
        
        if enable_color_offset:
            img = self.add_color_offset(img, color_offset_x, color_offset_y)
        
        if enable_overlay and overlay_file:
            img = self.add_overlay(img, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode)
        
        return img

    def add_grain(self, img, intensity):
        img_np = np.array(img)
        noise = np.random.randn(*img_np.shape) * 255 * intensity
        noisy_img = np.clip(img_np + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_img)

    def add_vignette(self, img, intensity, feather, roundness):
        width, height = img.size
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)
        
        x_center, y_center = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        for i in range(max_radius):
            alpha = int(255 * (1 - (i / max_radius) ** roundness) * intensity)
            draw.ellipse([x_center - i, y_center - i, x_center + i, y_center + i], fill=alpha)
        
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max_radius * feather))
        
        enhancer = ImageEnhance.Brightness(img)
        darkened = enhancer.enhance(1 - intensity * 0.5)
        
        return Image.composite(darkened, img, mask)

    def add_random_blur(self, img, max_size, strength):
        width, height = img.size
        blur_size = int(min(width, height) * max_size)
        x = random.randint(0, width - blur_size)
        y = random.randint(0, height - blur_size)
        
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([x, y, x + blur_size, y + blur_size], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_size // 4))
        
        blurred = img.filter(ImageFilter.GaussianBlur(radius=strength))
        return Image.composite(blurred, img, mask)

    def add_color_offset(self, img, offset_x, offset_y):
        r, g, b = img.split()
        r = ImageChops.offset(r, offset_x, offset_y)
        b = ImageChops.offset(b, -offset_x, -offset_y)
        return Image.merge('RGB', (r, g, b))

    def add_overlay(self, img, overlay_file, overlay_fit, opacity, blend_mode):
        if img is None:
            print("Error: Input image is None")
            return None

        # Try multiple potential locations for the overlays directory
        potential_dirs = [
            os.path.join(scripts.basedir(), "overlays"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlays"),
            os.path.join(os.getcwd(), "overlays"),
        ]
        
        overlay_path = None
        for overlay_dir in potential_dirs:
            temp_path = os.path.join(overlay_dir, overlay_file)
            if os.path.exists(temp_path):
                overlay_path = temp_path
                break

        if not overlay_path:
            print(f"Overlay file not found: {overlay_file}")
            return img

        try:
            overlay = Image.open(overlay_path).convert("RGBA")
        except Exception as e:
            print(f"Error opening overlay file: {e}")
            return img

        # Resize overlay
        if overlay_fit == "stretch":
            overlay = overlay.resize(img.size, Image.LANCZOS)
        elif overlay_fit == "fit_out":
            img_ratio = img.width / img.height
            overlay_ratio = overlay.width / overlay.height
            if img_ratio > overlay_ratio:
                new_width = img.width
                new_height = int(new_width / overlay_ratio)
            else:
                new_height = img.height
                new_width = int(new_height * overlay_ratio)
            overlay = overlay.resize((new_width, new_height), Image.LANCZOS)
            
            # Crop to fit
            left = (overlay.width - img.width) // 2
            top = (overlay.height - img.height) // 2
            right = left + img.width
            bottom = top + img.height
            overlay = overlay.crop((left, top, right, bottom))

        # Apply opacity
        overlay = Image.blend(Image.new('RGBA', img.size, (0, 0, 0, 0)), overlay, opacity)

        # Apply blend mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Apply blend mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        if blend_mode == "multiply":
            blended = ImageChops.multiply(img, overlay)
        elif blend_mode == "screen":
            blended = ImageChops.screen(img, overlay)
        elif blend_mode == "overlay":
            blended = self.overlay_blend(img, overlay)
        elif blend_mode == "darken":
            blended = ImageChops.darker(img, overlay)
        elif blend_mode == "lighten":
            blended = ImageChops.lighter(img, overlay)
        elif blend_mode == "color_dodge":
            blended = self.color_dodge(img, overlay)
        elif blend_mode == "color_burn":
            blended = self.color_burn(img, overlay)
        elif blend_mode == "hard_light":
            blended = self.hard_light(img, overlay)
        elif blend_mode == "soft_light":
            blended = self.soft_light(img, overlay)
        elif blend_mode == "difference":
            blended = ImageChops.difference(img, overlay)
        elif blend_mode == "exclusion":
            blended = self.exclusion(img, overlay)
        elif blend_mode == "hue":
            blended = self.hue_blend(img, overlay)
        elif blend_mode == "saturation":
            blended = self.saturation_blend(img, overlay)
        elif blend_mode == "color":
            blended = self.color_blend(img, overlay)
        elif blend_mode == "luminosity":
            blended = self.luminosity_blend(img, overlay)
        else:  # normal
            blended = Image.alpha_composite(img, overlay)

        return blended.convert("RGB")

    def adjust_luminosity(self, img, factor):
        return ImageEnhance.Brightness(img).enhance(1 + factor)

    def adjust_contrast(self, img, factor):
        return ImageEnhance.Contrast(img).enhance(factor)

    def adjust_hue(self, img, shift):
        img = img.convert('HSV')
        h, s, v = img.split()
        h = h.point(lambda x: (x + shift) % 256)
        return Image.merge('HSV', (h, s, v)).convert('RGB')

    def adjust_saturation(self, img, factor):
        return ImageEnhance.Color(img).enhance(factor)

    def add_effects(self, img, save_original, enable_grain, enable_vignette, enable_random_blur, enable_color_offset,
                    grain_intensity, vignette_intensity, vignette_feather, vignette_roundness,
                    blur_max_size, blur_strength, color_offset_x, color_offset_y,
                    enable_overlay, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode,
                    enable_luminosity, luminosity_factor, enable_contrast, contrast_factor,
                    enable_hue, hue_factor, enable_saturation, saturation_factor):
        if img is None:
            print("Error: Input image is None")
            return None

        if enable_grain:
            img = self.add_grain(img, grain_intensity)
        
        if enable_vignette:
            img = self.add_vignette(img, vignette_intensity, vignette_feather, vignette_roundness)
        
        if enable_random_blur:
            img = self.add_random_blur(img, blur_max_size, blur_strength)
        
        if enable_color_offset:
            img = self.add_color_offset(img, color_offset_x, color_offset_y)
        
        if enable_overlay and overlay_file:
            img = self.add_overlay(img, overlay_file, overlay_fit, overlay_opacity, overlay_blend_mode)
        
        if enable_luminosity:
            img = self.adjust_luminosity(img, luminosity_factor)
        
        if enable_contrast:
            img = self.adjust_contrast(img, contrast_factor)
        
        if enable_hue:
            img = self.adjust_hue(img, hue_factor)
        
        if enable_saturation:
            img = self.adjust_saturation(img, saturation_factor)
        
        return img

    def save_original_image(self, img):
        save_dir = getattr(shared.opts, 'outdir_samples', None) or getattr(shared.opts, 'outdir_txt2img_samples', None) or getattr(shared.opts, 'outdir_img2img_samples', None) or getattr(shared.opts, 'outdir_extras_samples', None) or os.getcwd()
        
        save_dir = os.path.join(save_dir, "originals")
        os.makedirs(save_dir, exist_ok=True)
        
        # Use a default extension if none is provided
        job_name = shared.state.job if shared.state.job else "image"
        base_name, ext = os.path.splitext(job_name)
        if not ext:
            ext = ".png"  # Default to PNG if no extension is provided
        
        filename = f"{base_name}_original{ext}"
        save_path = os.path.join(save_dir, filename)
        
        try:
            img.save(save_path)
            print(f"Original image saved to: {save_path}")
        except Exception as e:
            print(f"Error saving original image: {e}")
