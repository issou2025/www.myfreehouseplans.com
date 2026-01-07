"""
Forms for the core app.
"""
from django import forms
from django.conf import settings
from .models import ContactMessage
import os


class ContactMessageForm(forms.ModelForm):
    """
    Form for users to submit contact messages with optional file attachments.
    """
    
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'subject', 'message', 'attachment']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'required': True
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell us how we can help...',
                'required': True
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.zip'
            })
        }
        labels = {
            'full_name': 'Your Name',
            'email': 'Email Address',
            'subject': 'Subject',
            'message': 'Message',
            'attachment': 'Attach File (Optional)'
        }
        help_texts = {
            'attachment': 'You can attach documents, sketches, or images (PDF, JPG, PNG, ZIP - Max 10MB)'
        }
    
    def clean_attachment(self):
        """
        Validate file upload: check file type and size.
        """
        attachment = self.cleaned_data.get('attachment')
        
        if attachment:
            # Check file size (10MB max)
            if attachment.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                raise forms.ValidationError(
                    f'File size must be under 10MB. Your file is {attachment.size / (1024*1024):.1f}MB.'
                )
            
            # Check file extension
            file_ext = os.path.splitext(attachment.name)[1][1:].lower()
            allowed_types = settings.CONTACT_ALLOWED_FILE_TYPES
            
            if file_ext not in allowed_types:
                raise forms.ValidationError(
                    f'File type .{file_ext} is not allowed. Allowed types: {", ".join(allowed_types)}'
                )
        
        return attachment
    
    def clean_message(self):
        """
        Ensure message has minimum length.
        """
        message = self.cleaned_data.get('message', '')
        if len(message.strip()) < 10:
            raise forms.ValidationError('Please provide a more detailed message (at least 10 characters).')
        return message
