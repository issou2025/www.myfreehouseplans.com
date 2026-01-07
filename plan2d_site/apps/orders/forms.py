"""
Forms for order processing and receipt uploads.
"""
from django import forms
from .models import Order
from django.core.exceptions import ValidationError


class ReceiptUploadForm(forms.ModelForm):
    """
    Form for uploading payment receipt.
    """
    class Meta:
        model = Order
        fields = ['buyer_email', 'buyer_name', 'payment_method', 'receipt_file']
        widgets = {
            'buyer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'required': True
            }),
            'buyer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'receipt_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf',
                'required': True
            })
        }
        labels = {
            'buyer_email': 'Your Email Address',
            'buyer_name': 'Your Full Name (Optional)',
            'payment_method': 'Payment Method Used',
            'receipt_file': 'Payment Receipt',
        }
        help_texts = {
            'buyer_email': 'We\'ll send your download link here after verification',
            'payment_method': 'Select which payment method you used',
            'receipt_file': 'Upload screenshot or PDF of your payment confirmation (max 10MB)',
        }
    
    def clean_receipt_file(self):
        """Validate uploaded receipt file."""
        receipt = self.cleaned_data.get('receipt_file')
        
        if receipt:
            # Check file size (max 10MB)
            if receipt.size > 10 * 1024 * 1024:
                raise ValidationError('Receipt file size cannot exceed 10MB.')
            
            # Check file type
            allowed_types = [
                'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
                'application/pdf'
            ]
            if receipt.content_type not in allowed_types:
                raise ValidationError(
                    'Only image files (JPEG, PNG, GIF) and PDF are allowed.'
                )
        
        return receipt
