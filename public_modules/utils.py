import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

def generate_receipt_image(donation):
    """
    Generates a simple receipt image for a donation using Pillow.
    Saves the image to the donation's receipt_image field.
    """
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Load a font (try default, fallback to a basic one)
    try:
        # Try to load a standard font if available, or use default
        # adjusting size might be tricky with default load_default()
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        # Fallback for systems without arial
        font_large = ImageFont.load_default() 
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw Header
    draw.text((width/2, 50), "DONATION RECEIPT", font=font_large, fill="black", anchor="ms")
    
    # Draw Donation Details
    start_y = 150
    line_height = 50
    
    # helper for drawing lines
    def draw_line(label, value, y):
        draw.text((100, y), f"{label}:", font=font_medium, fill="gray", anchor="ls")
        draw.text((400, y), f"{value}", font=font_medium, fill="black", anchor="ls")

    draw_line("Donor Name", donation.donor.fullname if donation.donor else "Anonymous", start_y)
    draw_line("Amount", f"{donation.amount} {donation.currency.upper()}", start_y + line_height)
    draw_line("Date", donation.donation_date.strftime("%Y-%m-%d %H:%M:%S"), start_y + line_height * 2)
    draw_line("Payment Method", donation.payment_method.replace('_', ' ').title(), start_y + line_height * 3)
    draw_line("Purpose", donation.donation_purpose or "General Support", start_y + line_height * 4)
    if donation.stripe_payment_intent_id:
        draw_line("Transaction ID", donation.stripe_payment_intent_id, start_y + line_height * 5)
    
    # Draw Footer
    draw.text((width/2, height - 50), "Thank you for your support!", font=font_medium, fill="green", anchor="ms")

    # Save details
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    filename = f"receipt_{donation.id}.png"
    
    # Save to model
    donation.receipt_image.save(filename, ContentFile(buffer.getvalue()), save=True)
    return donation.receipt_image.url
