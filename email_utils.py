import logging

def send_detection_alert(missing_person, detection):
    """
    Send email alert when a missing person is detected
    Note: Email functionality disabled for now
    """
    try:
        logging.info(f"Email alert would be sent to {missing_person.contact_email} for {missing_person.name}")
        # Email functionality disabled - would normally send email here
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email alert: {str(e)}")
        return False

def send_registration_confirmation(missing_person):
    """
    Send confirmation email when a missing person is registered
    Note: Email functionality disabled for now
    """
    try:
        logging.info(f"Confirmation email would be sent to {missing_person.contact_email} for case MP-{missing_person.id:06d}")
        # Email functionality disabled - would normally send email here
        return True
        
    except Exception as e:
        logging.error(f"Failed to send confirmation email: {str(e)}")
        return False
