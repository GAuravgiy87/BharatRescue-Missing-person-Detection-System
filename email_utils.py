from flask_mail import Message
from app import mail, app
import logging

def send_detection_alert(missing_person, detection):
    """
    Send email alert when a missing person is detected
    """
    try:
        subject = f"ALERT: {missing_person.name} has been detected!"
        
        body = f"""
        Dear {missing_person.contact_name},

        We have detected a potential match for {missing_person.name} who was reported missing.

        Detection Details:
        - Person: {missing_person.name}
        - Age: {missing_person.age}
        - Gender: {missing_person.gender}
        - Detection Time: {detection.detection_time or 'Just now'}
        - Location: {detection.detected_location or 'Location not specified'}
        - Confidence Score: {detection.confidence_score:.2%}

        Original Report Details:
        - Last Seen: {missing_person.last_seen_location}
        - Last Seen Date: {missing_person.last_seen_date or 'Not specified'}
        - Contact Phone: {missing_person.contact_phone}

        Please contact local authorities immediately if this is indeed {missing_person.name}.

        This is an automated alert from the Missing Person Detection System.
        
        Best regards,
        Missing Person Detection Team
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
        Dear {missing_person.contact_name},

        Your missing person report has been successfully registered in our system.

        Report Details:
        - Case ID: MP-{missing_person.id:06d}
        - Person: {missing_person.name}
        - Age: {missing_person.age}
        - Gender: {missing_person.gender}
        - Last Seen: {missing_person.last_seen_location}
        - Last Seen Date: {missing_person.last_seen_date or 'Not specified'}
        - Registration Date: {missing_person.created_at or 'Just now'}

        Our face recognition system is now actively monitoring for {missing_person.name}. 
        You will receive an immediate email alert if a potential match is detected.

        Important reminders:
        - Contact local police authorities
        - Keep your contact information updated
        - Notify us immediately if {missing_person.name} is found

        We are committed to helping reunite missing persons with their families.

        Best regards,
        Missing Person Detection Team
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
