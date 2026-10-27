# ELLA's Fitness Center

ELLA's Fitness Center is a web-based gym management application developed using Django. It helps manage gym operations, including member records, attendance, payments, and reminders through a centralized platform.

## Features

* Member Management: Add, view, and manage gym member information.
* Attendance Tracking: Maintain attendance records for gym members.
* Payment Management: Organize membership payment records.
* Dashboard: View relevant information about gym operations.
* Account Management: Handle user accounts and related functionality.
* Reminders: Manage reminders for gym-related activities.

## Technologies Used

* Backend: Python, Django
* Frontend: HTML, CSS, JavaScript
* Database: SQLite
* Version Control: Git and GitHub

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Minha112/ELLA-s-Fitness-Center.git
cd ELLA-s-Fitness-Center
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser to access the application.

## Project Structure

* `accounts/` - Account management
* `attendance/` - Attendance tracking
* `dashboard/` - Dashboard functionality
* `members/` - Member management
* `payments/` - Payment management
* `reminders/` - Reminder functionality
* `templates/` - HTML templates
* `static/` - Static files such as CSS and JavaScript
  

## Project Objective

The main objective of this project is to simplify gym administration by organizing member information, tracking attendance, and managing payment records in one application.

## Developer

Minha112

GitHub: https://github.com/Minha112

