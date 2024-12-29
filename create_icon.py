from PIL import Image, ImageDraw, ImageFont
import os


def create_rfid_icon():
    """Create a modern RFID reader icon with multiple sizes."""

    # List of sizes needed for Windows icons
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for size in sizes:
        # Create new image with transparency
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Calculate dimensions
        width, height = size
        padding = width // 8
        inner_width = width - (2 * padding)
        inner_height = height - (2 * padding)

        # Draw RFID card outline (rounded rectangle)
        radius = width // 8
        rect_coords = [padding, padding, width - padding, height - padding]

        # Draw base card in blue
        draw.rounded_rectangle(
            rect_coords,
            radius,
            fill=(0, 122, 255, 255),  # Apple-style blue
            outline=(255, 255, 255, 255),
            width=max(1, width // 32),
        )

        # Draw RFID waves (arcs)
        center_x = width // 2
        center_y = height // 2
        wave_spacing = width // 10

        for i in range(3):
            wave_radius = (width // 4) + (i * wave_spacing)
            # Draw partial circle for wave effect
            draw.arc(
                [
                    center_x - wave_radius,
                    center_y - wave_radius,
                    center_x + wave_radius,
                    center_y + wave_radius,
                ],
                -45,  # Start angle
                45,  # End angle
                fill=(255, 255, 255, 200),  # Slightly transparent white
                width=max(1, width // 32),
            )

        # Draw chip
        chip_size = width // 6
        draw.rectangle(
            [
                center_x - chip_size,
                center_y - chip_size // 2,
                center_x + chip_size,
                center_y + chip_size // 2,
            ],
            fill=(255, 255, 255, 255),  # White
        )

        images.append(image)

    # Save as ICO file
    images[0].save("icon.ico", format="ICO", sizes=sizes, append_images=images[1:])


if __name__ == "__main__":
    create_rfid_icon()
