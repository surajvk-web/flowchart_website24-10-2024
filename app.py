from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['flowchart_database']
users_collection = db['users']
collection = db['entries']

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        if users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Insert user data into MongoDB
        users_collection.insert_one({'username': username, 'password': password})
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user credentials
        user = users_collection.find_one({'username': username, 'password': password})

        if user:
            session['username'] = username
            return redirect(url_for('new_entry'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html')

# New Entry Page (Requires login)
@app.route('/new_entry')
def new_entry():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('new_entry.html')


@app.route('/save_entry', methods=['POST'])
def save_entry():
    data = request.json
    
    # Extract and handle the 'entry_date' field
    entry_date = data.get('entry_date')
    
    # Convert string date to a datetime object, then format it to 'dd-mm-yyyy'
    if entry_date:
        try:
            # Assuming the input date is in 'yyyy-mm-dd' format from the front-end
            parsed_date = datetime.strptime(entry_date, '%Y-%m-%d')
            # Format the parsed date to 'dd-mm-yyyy'
            formatted_date = parsed_date.strftime('%d-%m-%Y')
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format, expected YYYY-MM-DD'}), 400
    else:
        # If no date is provided, use the current date in 'dd-mm-yyyy' format
        formatted_date = datetime.now().strftime('%d-%m-%Y')

    # Prepare the data to be saved in MongoDB
    entry_data = {
        'entry_date': formatted_date,  # Save the formatted date ('dd-mm-yyyy')
        'total_subject': data.get('total_subject'),
        'screening_eligibility': data.get('screening_eligibility'),
        'eligible_enrollment': data.get('eligible_enrollment'),
        'consent_enrolled': data.get('consent_enrolled'),
        'images': data.get('images'),
        'forehead': data.get('forehead'),
        'sternum': data.get('sternum'),
        'abdomen': data.get('abdomen'),
        'hips_thighs': data.get('hips_thighs'),
        'legs': data.get('legs'),
        'palm': data.get('palm'),
        'soles': data.get('soles'),
        'clips_videos': data.get('clips_videos'),
        'clip_forehead': data.get('clip_forehead'),
        'clip_sternum': data.get('clip_sternum'),
        'clip_abdomen': data.get('clip_abdomen'),
        'clip_hips_thighs': data.get('clip_hips_thighs'),
        'clip_legs': data.get('clip_legs'),
        'clip_palm': data.get('clip_palm'),
        'clip_soles': data.get('clip_soles'),
        'consent_refused': data.get('consent_refused'),
        'total_consent_refused': data.get('total_consent_refused'),
        'reason_1': data.get('reason_1'),
        'reason_2': data.get('reason_2')
    }

    # Insert the data into MongoDB
    try:
        entry_id = collection.insert_one(entry_data).inserted_id
        return jsonify({'success': True, 'entry_id': str(entry_id)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_entry', methods=['GET', 'POST'])
def edit_entry():
    query = {}
    entries = []

    if request.method == 'POST':
        entry_date = request.form.get('entry_date')
        month = request.form.get('month')
        year = request.form.get('year')
        search_year = request.form.get('search_year')

        # Date-wise search
        if entry_date:
            try:
                # Parse date and format to match stored format
                parsed_date = datetime.strptime(entry_date, '%d/%m/%Y')
                formatted_date = parsed_date.strftime('%d-%m-%Y')
                query = {"entry_date": formatted_date}
            except ValueError:
                return "Invalid date format. Please use DD/MM/YYYY.", 400

        # Month-wise search
        elif month and year:
            try:
                start_date = datetime.strptime(f"01/{month}/{year}", '%d/%m/%Y')
                next_month = start_date.replace(day=28) + timedelta(days=4)  # get next month
                end_date = next_month - timedelta(days=next_month.day)  # last day of current month
                query = {
                    "entry_date": {
                        "$gte": start_date.strftime('%d-%m-%Y'),
                        "$lte": end_date.strftime('%d-%m-%Y')
                    }
                }
            except ValueError:
                return "Invalid month or year.", 400

        # Year-wise search
        elif search_year:
            try:
                start_date = datetime.strptime(f"01/01/{search_year}", '%d/%m/%Y')
                end_date = datetime.strptime(f"31/12/{search_year}", '%d/%m/%Y')
                query = {
                    "entry_date": {
                        "$gte": start_date.strftime('%d-%m-%Y'),
                        "$lte": end_date.strftime('%d-%m-%Y')
                    }
                }
            except ValueError:
                return "Invalid year.", 400

        # Fetch entries based on the query
        entries = list(collection.find(query))

    # Render the template with search results
    return render_template('edit_entry.html', entries=entries)



@app.route('/edit_entry/<entry_id>', methods=['GET', 'POST'])
def edit_specific_entry(entry_id):
    # Find the entry by ID
    entry = collection.find_one({'_id': ObjectId(entry_id)})

    if request.method == 'POST':
        # Update the document with new values from the form
        updated_data = {

            'total_subject': request.form.get('total_subject'),
            'screening_eligibility': request.form.get('screening-eligibility'),
            # <input type="text" id="input-screening-eligibility" name="screening-eligibility" value="{{ entry.screening_eligibility }}"><br>
            # request.form.get main "name wali value lete hai"
            'eligible_enrollment': request.form.get('eligible-enrollment'),
            'consent_enrolled': request.form.get('consent-enrolled'),
            'images': request.form.get('images'),
            'forehead': request.form.get('forehead'),
            'sternum': request.form.get('sternum'),
            'abdomen': request.form.get('abdomen'),
            'hips_thighs': request.form.get('hips-thighs'),
            'legs': request.form.get('legs'),
            'palm': request.form.get('palm'),
            'soles': request.form.get('soles'),
            'clips_videos': request.form.get('clips-videos'),
            'consent_refused': request.form.get('consent-refused'),
            'total_consent_refused': request.form.get('total-consent-refused'),
            'reason_1': request.form.get('reason-1'),
            'reason_2': request.form.get('reason-2'),
            'clip_forehead': request.form.get('clip-forehead'),
            'clip_sternum': request.form.get('clip-sternum'),
            'clip_abdomen': request.form.get('clip-abdomen'),
            'clip_hips_thighs': request.form.get('clip-hips-thighs'),
            'clip_legs': request.form.get('clip-legs'),
            'clip_palm': request.form.get('clip-palm'),
            'clip_soles': request.form.get('clip-soles'),
        }

        # Update the entry in MongoDB
        collection.update_one({'_id': ObjectId(entry_id)}, {"$set": updated_data})

        # Flash a success message
        flash('Your data has been edited/updated.')

        return redirect('/edit_entry')  # Redirect to the list of entries after updating

    return render_template('edit_specific_entry.html', entry=entry)


@app.route('/view_entries', methods=['GET', 'POST'])
def view_entries():
    if request.method == 'POST':
        entry_date = request.form.get('entry_date')
        month = request.form.get('month')
        year = request.form.get('year')

        query = {}
        selected_date = None
        selected_month = None
        selected_year = None

        # Date-wise search
        if entry_date:
            try:
                # Parse the date from DD/MM/YYYY format
                parsed_date = datetime.strptime(entry_date, '%d/%m/%Y')
                formatted_date = parsed_date.strftime('%d-%m-%Y')
                query = {"entry_date": formatted_date}
                selected_date = formatted_date
            except ValueError:
                return "Invalid date format. Please use DD/MM/YYYY.", 400

        # Month and Year-wise search using date ranges
        elif month and year:
            try:
                # Create start and end dates for the selected month and year
                start_date = datetime.strptime(f"01/{month}/{year}", '%d/%m/%Y')
                next_month = start_date.replace(day=28) + timedelta(days=4)  # get into the next month
                end_date = next_month - timedelta(days=next_month.day)  # last day of the current month

                start_date_str = start_date.strftime('%d-%m-%Y')
                end_date_str = end_date.strftime('%d-%m-%Y')

                # Query for entries within the start and end date range
                query = {
                    "entry_date": {
                        "$gte": start_date_str,
                        "$lte": end_date_str
                    }
                }

                selected_month = month
                selected_year = year
            except ValueError:
                return "Invalid month or year.", 400










        # Year-wise search using the entire year range
        elif year:
            try:
                year = int(year)  # Ensure the year is a valid integer
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31, 23, 59, 59)

                start_date_str = start_date.strftime('%d-%m-%Y')
                end_date_str = end_date.strftime('%d-%m-%Y')

                # Query for entries within the year range
                query = {
                    "entry_date": {
                        "$gte": start_date_str,
                        "$lte": end_date_str
                    }
                }

                selected_year = year
            except ValueError:
                return "Invalid year format. Please use YYYY.", 400

        # Fetch entries from the database
        entries = list(collection.find(query))

        return render_template('view_entries.html', 
                               entries=entries, 
                               selected_date=selected_date, 
                               selected_month=selected_month, 
                               selected_year=selected_year)

    # If it's a GET request (initial load), show an empty page or default entries
    return render_template('view_entries.html', entries=[])

@app.route('/view_full_entry/<entry_id>', methods=['GET'])
def view_full_entry(entry_id):
    # Fetch the entry from the database using the entry_id
    entry = db.entries.find_one({"_id": ObjectId(entry_id)})

    # Check if the entry exists
    if entry:
        return render_template('full_view.html', entry=entry)
    else:
        flash('Entry not found.')
        return redirect('/view_entries')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)