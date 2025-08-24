from flask_mail import Message
from app import mail, app
import logging
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

def send_detection_alert_with_image(missing_person, detection, detection_image_path=None):
    """
    Send email alert when a missing person is detected, with captured image if available
    """
    try:
        # Use Gmail SMTP directly for better reliability
        gmail_user = "gauravchauhan292005@gmail.com"
        gmail_password = "YOUR_16_CHAR_APP_PASSWORD_HERE"  # Replace with the 16-character App Password from Google
        
        subject = f"🚨 ALERT: {missing_person.name} has been FOUND!"
        
        # Check if this is a high confidence detection (person marked as found)
        status_message = ""
        if detection.confidence_score > 0.5:
            status_message = f"""
🎉 EXCELLENT NEWS: Due to the high confidence score ({detection.confidence_score:.1%}), 
we have automatically marked {missing_person.name} as FOUND in our system!

"""
        
        body = f"""
URGENT ALERT - MISSING PERSON FOUND!

Dear {missing_person.contact_name},

🎉 WONDERFUL NEWS: We have successfully located {missing_person.name}!

{status_message}DETECTION DETAILS:
==================
📍 Found at Location: {detection.detected_location or 'Location being verified'}
🕐 Detection Time: {detection.detection_time or 'Just now'}
📊 Match Confidence: {detection.confidence_score:.1%}
🆔 Case ID: MP-{missing_person.id:06d}
📋 Current Status: FOUND ✅

MISSING PERSON INFORMATION:
==========================
👤 Name: {missing_person.name}
📅 Age: {missing_person.age} years old
⚥ Gender: {missing_person.gender}
🏠 Originally Last Seen: {missing_person.last_seen_location}
📆 Last Seen Date: {missing_person.last_seen_date or 'Not specified'}

IMMEDIATE ACTION REQUIRED:
=========================
1. 🚓 Contact local police immediately: 100 (Emergency)
2. 📞 Go to the detected location: {detection.detected_location}
3. 🚗 Coordinate with authorities for safe recovery
4. 📧 Reply to confirm when you've reached the location

CONTACT INFORMATION:
===================
📧 Your Email: {missing_person.contact_email}
📱 Your Phone: {missing_person.contact_phone}
🆔 Case Reference: MP-{missing_person.id:06d}

IMPORTANT NOTES:
===============
• Our advanced face recognition system detected this match
• A detection image is attached to this email for verification
• Please verify the identity before approaching
• Contact authorities to assist with safe recovery

SYSTEM INFORMATION:
==================
Detection Source: Missing Person Detection System
Alert Generated: Automatically upon detection
System Contact: gauravchauhan292005@gmail.com
Detection Location: {detection.detected_location}

🎉 WE ARE THRILLED TO HELP REUNITE YOUR FAMILY! 🎉

Best regards,
Missing Person Detection Team
Automated Alert System
"""
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = missing_person.contact_email
        msg['Cc'] = gmail_user  # CC yourself
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach detection image if available
        if detection_image_path and os.path.exists(detection_image_path):
            try:
                with open(detection_image_path, 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-Disposition', f'attachment; filename="detection_{missing_person.name}_{detection.id}.jpg"')
                msg.attach(image)
                logging.info(f"Attached detection image: {detection_image_path}")
            except Exception as e:
                logging.error(f"Failed to attach image: {str(e)}")
        
        # Attach original missing person photo for comparison
        original_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], missing_person.photo_filename)
        if os.path.exists(original_photo_path):
            try:
                with open(original_photo_path, 'rb') as f:
                    img_data = f.read()
                original_image = MIMEImage(img_data)
                original_image.add_header('Content-Disposition', f'attachment; filename="original_{missing_person.name}.jpg"')
                msg.attach(original_image)
                logging.info(f"Attached original photo: {original_photo_path}")
            except Exception as e:
                logging.error(f"Failed to attach original photo: {str(e)}")
        
        # Send email using Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, [missing_person.contact_email, gmail_user], text)
        server.quit()
        
        logging.info(f"🎉 DETECTION ALERT SENT: {missing_person.name} found at {detection.detected_location}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send detection email: {str(e)}")
        # Fallback to basic notification
        try:
            logging.info(f"📧 FALLBACK: Attempting basic email notification")
            basic_msg = Message(
                subject=f"ALERT: {missing_person.name} FOUND!",
                recipients=[missing_person.contact_email, 'gauravchauhan292005@gmail.com'],
                body=f"URGENT: {missing_person.name} has been found at {detection.detected_location} with {detection.confidence_score:.1%} confidence. Contact local authorities immediately!"
            )
            mail.send(basic_msg)
            return True
        except Exception as e2:
            logging.error(f"Fallback email also failed: {str(e2)}")
            return False

