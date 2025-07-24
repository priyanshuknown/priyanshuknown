# Vehicle Parking App - V1

A comprehensive multi-user parking management system built with Flask, featuring real-time parking spot tracking, user authentication, and administrative controls for 4-wheeler parking lots.

## 🚗 Features

### Administrator Features
- **Superuser Access**: Pre-configured admin account with full system control
- **Parking Lot Management**: Create, edit, and delete parking lots with custom pricing
- **Real-time Monitoring**: View status of all parking spots across all lots
- **Dynamic Spot Management**: Add or remove parking spots from existing lots
- **Comprehensive Dashboard**: Visual overview with occupancy statistics and system metrics

### User Features
- **User Registration & Authentication**: Secure account creation and login system
- **Parking Spot Booking**: Browse available lots and book spots automatically
- **Vehicle Management**: Associate vehicle numbers with bookings
- **Booking History**: View current active bookings with details
- **Spot Release**: Easy release of parked vehicles

### System Features
- **SQLite Database**: Programmatically created database with proper relationships
- **Responsive Design**: Modern Bootstrap UI that works on all devices
- **Real-time Updates**: Live availability tracking and status updates
- **Data Validation**: Comprehensive form validation and error handling
- **Security**: Password hashing and session management

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: Jinja2 templating, HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (with programmatic creation)
- **Icons**: Bootstrap Icons
- **Authentication**: Werkzeug password hashing
- **Session Management**: Flask sessions

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vehicle-parking-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - The database will be automatically created on first run

### Demo Credentials

**Administrator Access:**
- Username: `admin`
- Password: `admin123`

**User Access:**
- Register a new account through the registration page
- Or create test users as needed

## 📖 Usage Guide

### For Administrators

1. **Login** with admin credentials
2. **Create Parking Lots**:
   - Click "Create New Lot" from the admin dashboard
   - Enter lot name, location, number of spots, and hourly rate
   - Spots are automatically numbered from 1 to total count
3. **Manage Existing Lots**:
   - View all lots with real-time occupancy statistics
   - Edit lot details or adjust number of spots
   - Delete lots (only if no spots are occupied)
4. **Monitor Spots**:
   - Click "View Spots" to see visual grid layout
   - Click on occupied spots for user and vehicle details
   - View detailed occupancy reports

### For Users

1. **Register** a new account or **login** with existing credentials
2. **Browse Available Lots**:
   - View all lots with available spots
   - See pricing and location information
3. **Book a Spot**:
   - Enter your vehicle number
   - Click "Book Now" - spot is automatically assigned
   - Receive confirmation with spot number
4. **Manage Bookings**:
   - View all current bookings on your dashboard
   - See booking details including time and location
   - Release spots when done parking

## 📁 Project Structure

```
vehicle-parking-app/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── parking_app.db            # SQLite database (auto-created)
└── templates/                # Jinja2 templates
    ├── base.html             # Base template with navigation
    ├── index.html            # Homepage
    ├── login.html            # Login page
    ├── register.html         # User registration
    ├── admin_dashboard.html  # Admin control panel
    ├── create_lot.html       # Create parking lot form
    ├── edit_lot.html         # Edit parking lot form
    ├── view_spots.html       # Visual spot layout
    └── user_dashboard.html   # User booking interface
```

## 🗄️ Database Schema

### Tables

1. **users**
   - `id`: Primary key
   - `username`: Unique username
   - `email`: Unique email address
   - `password_hash`: Hashed password
   - `is_admin`: Boolean flag for admin privileges
   - `created_at`: Account creation timestamp

2. **parking_lots**
   - `id`: Primary key
   - `name`: Parking lot name
   - `location`: Physical location
   - `total_spots`: Number of parking spots
   - `price_per_hour`: Hourly parking rate
   - `created_at`: Creation timestamp

3. **parking_spots**
   - `id`: Primary key
   - `lot_id`: Foreign key to parking_lots
   - `spot_number`: Spot number within the lot
   - `is_occupied`: Boolean occupancy status
   - `vehicle_number`: Parked vehicle identifier
   - `user_id`: Foreign key to users (when occupied)
   - `booked_at`: Booking timestamp

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface using Bootstrap 5
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Interactive Elements**: Hover effects, modals, and smooth transitions
- **Visual Feedback**: Color-coded status indicators and progress bars
- **Real-time Updates**: Live occupancy tracking and availability display
- **Intuitive Navigation**: Clear menu structure and breadcrumbs

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Secure user session handling
- **Role-based Access**: Separate admin and user privileges
- **Input Validation**: Server-side and client-side form validation
- **SQL Injection Prevention**: Parameterized queries
- **CSRF Protection**: Built-in Flask security measures

## 🌟 Key Highlights

- **Zero Manual Database Setup**: Database and tables created automatically
- **Automatic Spot Assignment**: Users don't choose spots - system assigns optimally
- **Real-time Availability**: Live updates without page refresh requirements
- **Scalable Architecture**: Easy to extend with additional features
- **Production Ready**: Comprehensive error handling and validation
- **Mobile Friendly**: Fully responsive design works on all screen sizes

## 📝 Development Notes

- The application uses Flask's development server (not suitable for production)
- Database file (`parking_app.db`) is created in the project root directory
- Session secret key should be changed for production deployment
- All parking spots are designed for 4-wheeler vehicles only
- Admin account is automatically created on first run

## 🚀 Future Enhancements

Potential features for V2:
- Payment integration
- Reservation system with time slots
- Mobile app companion
- SMS/Email notifications
- Advanced reporting and analytics
- Multi-location support
- API endpoints for third-party integration

## 📞 Support

For issues or questions regarding the Vehicle Parking App, please refer to the code comments or create an issue in the repository.

---

**© 2024 Vehicle Parking App. Built with Flask and Bootstrap.**
