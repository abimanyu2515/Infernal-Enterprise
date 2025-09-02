from django.shortcuts import render


import cv2
import numpy as np
import os
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

# Reference object known width in cm
KNOWN_WIDTH_CM = 8.5

def find_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_pixel_to_cm_ratio(reference_image_path, known_width_cm=KNOWN_WIDTH_CM):
    image = cv2.imread(reference_image_path)
    contours = find_contours(image)

    if not contours:
        return None

    reference_contour = max(contours, key=cv2.contourArea)
    _, _, w, h = cv2.boundingRect(reference_contour)
    pixel_width = max(w, h)
    
    return known_width_cm / pixel_width

def measure_shirt_armpit_width(shirt_image_path, pixel_to_cm_ratio):
    image = cv2.imread(shirt_image_path)
    contours = find_contours(image)

    if not contours:
        return None

    shirt_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(shirt_contour)

    armpit_y = int(y + h * 0.6)
    horizontal_edges = cv2.Canny(image[armpit_y:armpit_y + 5, :], 50, 150)
    armpit_contours, _ = cv2.findContours(horizontal_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not armpit_contours:
        return None

    min_x = image.shape[1]
    max_x = 0

    for contour in armpit_contours:
        for point in contour:
            px, _ = point[0]
            min_x = min(min_x, px)
            max_x = max(max_x, px)

    chest_width_pixels = max_x - min_x
    return chest_width_pixels * pixel_to_cm_ratio

def suggest_size(size_inches):
    size_chart = {
        "S": (0, 38), "M": (39, 40), "L": (41, 42), "XL": (43, 44),
        "2XL": (45, 46), "3XL": (47, 48), "4XL": (49, 50), "5XL": (51, 52),
        "6XL": (53, 54), "7XL": (55, 56), "8XL": (57, 58)
    }
    threshold = 5

    for size, (min_inches, max_inches) in size_chart.items():
        if min_inches <= size_inches <= max_inches:
            if size_inches >= max_inches - threshold:
                next_size = next((s for s in size_chart if size_chart[s][0] == max_inches + 1), None)
                return next_size if next_size else size
            return size

    return "Size not available"

@api_view(['POST'])
def measure_shirt_size(request):
    parser_classes = [MultiPartParser, FormParser]

    if 'shirt_image' not in request.FILES:
        return Response({'error': 'Shirt image file is required'}, status=400)

    shirt_image = request.FILES['shirt_image']
    shirt_image_path = os.path.join(settings.MEDIA_ROOT, 'shirt_image.png')

    # Save the uploaded image
    with open(shirt_image_path, 'wb') as f:
        for chunk in shirt_image.chunks():
            f.write(chunk)

    # Reference image path
    reference_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'reference.png')
    pixel_to_cm_ratio = get_pixel_to_cm_ratio(reference_image_path)

    if pixel_to_cm_ratio is None:
        return Response({'error': 'Failed to determine pixel-to-cm ratio'}, status=400)

    chest_width_cm = measure_shirt_armpit_width(shirt_image_path, pixel_to_cm_ratio)

    if chest_width_cm is None:
        return Response({'error': 'Failed to detect chest width'}, status=400)

    chest_width_inches = chest_width_cm / 2.54 * 2
    suggested_size = suggest_size(chest_width_inches)

    return Response({
        'chest_width_cm': round(chest_width_cm, 2),
        'chest_width_inches': round(chest_width_inches, 2),
        'suggested_size': suggested_size
    })
