# Contact Form Enhancement - Testing Guide

## ✅ Implementation Complete!

### What Was Added:

1. **ContactMessage Model** - Stores all contact submissions with optional file attachments
2. **ContactMessageForm** - Django form with file upload validation
3. **Enhanced Contact View** - Handles file uploads and sends email notifications
4. **Modern Contact Template** - File upload field + WhatsApp button
5. **Admin Interface** - View and manage contact messages
6. **Email Notifications** - Admin receives emails with attachments

### File Upload Features:
- **Allowed Types**: PDF, JPG, JPEG, PNG, ZIP
- **Max Size**: 10MB
- **Security**: Server-side validation, sanitized filenames
- **Storage**: `media/contact_uploads/` directory

### WhatsApp Integration:
- **Number**: +22796380877
- **Click-to-chat**: https://wa.me/22796380877
- **Green button** with WhatsApp branding

---

## 🧪 How to Test:

### 1. Visit Contact Page
Navigate to: **http://127.0.0.1:8000/contact/**

### 2. Test Form Submission (No File)
- Fill in all required fields
- Leave attachment empty
- Submit form
- Check console for email output

### 3. Test File Upload
- Fill in all fields
- Upload a PDF, image, or ZIP file (under 10MB)
- Submit form
- Check: `media/contact_uploads/` folder for the file

### 4. Test File Validation
- Try uploading a .exe or .txt file (should fail)
- Try uploading a file over 10MB (should fail)
- Error messages should display

### 5. Test WhatsApp Button
- Click the green "Start WhatsApp Chat" button
- Should open WhatsApp with pre-filled message
- Works on mobile and desktop

### 6. View in Admin
- Go to: **http://127.0.0.1:8000/admin/**
- Click "Contact Messages"
- See submitted messages with file info
- Click "Download" to get attached files
- Click "Reply" to email sender

---

## 📧 Email Configuration

Currently using **console backend** (emails print to terminal).

To send real emails in production, update `config/settings/base.py`:

```python
# For Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password, not regular password
```

Or use your hosting provider's SMTP settings.

---

## 📁 Files Created/Modified:

### New Files:
1. `apps/core/models.py` - ContactMessage model
2. `apps/core/forms.py` - ContactMessageForm with validation
3. `apps/core/migrations/0001_initial.py` - Database migration

### Modified Files:
1. `apps/core/views.py` - Enhanced ContactView with file upload
2. `apps/core/admin.py` - Admin interface for messages
3. `apps/core/templates/core/contact.html` - Updated template
4. `config/settings/base.py` - Added email & file upload settings

---

## 🔒 Security Features:

✅ **File Type Validation** - Only allows safe file types
✅ **File Size Limit** - 10MB maximum
✅ **Filename Sanitization** - Removes dangerous characters
✅ **Unique Filenames** - Timestamps prevent collisions
✅ **Server-side Validation** - Can't be bypassed by client
✅ **IP Logging** - Track submission source
✅ **User Agent Logging** - Identify browser/device

---

## 📱 Mobile-Friendly:

- Responsive form layout
- Touch-friendly buttons
- WhatsApp deep-linking
- File picker works on mobile
- Camera upload on mobile devices

---

## 🎨 UI Features:

- Green WhatsApp card with official branding
- File upload field with help text
- Privacy assurance message
- Success/error feedback
- Icon-based labeling
- Modern gradient design

---

## 👨‍💼 Admin Features:

- View all contact messages
- Filter by subject, read status, date
- Search by name, email, message
- Download attached files
- Quick reply via mailto link
- Mark as read/unread
- Add admin notes
- View IP address & user agent

---

## 🚀 Next Steps (Optional):

1. **Email Templates**: Create HTML email templates for better formatting
2. **Auto-reply**: Send confirmation email to users
3. **File Preview**: Show image thumbnails in admin
4. **Export**: Add CSV export for contact messages
5. **Spam Protection**: Add reCAPTCHA or honeypot field
6. **Rate Limiting**: Prevent abuse with throttling
7. **Real SMTP**: Configure production email settings

---

## 📞 Support Contact:

- **Email**: entreprise2rc@gmail.com
- **WhatsApp**: +22796380877

---

**Status**: ✅ Fully Functional
**Tested**: Form submission, file upload, validation
**Ready**: For production use (configure SMTP first)
