from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import logging

from app import app, db
from models import MissingPerson, Detection, Admin
from face_recognition_utils import extract_face_encoding, serialize_face_encoding, compare_faces, detect_faces_in_frame
from email_utils import send_detection_alert, send_registration_confirmation

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Landing page"""
    recent_cases = MissingPerson.query.filter_by(status='missing').order_by(MissingPerson.created_at.desc()).limit(6).all()
    total_cases = MissingPerson.query.filter_by(status='missing').count()
    found_cases = MissingPerson.query.filter_by(status='found').count()
    return render_template('index.html', recent_cases=recent_cases, total_cases=total_cases, found_cases=found_cases)

@app.route('/register', methods=['GET', 'POST'])
def register_missing():
    """Register a new missing person"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name') or ''
            age = int(request.form.get('age') or 0)
            gender = request.form.get('gender') or ''
            last_seen_location = request.form.get('last_seen_location') or ''
            last_seen_date_str = request.form.get('last_seen_date') or ''
            last_seen_date = datetime.strptime(last_seen_date_str, '%Y-%m-%d').date()
            description = request.form.get('description') or ''
            contact_name = request.form.get('contact_name') or ''
            contact_email = request.form.get('contact_email') or ''
            contact_phone = request.form.get('contact_phone') or ''
            aadhar_number = request.form.get('aadhar_number') or ''
            
            # Handle file upload
            if 'photo' not in request.files:
                flash('No photo uploaded', 'error')
                return redirect(request.url)
            
            file = request.files['photo']
            if file.filename == '':
                flash('No photo selected', 'error')
                return redirect(request.url)
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(str(file.filename))
                # Add timestamp to filename to avoid conflicts
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract face encoding
                face_encoding = extract_face_encoding(filepath)
                if face_encoding is None:
                    flash('Could not detect a face in the uploaded photo. Please try with a clearer image.', 'error')
                    os.remove(filepath)  # Clean up uploaded file
                    return redirect(request.url)
                
                # Create new missing person record
                missing_person = MissingPerson()
                missing_person.name = name
                missing_person.age = age
                missing_person.gender = gender
                missing_person.last_seen_location = last_seen_location
                missing_person.last_seen_date = last_seen_date
                missing_person.description = description
                missing_person.contact_name = contact_name
                missing_person.contact_email = contact_email
                missing_person.contact_phone = contact_phone
                missing_person.aadhar_number = aadhar_number
                missing_person.photo_filename = filename
                missing_person.face_encoding = serialize_face_encoding(face_encoding)
                
                db.session.add(missing_person)
                db.session.commit()
                
                # Send confirmation email
                send_registration_confirmation(missing_person)
                
                flash(f'Missing person report for {name} has been registered successfully! Case ID: MP-{missing_person.id:06d}', 'success')
                return redirect(url_for('dashboard'))
                
            else:
                flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image.', 'error')
                
        except Exception as e:
            logging.error(f"Error registering missing person: {str(e)}")
            flash('An error occurred while registering the missing person. Please try again.', 'error')
    
    return render_template('register_missing.html')

