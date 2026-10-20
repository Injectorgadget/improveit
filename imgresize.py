
from PIL import Image

# Load the tall banner you generated
img = Image.open("assets/improveit_wide_banner.png")

# Final header size
target_height = 450
target_width = 1450

# Resize to exactly the correct size
header = img.resize((target_width, target_height), Image.LANCZOS)

# Save as the final header strip
header.save("assets/improveit_header_120.png")
