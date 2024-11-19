from django import forms

class ImageUploadForm(forms.Form):
    original_image = forms.ImageField(label="Select Image")
    
    COMPRESSION_CHOICES = [
        ('transform', 'Transform Coding'),
        ('rle', 'Run-Length Encoding'),
        ('deflate', 'Deflate'),
        ('jpeg', 'JPEG'),
        ('jpeg2000', 'JPEG 2000'),
    ]
    
    compression_type = forms.ChoiceField(choices=COMPRESSION_CHOICES, label="Compression Type")