@app.route('/dashboard')
def dashboard():
    """View all missing persons"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'missing')
    search_query = request.args.get('search', '')
    
    query = MissingPerson.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(MissingPerson.name.contains(search_query))
    
    cases_query = query.order_by(MissingPerson.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Convert cases to dictionaries for JSON serialization
    cases_data = []
    for case in cases_query.items:
        case_dict = {
            'id': case.id,
            'name': case.name,
            'age': case.age,
            'gender': case.gender,
            'last_seen_location': case.last_seen_location,
            'last_seen_date': case.last_seen_date.isoformat() if case.last_seen_date else None,
            'description': case.description,
            'status': case.status,
            'photo_filename': case.photo_filename,
            'contact_name': case.contact_name,
            'contact_email': case.contact_email,
            'contact_phone': case.contact_phone,
            'created_at': case.created_at.isoformat() if case.created_at else None
        }
        cases_data.append(case_dict)
    
    return render_template('dashboard.html', cases=cases_data, cases_pagination=cases_query, status_filter=status_filter, search_query=search_query)

@app.route('/detection', methods=['GET', 'POST'])
def detection():
    """Face detection and matching"""
    if request.method == 'POST':
        try:
            if 'detection_photo' not in request.files:
                flash('No photo uploaded for detection', 'error')
                return redirect(request.url)
            
            file = request.files['detection_photo']
            location = request.form.get('location', 'Unknown location')
            
            if file.filename == '':
                flash('No photo selected', 'error')
                return redirect(request.url)
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(str(file.filename))
                filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                matches = []
                missing_persons = MissingPerson.query.filter_by(status='missing').all()
                
                for person in missing_persons:
                    if person.face_encoding:
                        is_match, confidence = compare_faces(person.face_encoding, filepath)
                        
                        if is_match and confidence > 0.4:  # Threshold for potential match
                            matches.append({
                                'person': person,
                                'confidence': confidence
                            })
                            
                            # Create detection record
                            detection_record = Detection()
                            detection_record.missing_person_id = person.id
                            detection_record.detected_location = location
                            detection_record.confidence_score = confidence
                            db.session.add(detection_record)
                            
                            # Send alert email if confidence is high enough
                            if confidence > 0.6:
                                if send_detection_alert(person, detection_record):
                                    detection_record.notified = True
                
                db.session.commit()
                
                # Clean up detection photo
                os.remove(filepath)
                
                if matches:
                    # Sort by confidence
                    matches.sort(key=lambda x: x['confidence'], reverse=True)
                    flash(f'Found {len(matches)} potential match(es)!', 'success')
                    return render_template('detection.html', matches=matches)
                else:
                    flash('No matches found in the database.', 'info')
                    
            else:
                flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image.', 'error')
                
        except Exception as e:
            logging.error(f"Error during detection: {str(e)}")
            flash('An error occurred during detection. Please try again.', 'error')
    
    return render_template('detection.html')

@app.route('/search')
def search():
    """Search for missing persons"""
    query = request.args.get('q', '')
    gender_filter = request.args.get('gender', '')
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    
    results = MissingPerson.query.filter_by(status='missing')
    
    if query:
        results = results.filter(MissingPerson.name.contains(query))
    
    if gender_filter:
        results = results.filter_by(gender=gender_filter)
    
    if age_min:
        results = results.filter(MissingPerson.age >= age_min)
    
    if age_max:
        results = results.filter(MissingPerson.age <= age_max)
    
    results = results.order_by(MissingPerson.created_at.desc()).all()
    
    return render_template('search.html', results=results, query=query, 
                         gender_filter=gender_filter, age_min=age_min, age_max=age_max)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        flash('Please log in to access admin dashboard', 'error')
        return redirect(url_for('admin_login'))
    
    total_cases = MissingPerson.query.count()
    missing_cases = MissingPerson.query.filter_by(status='missing').count()
    found_cases = MissingPerson.query.filter_by(status='found').count()
    recent_detections = Detection.query.order_by(Detection.detection_time.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         total_cases=total_cases, 
                         missing_cases=missing_cases, 
                         found_cases=found_cases,
                         recent_detections=recent_detections)

@app.route('/admin/surveillance')
def admin_surveillance():
    """Surveillance system for IP cameras"""
    if 'admin_id' not in session:
        flash('Please log in to access surveillance system', 'error')
        return redirect(url_for('admin_login'))
    
    return render_template('surveillance.html')

@app.route('/admin/surveillance/stream')
def surveillance_stream():
    """IP camera stream endpoint"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    camera_ip = request.args.get('ip', '')
    if not camera_ip:
        return jsonify({'error': 'No camera IP provided'}), 400
    
    # Return camera stream URL for mobile IP camera apps
    stream_url = f"http://{camera_ip}:8080/video"
    return jsonify({'stream_url': stream_url})

@app.route('/admin/surveillance/detect', methods=['POST'])
def surveillance_detect():
    """Process surveillance footage for face detection"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        camera_ip = request.json.get('camera_ip', '')
        frame_data = request.json.get('frame_data', '')
        location = request.json.get('location', f'IP Camera {camera_ip}')
        
        if not frame_data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # In a real implementation, you would decode the base64 frame data
        # and process it through face recognition
        # For now, we'll simulate the detection process
        
        matches = []
        missing_persons = MissingPerson.query.filter_by(status='missing').all()
        
        # Simulate face detection (in real implementation, process the actual frame)
        logging.info(f"Processing surveillance frame from {camera_ip} at {location}")
        
        return jsonify({
            'success': True,
            'matches': len(matches),
            'message': f'Processed frame from {location}'
        })
        
    except Exception as e:
        logging.error(f"Error in surveillance detection: {str(e)}")
        return jsonify({'error': 'Detection failed'}), 500

@app.route('/admin/case/<int:case_id>/update_status', methods=['POST'])
def update_case_status():
    """Update case status"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    json_data = request.get_json() or {}
    case_id = json_data.get('case_id')
    new_status = json_data.get('status')
    
    if new_status not in ['missing', 'found', 'closed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    case = MissingPerson.query.get_or_404(case_id)
    case.status = new_status
    case.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Case status updated to {new_status}'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Create default admin user if none exists
def create_default_admin():
    with app.app_context():
        if Admin.query.count() == 0:
            admin = Admin()
            admin.username = 'gaurav'
            admin.email = 'gauravchauhan292005@gmail.com'
            admin.set_password('gauravacess')
            db.session.add(admin)
            db.session.commit()
            logging.info("Default admin user created: gaurav/gauravacess")

# Initialize default admin after app context is available
create_default_admin()
