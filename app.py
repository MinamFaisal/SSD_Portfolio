from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask app and configure SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'
db = SQLAlchemy(app)

# Database Model for User Portfolio
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(15))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    image_filename = db.Column(db.String(100))

# Create database tables if they don’t exist
with app.app_context():
    db.create_all()

# Home Page Route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        bio = request.form.get('bio')
        skills = request.form.get('skills')
        linkedin = request.form.get('linkedin')
        github = request.form.get('github')

        # Handle image upload
        image = request.files.get('image')  # Make sure this matches the input name
        image_filename = None

        if image and image.filename:  # Check if an image was uploaded
            image_filename = image.filename
            # Save the image to the upload folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            print(f"Image saved as: {image_filename}")  # Debugging output
        else:
            print("No image uploaded or filename is empty.")  # Debugging output

        # Save user data to the database
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            bio=bio,
            skills=skills,
            linkedin=linkedin,
            github=github,
            image_filename=image_filename
        )
        db.session.add(user)
        db.session.commit()

        flash('Portfolio created successfully!', 'success')
        return redirect(url_for('view_portfolio', user_id=user.id))

    return render_template('form.html')


# Portfolio Page Route
@app.route('/portfolio/<int:user_id>')
def view_portfolio(user_id):
    user = User.query.get_or_404(user_id)
    
    # Set default placeholder if no image is uploaded
    if user.image_filename:
        image_url = url_for('static', filename=f'images/{user.image_filename}')
    else:
        image_url = url_for('static', filename='images/placeholder.png')

    print(f"Image URL: {image_url}")  # Debugging output

    return render_template('portfolio.html', user=user, image_url=image_url)


# Database Model for Contact Messages
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Create database tables if they don’t exist
with app.app_context():
    db.create_all()

# Contact Page Route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form['name']
        message = request.form['message']
        
        # Save contact message to the database
        contact_message = ContactMessage(name=name, message=message)
        db.session.add(contact_message)
        db.session.commit()
        
        flash(f'Thank you, {name}. Your message has been received!', 'info')
        return redirect(url_for('home'))

    return render_template('contact.html')




# Run the application
if __name__ == '__main__':
    app.run(debug=True)
