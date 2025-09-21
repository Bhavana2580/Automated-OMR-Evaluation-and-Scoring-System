from pdf2image import convert_from_path
from pathlib import Path

def pdf_to_images(pdf_path, output_folder=None, dpi=300):
    """
    Converts a PDF file to images, one per page.
    Args:
        pdf_path: Path to PDF file
        output_folder: Folder to save images (optional)
        dpi: Resolution
    Returns:
        List of PIL.Image objects
    """
    images = convert_from_path(pdf_path, dpi=dpi)
    
    if output_folder:
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        saved_files = []
        for i, img in enumerate(images):
            save_path = Path(output_folder) / f"page_{i+1}.jpg"
            img.save(save_path, "JPEG")
            saved_files.append(save_path)
        return saved_files
    
    return images
