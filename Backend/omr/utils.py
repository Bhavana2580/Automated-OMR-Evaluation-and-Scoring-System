import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

def load_image(path):
    return cv2.imread(path)

def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def save_image(path, image):
    cv2.imwrite(path, image)
