"""
ToxinSolutions — Backend API Server
Built with Flask + Python
Handles: Contact forms, Newsletter subscriptions, Analytics
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import json
import os
import re

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ─── Data Storage (JSON file-based for simplicity) ───
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

CONTACTS_FILE = os.path.join(DATA_DIR, 'contacts.json')
NEWSLETTER_FILE = os.path.join(DATA_DIR, 'newsletter.json')


def load_data(filepath):
    """Load data from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


def save_data(filepath, data):
    """Save data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ─── Routes ───

@app.route('/')
def index():
    """Serve the main website."""
    return send_file('index.html')


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static asset files."""
    return send_from_directory('assets', filename)


@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions."""
    try:
        data = request.get_json()

        # Validation
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        service = data.get('service', '').strip()
        budget = data.get('budget', '').strip()
        message = data.get('message', '').strip()

        if not name or len(name) < 2:
            return jsonify({'error': 'Name is required (min 2 characters)'}), 400

        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400

        if not message or len(message) < 10:
            return jsonify({'error': 'Message is required (min 10 characters)'}), 400

        # Save contact
        contacts = load_data(CONTACTS_FILE)
        contact_entry = {
            'id': len(contacts) + 1,
            'name': name,
            'email': email,
            'phone': phone,
            'service': service,
            'budget': budget,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'new',
            'ip': request.remote_addr
        }
        contacts.append(contact_entry)
        save_data(CONTACTS_FILE, contacts)

        print(f"✅ New contact from: {name} ({email})")

        return jsonify({
            'success': True,
            'message': 'Thank you for reaching out! We will get back to you within 24 hours.'
        }), 200

    except Exception as e:
        print(f"❌ Contact form error: {str(e)}")
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500


@app.route('/api/newsletter', methods=['POST'])
def newsletter():
    """Handle newsletter subscriptions."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400

        subscribers = load_data(NEWSLETTER_FILE)

        # Check for duplicates
        if any(sub['email'] == email for sub in subscribers):
            return jsonify({'message': 'You are already subscribed!'}), 200

        subscriber = {
            'id': len(subscribers) + 1,
            'email': email,
            'subscribed_at': datetime.now().isoformat(),
            'active': True
        }
        subscribers.append(subscriber)
        save_data(NEWSLETTER_FILE, subscribers)

        print(f"📧 New subscriber: {email}")

        return jsonify({
            'success': True,
            'message': 'Welcome aboard! You\'re now subscribed to our newsletter.'
        }), 200

    except Exception as e:
        print(f"❌ Newsletter error: {str(e)}")
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Retrieve all contact submissions (admin endpoint)."""
    contacts = load_data(CONTACTS_FILE)
    return jsonify({
        'total': len(contacts),
        'contacts': contacts
    }), 200


@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Retrieve all newsletter subscribers (admin endpoint)."""
    subscribers = load_data(NEWSLETTER_FILE)
    return jsonify({
        'total': len(subscribers),
        'subscribers': subscribers
    }), 200


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ToxinSolutions API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200


# ─── Catch-all for SPA routing ───
@app.route('/<path:path>')
def catch_all(path):
    """Serve static files or fall back to index."""
    if os.path.exists(path):
        return send_file(path)
    return send_file('index.html')


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║     🚀 ToxinSolutions Server is Running!         ║
    ║     → http://localhost:3000                       ║
    ║     → API: http://localhost:3000/api/health       ║
    ╚═══════════════════════════════════════════════════╝
    """)
    app.run(debug=True, port=3000, host='0.0.0.0')
