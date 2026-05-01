from PIL import Image, ImageTk
from loguru import logger

import tkinter as tk

def show_splash(duration=3000):
    root = tk.Tk()
    root.overrideredirect(True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    pil_img = Image.open('assets/splash.png').convert('RGBA')
    img_w, img_h = pil_img.size

    max_w, max_h = int(screen_width * 0.9), int(screen_height * 0.9)
    if img_w > max_w or img_h > max_h:
        ratio = min(max_w / img_w, max_h / img_h)
        img_w, img_h = int(img_w * ratio), int(img_h * ratio)
        pil_img = pil_img.resize((img_w, img_h), Image.LANCZOS)

    tk_img = ImageTk.PhotoImage(pil_img)

    x = (screen_width - img_w) // 2
    y = (screen_height - img_h) // 2
    root.geometry(f'{img_w}x{img_h}+{x}+{y}')

    # Прозрачность окна
    root.config(bg='black')
    root.attributes('-transparentcolor', 'black')

    label = tk.Label(root, image=tk_img, bd=0, highlightthickness=0, bg='black')
    label.pack(fill='both', expand=True)

    root.after(duration, root.destroy)
    root.mainloop()