import os
import shutil
from tkinter import Tk, filedialog

# Set up paths
ASSETS_DIR = "assets"
TARGET_FILENAME = "your_image.jpg"

# Make sure assets folder exists
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Hide the Tkinter main window
Tk().withdraw()

# Let the user pick an image
file_path = filedialog.askopenfilename(
    title="Choose an image for the puzzle",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

# If the user selected a file
if file_path:
    # Copy it to the assets folder and rename
    dest_path = os.path.join(ASSETS_DIR, TARGET_FILENAME)
    shutil.copyfile(file_path, dest_path)
    print(f"✅ Image copied to: {dest_path}")
    print("🧩 You can now run the puzzle game!")
else:
    print("❌ No image was selected.")
