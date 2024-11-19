import os
import cv2
import numpy as np
import zlib
from collections import Counter
from heapq import heapify, heappop, heappush
from django.shortcuts import render
from django.conf import settings
from PIL import Image
from .forms import ImageUploadForm
from .arithmeticcoding import ArithmeticEncoder, ArithmeticDecoder  

from django.core.exceptions import ValidationError

def validate_image(file):
    try:
        Image.open(file)
    except (IOError, OSError):
        raise ValidationError("The file is not a valid image.")


# JPEG Compression for reduced size
def jpeg_compression(input_path, output_path, quality=50):
    """Compress the image using JPEG compression with specified quality."""
    image = Image.open(input_path)
    image.save(output_path, 'JPEG', quality=quality)
    return os.path.getsize(input_path), os.path.getsize(output_path)

def transform_coding(input_path, output_path):
    """Compress the image using Discrete Cosine Transform (DCT) and quantization."""
    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Ensure the file exists and is a valid image.")
    
    # Downscale the image to reduce size before compression
    image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))  # Downscale by half
    
    # Normalize the image
    image_float = np.float32(image) / 255.0
    
    # Apply DCT
    dct = cv2.dct(image_float)
    
    # Quantization: Discard small DCT coefficients (lower threshold for more compression)
    threshold = 0.01  # Lowering this for better compression
    dct[np.abs(dct) < threshold] = 0
    
    # Perform Inverse DCT to get the compressed image
    compressed_image = cv2.idct(dct) * 255.0
    compressed_image = np.clip(compressed_image, 0, 255).astype(np.uint8)
    
    # Save the compressed image
    cv2.imwrite(output_path, compressed_image)

def run_length_encoding(input_path, output_path):
    """Compress the image using Run-Length Encoding."""
    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Ensure the file exists and is a valid image.")

    flat = image.flatten()
    encoded = []
    count = 1

    for i in range(1, len(flat)):
        if flat[i] == flat[i - 1]:
            count += 1
        else:
            encoded.append((flat[i - 1], count))
            count = 1
    encoded.append((flat[-1], count))

    # Save as a new image with RLE data
    decoded = np.concatenate([[pixel] * count for pixel, count in encoded])
    decoded = decoded.reshape(image.shape)
    cv2.imwrite(output_path, decoded)


def deflate_compression(input_path, output_path):
    """Compress the image using Deflate algorithm."""
    with open(input_path, 'rb') as f:
        data = f.read()

    compressed_data = zlib.compress(data)
    
    with open(output_path, 'wb') as f:
        f.write(compressed_data)

from PIL import Image

def jpeg2000_compress(input_path, output_path, quality=20):
    """Compress the image using JPEG2000 compression with specified quality."""
    image = Image.open(input_path)
    
    # Convert image to RGB if it is not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save the image in JPEG2000 format
    image.save(output_path, format='JPEG2000', quality_mode='web', quality_layers=[quality])
    return os.path.getsize(input_path), os.path.getsize(output_path)

def compress_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES['original_image']
            compression_type = form.cleaned_data['compression_type']
            original_path = os.path.join(settings.MEDIA_ROOT, uploaded_image.name)
            compressed_path = os.path.join(settings.MEDIA_ROOT, 'compressed_' + uploaded_image.name)

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with open(original_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            # Initialize default sizes to avoid UnboundLocalError
            original_size = os.path.getsize(original_path)
            compressed_size = 0

            # Call the appropriate compression function
            if compression_type == 'jpeg':
                original_size, compressed_size = jpeg_compression(original_path, compressed_path, quality=50)
            elif compression_type == 'transform':
                transform_coding(original_path, compressed_path)
                compressed_size = os.path.getsize(compressed_path)
            elif compression_type == 'rle':
                run_length_encoding(original_path, compressed_path)
                compressed_size = os.path.getsize(compressed_path)
            elif compression_type == 'deflate':
                deflate_compression(original_path, compressed_path)
                compressed_size = os.path.getsize(compressed_path)
            elif compression_type == 'jpeg2000':
                original_size, compressed_size = jpeg2000_compress(original_path, compressed_path, quality=20)

            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            return render(request, 'result.html', {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compressed_image_url': os.path.join(settings.MEDIA_URL, 'compressed_' + uploaded_image.name),
            })
    else:
        form = ImageUploadForm()

    return render(request, 'index.html', {'form': form})