def send_detection_alert(missing_person, detection):
    """
    Wrapper function for backward compatibility
    """
    return send_detection_alert_with_image(missing_person, detection)

def send_registration_confirmation(missing_person):
    """
    Send confirmation email when a missing person is registered
    """
    try:
        subject = f"Missing Person Report Registered - {missing_person.name}"
        
        body = f"""
        MISSING PERSON REPORT SUCCESSFULLY REGISTERED

        Dear {missing_person.contact_name},

        ✅ Your missing person report has been successfully registered in our system.

        CASE INFORMATION:
        ================
        🆔 Case ID: MP-{missing_person.id:06d}
        👤 Missing Person: {missing_person.name}
        📅 Age: {missing_person.age} years old
        ⚥ Gender: {missing_person.gender}
        🏠 Last Seen Location: {missing_person.last_seen_location}
        📆 Last Seen Date: {missing_person.last_seen_date or 'Not specified'}
        📝 Description: {missing_person.description or 'No additional description'}
        ⏰ Report Registered: {missing_person.created_at or 'Just now'}

        CONTACT DETAILS ON FILE:
        =======================
        📧 Email: {missing_person.contact_email}
        📱 Phone: {missing_person.contact_phone}
        🆔 Aadhar: {missing_person.aadhar_number or 'Not provided'}

        WHAT HAPPENS NEXT:
        =================
        🔍 Our advanced face recognition system is now actively monitoring for {missing_person.name}
        📧 You will receive IMMEDIATE email alerts for any potential matches
        📊 Detection confidence scores help determine likelihood of matches
        🚨 High-confidence matches (>50%) automatically trigger urgent alerts

        IMMEDIATE ACTIONS YOU SHOULD TAKE:
        =================================
        1. 🚓 File a formal police complaint immediately
        2. 📢 Share this information with local community groups
        3. 📱 Post on social media with #{missing_person.name}Missing hashtag
        4. 📋 Contact local hospitals and shelters
        5. 🗞️ Consider contacting local news media

        IMPORTANT EMERGENCY CONTACTS:
        ============================
        🚨 Police Emergency: 100
        👩‍⚕️ Women Helpline: 1091
        🧒 Child Helpline: 1098
        🆘 Disaster Management: 108

        SYSTEM FEATURES:
        ===============
        • 24/7 automated face recognition monitoring
        • Real-time alert system via email
        • Database accessible to authorities
        • Privacy-protected secure system

        IMPORTANT REMINDERS:
        ===================
        ⚠️ Keep your contact information updated
        ⚠️ Notify us IMMEDIATELY if {missing_person.name} is found
        ⚠️ Respond to detection alerts quickly for best results
        ⚠️ Share case ID: MP-{missing_person.id:06d} with authorities

        We understand this is a difficult time for your family. Our system works around the clock to help locate missing persons and reunite families.

        Stay strong and don't lose hope.

        Best regards,
        Missing Person Detection Team
        Email: gauravchauhan292005@gmail.com
        Case Reference: MP-{missing_person.id:06d}
        """
        
        # Send to both the family contact and system admin
        recipients = [missing_person.contact_email, 'gauravchauhan292005@gmail.com']
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body
        )
        
        mail.send(msg)
        logging.info(f"Confirmation email sent successfully to {recipients}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send confirmation email: {str(e)}")
        return False
