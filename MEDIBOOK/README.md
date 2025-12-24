# MEDIBOOK

MEDIBOOK is a comprehensive medical appointment booking system designed to bridge the gap between patients and doctors. It allows patients to search for doctors, book appointments, and manage their health profile, while providing doctors with tools to manage their availability and appointments.

## Features

### Core Features
- **User Authentication**: Secure login and registration for Patients, Doctors, and Admins.
- **Role-Based Dashboards**: Tailored interfaces for different user roles.
- **Doctor Search**: Advanced search by specialization, city, and name.
- **Appointment Booking**: Easy booking system with availability checking.
- **Doctor Availability**: Doctors can manage their available time slots.
- **Reviews & Ratings**: Patients can review doctors after appointments.
- **Admin Panel**: For verifying doctor accounts and managing the system.
- **Profile Management**: Users can update their profiles and upload pictures.

### Bonus Features
- **AI Medical Assistant**: An integrated functionality to chat with an AI for preliminary medical advice.
- **Design Patterns**: 
  - **MVC Architecture**: Strict separation of concerns.
  - **Repository Pattern**: Abstraction layer for data access.
  - **Singleton Pattern**: Efficient database connection management.
  - **App Factory Pattern**: Modular application creation.

## Technology Stack
- **Backend**: Python, Flask
- **Database**: SQLite, SQLAlchemy (ORM)
- **Frontend**: HTML5, CSS3
- **Containerization**: Docker

##  Project Structure
```
MEDIBOOK/
├── MediBook/               # Source code
│   ├── controllers/        # Route handlers (Blueprints)
│   ├── models/             # Database models
│   ├── templates/          # HTML templates
│   ├── static/             # Static assets (CSS, images)
│   ├── app.py              # Application entry point & Factory
│   ├── config.py           # Configuration settings
│   ├── repositories.py     # Data access layer
│   └── database_singleton.py # Database instance management
├── tests/                  # Unit tests
├── docs/                   # Documentation (SRS, Design, Manuals)
├── deployment/             # Deployment configurations
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

##  Installation & Setup

### Prerequisites
- Python 3.9+
- pip

### Local Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MEDIBOOK/MEDIBOOK
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m MediBook.app
   # OR direct execution if in MediBook folder
   python app.py
   ```
   The application will be available at `http://localhost:5000`.

### Docker Setup
1. **Build the image**
   ```bash
   docker build -t medibook .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 medibook
   ```

##  Testing
Run the automated test suite:
```bash
pytest
```

## Contributors
Ahmed Ragheb 202301566
Ammar Yasser 202400663 
Ahmed Ibrahem 202402177 
Yossef Ahmed 202300216



---
*Course Project for CSAI 203: Introduction to Software Engineering*
