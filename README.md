# Employee Task Reminder

A Flask-based web application for managing employee tasks with role-based dashboards for managers and employees. Features AWS DynamoDB integration for data persistence and SNS for task notifications.

## Features

- **Role-Based Access Control**
  - Manager dashboard for creating and tracking tasks
  - Employee dashboard for viewing and completing assigned tasks
  - Separate login/signup for managers and employees

- **Task Management**
  - Create tasks with priority levels (High, Medium, Low)
  - Set deadlines and add remarks
  - Track task status (Pending, In Progress, Completed)
  - Employee task completion with notes

- **AWS Integration**
  - DynamoDB for persistent data storage
  - SNS for task update notifications
  - Automatic table creation and demo data seeding

- **User Authentication**
  - Secure login and signup flows
  - Session-based authentication
  - Separate manager and employee accounts

## Project Structure

```
employee_task_reminder/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   └── style.css         # CSS styling
└── templates/
    ├── landing.html      # Home page
    ├── login.html        # Login page
    ├── signup.html       # Sign up page
    ├── manager_dashboard.html  # Manager interface
    └── employee_dashboard.html # Employee interface
```

## Prerequisites

- Python 3.7+
- AWS Account (for DynamoDB and SNS services)
- AWS credentials configured locally or via environment variables

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee_task_reminder
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure AWS credentials**
   - Set environment variables or configure AWS CLI:
     ```bash
     aws configure
     ```
   - Ensure your AWS user has permissions for DynamoDB and SNS

## Configuration

Edit the configuration section in `app.py`:

```python
REGION = "ap-south-1"  # AWS region
MANAGERS_TABLE = "Managers"
EMPLOYEES_TABLE = "Employees"
TASKS_TABLE = "Tasks"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:887525715970:task-update-topic"
USE_AWS = True  # Set to False for local demo mode
USE_SNS = True  # Set to False to disable notifications
```

## Running the Application

1. **Start Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open browser and navigate to `http://localhost:5000`

## Demo Credentials

The application includes demo data for testing:

**Manager:**
- ID: `manager1`
- Email: `manager@example.com`
- Password: `manager123`

**Employees:**
- Employee 1: `ravi@example.com` / `emp123`
- Employee 2: `priya@example.com` / `emp123`

## Usage

### For Managers
1. Login with manager credentials
2. View dashboard with all assigned employees
3. Create new tasks for employees
4. Set task priority, deadline, and remarks
5. Track task completion status
6. Receive notifications on task updates

### For Employees
1. Signup or login with credentials
2. View assigned tasks on dashboard
3. Check task details, priority, and deadline
4. Mark tasks as complete with completion notes
5. Receive notifications about new tasks

## Local Demo Mode

To run without AWS services:

1. Edit `app.py` and set:
   ```python
   USE_AWS = False
   USE_SNS = False
   ```

2. The application will use in-memory data stores with demo data.

## Database Schema

### Managers Table
- `manager_id` (String, Primary Key)
- `name` (String)
- `email` (String)
- `password` (String)

### Employees Table
- `employee_id` (String, Primary Key)
- `name` (String)
- `email` (String)
- `password` (String)

### Tasks Table
- `task_id` (String, Primary Key)
- `employee_id` (String)
- `task_name` (String)
- `status` (String)
- `priority` (String)
- `deadline` (String)
- `remarks` (String)
- `submitted_on` (String)
- `completion_note` (String)

## Notifications

SNS notifications are sent for:
- New task assignments
- Task status updates
- Task completions

Configure the `SNS_TOPIC_ARN` to receive notifications in your AWS account.

## Troubleshooting

**Cannot connect to DynamoDB:**
- Check AWS credentials are properly configured
- Verify IAM permissions for DynamoDB and SNS
- Ensure the specified AWS region is correct

**Tables not creating:**
- Check AWS credentials and permissions
- Verify `USE_AWS` is set to `True`
- Check CloudWatch logs for detailed errors

**Session issues:**
- Clear browser cookies
- Verify `app.secret_key` is set correctly
- Restart Flask application

## Dependencies

- **Flask**: Web framework for Python
- **boto3**: AWS SDK for Python

See `requirements.txt` for specific versions.

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
