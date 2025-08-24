from flask_mail import Message
from app import mail, app
import logging

def send_detection_alert(missing_person, detection):
    """
    Send email alert when a missing person is detected
    """
    try:
        subject = f"ALERT: {missing_person.name} has been detected!"
        
        # Check if this is a high confidence detection (person marked as found)
        status_message = ""
        if detection.confidence_score > 0.5:
            status_message = f"""
        🎉 GREAT NEWS: Due to the high confidence score ({detection.confidence_score:.2%}), 
        we have automatically marked {missing_person.name} as FOUND in our system.
        
        """
        
        body = f"""
        URGENT ALERT - MISSING PERSON DETECTED

        Dear {missing_person.contact_name},

        🚨 IMPORTANT: We have detected a potential match for {missing_person.name} who was reported missing.

        {status_message}DETECTION DETAILS:
        ==================
        📍 Location: {detection.detected_location or 'Location not specified'}
        🕐 Detection Time: {detection.detection_time or 'Just now'}
        📊 Match Confidence: {detection.confidence_score:.1%}
        🆔 Case ID: MP-{missing_person.id:06d}
        📋 Current Status: {missing_person.status.upper()}

        MISSING PERSON INFORMATION:
        ==========================
        👤 Name: {missing_person.name}
        📅 Age: {missing_person.age} years old
        ⚥ Gender: {missing_person.gender}
        🏠 Last Known Location: {missing_person.last_seen_location}
        📆 Last Seen Date: {missing_person.last_seen_date or 'Not specified'}
        📝 Description: {missing_person.description or 'No additional description'}

        IMMEDIATE ACTION REQUIRED:
        =========================
        1. 🚓 Contact local police immediately: 100 (Emergency) or 1091 (Women Helpline)
        2. 📞 Contact the detection location if known
        3. 🚗 Consider going to the detected location safely
        4. 📧 Reply to this email to confirm if this is correct

        CONTACT INFORMATION:
        ===================
        📧 Your Email: {missing_person.contact_email}
        📱 Your Phone: {missing_person.contact_phone}
        🆔 Aadhar: {missing_person.aadhar_number or 'Not provided'}

        IMPORTANT NOTES:
        ===============
        • This detection was made using advanced face recognition technology
        • False positives are possible - please verify before taking action
        • If this is NOT {missing_person.name}, please inform us immediately
        • Keep this information confidential until verified

        SYSTEM INFORMATION:
        ==================
        Detection Source: Missing Person Detection System
        Alert Generated: Automatically upon detection
        System Contact: gauravchauhan292005@gmail.com

        We are committed to reuniting missing persons with their families safely.

        Stay hopeful and take immediate action.

        Best regards,
        Missing Person Detection Team
        Automated Alert System
        """
        
        # Send to both the family contact and system admin
        recipients = [missing_person.contact_email, 'gauravchauhan292005@gmail.com']
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body
        )
        
        mail.send(msg)
        logging.info(f"Alert email sent successfully to {recipients}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email alert: {str(e)}")
        return False

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
