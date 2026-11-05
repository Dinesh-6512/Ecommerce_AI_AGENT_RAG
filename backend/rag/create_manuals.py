import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Manuals destination directory: frontend/public/manuals/
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "frontend" / "public" / "manuals"

MANUALS_DATA = [
    {
        "filename": "classic-white-t-shirt.pdf",
        "product_name": "Classic White T-Shirt",
        "how_to_use": (
            "Wear for casual everyday use or layering. Machine wash cold with similar colors inside out. "
            "Use gentle detergent and avoid bleach to maintain fabric brightness and softness. "
            "Tumble dry low or hang dry in the shade to preserve fit and prevent fabric shrinkage. "
            "Iron inside out on medium heat if necessary."
        ),
        "troubleshooting": (
            "If yellowing occurs, pre-soak in cold water with baking soda before washing. "
            "For persistent coffee or grease stains, apply mild liquid detergent directly onto the spot "
            "and let sit for ten minutes before regular laundering. "
            "If minor shrinking happens, gently stretch the damp shirt back to shape before flat drying."
        ),
        "warranty": (
            "Comes with a 30-day satisfaction guarantee covering fabric defects, torn seams, and stitching flaws. "
            "Normal cosmetic wear, accidental snags, or shrinkage caused by high-heat washing and drying are excluded. "
            "Contact support with your order ID for replacement or refund requests."
        ),
    },
    {
        "filename": "wireless-bluetooth-headphones.pdf",
        "product_name": "Wireless Bluetooth Headphones",
        "how_to_use": (
            "Press and hold the power button for three seconds until the LED flashes blue to enter pairing mode. "
            "Select 'SimpleAudio Pro' in your device Bluetooth settings. Use the volume rocker to adjust audio levels "
            "and press the multi-function button once to play or pause. Charge with the provided USB-C cable for two hours."
        ),
        "troubleshooting": (
            "If audio drops or Bluetooth disconnects, ensure the headphones are within ten meters of the paired device. "
            "To reset, hold the power and volume down buttons simultaneously for seven seconds until the LED turns red. "
            "If the microphone sounds muffled during phone calls, verify the mic hole is free of dust and debris."
        ),
        "warranty": (
            "Includes a one-year limited hardware warranty against manufacturing defects, internal battery failure, "
            "and driver malfunction. Liquid damage, physical drops, and unauthorized disassembly void all coverage. "
            "Submit warranty claims with your original order receipt through customer support."
        ),
    },
    {
        "filename": "stainless-steel-water-bottle.pdf",
        "product_name": "Stainless Steel Water Bottle",
        "how_to_use": (
            "Rinse thoroughly with warm soapy water before initial use. Suitable for cold beverages up to twenty-four hours "
            "and hot liquids up to twelve hours. Ensure the silicone seal ring inside the screw lid is seated flat before "
            "tightening to guarantee leakproof transport. Hand washing is recommended to protect the exterior powder finish."
        ),
        "troubleshooting": (
            "If liquid leaks from the lid, unscrew and inspect the internal silicone gasket for misalignment or foreign particles. "
            "For residual coffee or tea odors, fill the bottle with warm water and one teaspoon of white vinegar, "
            "soak for thirty minutes, and scrub with a soft bottle brush. Do not freeze or place in a microwave oven."
        ),
        "warranty": (
            "Covered by a lifetime warranty against thermal insulation failure and stainless steel manufacturing defects. "
            "Dents, exterior paint scratches, and missing lid gaskets from normal usage are not covered. "
            "Replacement gaskets are available upon request through our customer care team."
        ),
    },
    {
        "filename": "canvas-everyday-backpack.pdf",
        "product_name": "Canvas Everyday Backpack",
        "how_to_use": (
            "Pack heavier items closest to your back panel for optimal weight balance. Use the padded interior compartment "
            "to secure laptops up to fifteen inches. Adjust shoulder straps evenly so the backpack rests comfortably against "
            "your upper back. Spot clean canvas fabric using a damp cloth and mild neutral soap."
        ),
        "troubleshooting": (
            "If a zipper sticks, rub a graphite pencil tip or beeswax lightly along the zipper teeth to restore smooth travel. "
            "For water marks or surface stains, gently scrub with warm water and air dry away from direct heat. "
            "Do not machine wash or dry clean as this degrades the water-resistant internal fabric lining."
        ),
        "warranty": (
            "Protected by a two-year warranty covering zipper splits, buckle fractures, and strap seam unraveling. "
            "Overloading beyond fifteen kilograms, fabric cuts, chemical spills, and cosmetic discoloration are excluded. "
            "Contact our support portal with clear photos of the damaged area to initiate service."
        ),
    },
    {
        "filename": "ceramic-coffee-mug.pdf",
        "product_name": "Ceramic Coffee Mug",
        "how_to_use": (
            "Safe for hot beverages including freshly brewed coffee, espresso, and herbal tea up to 100 degrees Celsius. "
            "Microwave safe and top-rack dishwasher safe. For longest lasting ceramic glaze brilliance, gentle hand washing "
            "with a non-abrasive sponge is recommended. Allow mug to warm to room temperature before pouring boiling liquids."
        ),
        "troubleshooting": (
            "If stubborn coffee or tea stains build up inside, rub with a paste of baking soda and warm water. "
            "To remove metal flatware marks, use a mild ceramic cleaner. Avoid rapid temperature shocks, such as "
            "placing a hot mug onto cold marble countertops, to prevent hairline thermal cracking."
        ),
        "warranty": (
            "Guaranteed against structural cracking, manufacturing chipping, and glaze defects for ninety days from delivery. "
            "Accidental drops, physical impact breaks, and normal wear and tear are not covered by the warranty. "
            "Replacement requests require order verification and a photograph of the defect."
        ),
    },
]

def generate_pdf(manual_data: dict, output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    notice_style = ParagraphStyle(
        "NoticeStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica-Oblique",
        spaceAfter=12,
    )

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e40af"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10,
    )

    story = [
        Paragraph("Synthetic manual for learning", notice_style),
        Paragraph(f"{manual_data['product_name']} User Manual", title_style),
        Spacer(1, 6),
        Paragraph("How to Use", heading_style),
        Paragraph(manual_data["how_to_use"], body_style),
        Paragraph("Troubleshooting", heading_style),
        Paragraph(manual_data["troubleshooting"], body_style),
        Paragraph("Warranty", heading_style),
        Paragraph(manual_data["warranty"], body_style),
    ]

    doc.build(story)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for manual in MANUALS_DATA:
        file_path = OUTPUT_DIR / manual["filename"]
        generate_pdf(manual, file_path)
        print(f"Generated: {file_path}")

if __name__ == "__main__":
    main()

