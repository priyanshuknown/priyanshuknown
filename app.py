from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
DATABASE = 'parking_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create parking_lots table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            total_spots INTEGER NOT NULL,
            price_per_hour REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create parking_spots table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            spot_number INTEGER NOT NULL,
            is_occupied BOOLEAN DEFAULT 0,
            vehicle_number TEXT,
            user_id INTEGER,
            booked_at TIMESTAMP,
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create admin user if not exists
    admin_exists = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        conn.execute('INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                    ('admin', 'admin@parking.com', admin_password, 1))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                                   (username, email)).fetchone()
        
        if existing_user:
            flash('Username or email already exists')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (username, email, password_hash))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all parking lots with spot statistics
    lots = conn.execute('''
        SELECT pl.*, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.is_occupied = 1 THEN 1 ELSE 0 END) as occupied_spots
        FROM parking_lots pl
        LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
        GROUP BY pl.id
        ORDER BY pl.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', lots=lots)

@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_lot():
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        total_spots = int(request.form['total_spots'])
        price_per_hour = float(request.form['price_per_hour'])
        
        conn = get_db_connection()
        
        # Create parking lot
        cursor = conn.execute('INSERT INTO parking_lots (name, location, total_spots, price_per_hour) VALUES (?, ?, ?, ?)',
                             (name, location, total_spots, price_per_hour))
        lot_id = cursor.lastrowid
        
        # Create parking spots
        for i in range(1, total_spots + 1):
            conn.execute('INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)',
                        (lot_id, i))
        
        conn.commit()
        conn.close()
        
        flash(f'Parking lot "{name}" created successfully with {total_spots} spots!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        total_spots = int(request.form['total_spots'])
        price_per_hour = float(request.form['price_per_hour'])
        
        # Get current total spots
        current_lot = conn.execute('SELECT total_spots FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        current_spots = current_lot['total_spots']
        
        # Update parking lot
        conn.execute('UPDATE parking_lots SET name = ?, location = ?, total_spots = ?, price_per_hour = ? WHERE id = ?',
                    (name, location, total_spots, price_per_hour, lot_id))
        
        # Adjust parking spots if needed
        if total_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, total_spots + 1):
                conn.execute('INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)',
                            (lot_id, i))
        elif total_spots < current_spots:
            # Remove excess spots (only unoccupied ones)
            conn.execute('DELETE FROM parking_spots WHERE lot_id = ? AND spot_number > ? AND is_occupied = 0',
                        (lot_id, total_spots))
        
        conn.commit()
        conn.close()
        
        flash(f'Parking lot updated successfully!')
        return redirect(url_for('admin_dashboard'))
    
    # Get lot details
    lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
    conn.close()
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if any spots are occupied
    occupied_spots = conn.execute('SELECT COUNT(*) as count FROM parking_spots WHERE lot_id = ? AND is_occupied = 1',
                                 (lot_id,)).fetchone()
    
    if occupied_spots['count'] > 0:
        flash('Cannot delete parking lot. Some spots are currently occupied.')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    # Delete parking spots and lot
    conn.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
    conn.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
    conn.commit()
    conn.close()
    
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view_spots/<int:lot_id>')
def view_spots(lot_id):
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
    spots = conn.execute('''
        SELECT ps.*, u.username
        FROM parking_spots ps
        LEFT JOIN users u ON ps.user_id = u.id
        WHERE ps.lot_id = ?
        ORDER BY ps.spot_number
    ''', (lot_id,)).fetchall()
    
    conn.close()
    
    return render_template('view_spots.html', lot=lot, spots=spots)

@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id') or session.get('is_admin'):
        flash('Please login as a user to access this page.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get user's current bookings
    current_bookings = conn.execute('''
        SELECT ps.*, pl.name as lot_name, pl.location, pl.price_per_hour
        FROM parking_spots ps
        JOIN parking_lots pl ON ps.lot_id = pl.id
        WHERE ps.user_id = ? AND ps.is_occupied = 1
    ''', (session['user_id'],)).fetchall()
    
    # Get available parking lots
    available_lots = conn.execute('''
        SELECT pl.*, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.is_occupied = 0 THEN 1 ELSE 0 END) as available_spots
        FROM parking_lots pl
        LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
        GROUP BY pl.id
        HAVING available_spots > 0
        ORDER BY pl.name
    ''').fetchall()
    
    conn.close()
    
    return render_template('user_dashboard.html', current_bookings=current_bookings, available_lots=available_lots)

@app.route('/user/book_spot/<int:lot_id>', methods=['POST'])
def book_spot(lot_id):
    if not session.get('user_id') or session.get('is_admin'):
        flash('Please login as a user to book a spot.')
        return redirect(url_for('login'))
    
    vehicle_number = request.form['vehicle_number']
    
    if not vehicle_number:
        flash('Please enter your vehicle number.')
        return redirect(url_for('user_dashboard'))
    
    conn = get_db_connection()
    
    # Find an available spot
    available_spot = conn.execute('''
        SELECT * FROM parking_spots 
        WHERE lot_id = ? AND is_occupied = 0 
        ORDER BY spot_number 
        LIMIT 1
    ''', (lot_id,)).fetchone()
    
    if not available_spot:
        flash('No available spots in this parking lot.')
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    # Book the spot
    conn.execute('''
        UPDATE parking_spots 
        SET is_occupied = 1, vehicle_number = ?, user_id = ?, booked_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (vehicle_number, session['user_id'], available_spot['id']))
    
    conn.commit()
    conn.close()
    
    flash(f'Successfully booked spot #{available_spot["spot_number"]}!')
    return redirect(url_for('user_dashboard'))

@app.route('/user/release_spot/<int:spot_id>')
def release_spot(spot_id):
    if not session.get('user_id') or session.get('is_admin'):
        flash('Please login as a user to release a spot.')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Verify that the spot belongs to the current user
    spot = conn.execute('SELECT * FROM parking_spots WHERE id = ? AND user_id = ?',
                       (spot_id, session['user_id'])).fetchone()
    
    if not spot:
        flash('Invalid spot or you do not have permission to release this spot.')
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    # Release the spot
    conn.execute('''
        UPDATE parking_spots 
        SET is_occupied = 0, vehicle_number = NULL, user_id = NULL, booked_at = NULL
        WHERE id = ?
    ''', (spot_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Successfully released spot #{spot["spot_number"]}!')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)