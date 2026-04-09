from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "taskapp_secret_key"

# =========================
# AWS config
# =========================
REGION = "ap-south-1"

MANAGERS_TABLE = "Managers"
EMPLOYEES_TABLE = "Employees"
TASKS_TABLE = "Tasks"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:887525715970:task-update-topic"

USE_AWS = True
USE_SNS = True

dynamodb_resource = None
dynamodb_client = None
sns = None

if USE_AWS:
    dynamodb_resource = boto3.resource("dynamodb", region_name=REGION)
    dynamodb_client = boto3.client("dynamodb", region_name=REGION)
    sns = boto3.client("sns", region_name=REGION)

# =========================
# local fallback demo data
# =========================
managers = {
    "manager1": {
        "manager_id": "manager1",
        "name": "Main Manager",
        "email": "manager@example.com",
        "password": "manager123"
    }
}

employees = {
    "E101": {
        "employee_id": "E101",
        "name": "Ravi",
        "email": "ravi@example.com",
        "password": "emp123"
    },
    "E102": {
        "employee_id": "E102",
        "name": "Priya",
        "email": "priya@example.com",
        "password": "emp123"
    }
}

tasks = {
    "T101": {
        "task_id": "T101",
        "employee_id": "E101",
        "task_name": "Prepare weekly report",
        "status": "Pending",
        "priority": "High",
        "deadline": "2026-04-15",
        "remarks": "Submit before evening",
        "submitted_on": "",
        "completion_note": ""
    }
}


# =========================
# AWS helpers
# =========================
def create_table_if_not_exists(table_name, partition_key):
    existing_tables = dynamodb_client.list_tables()["TableNames"]

    if table_name not in existing_tables:
        dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": partition_key, "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": partition_key, "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        waiter = dynamodb_client.get_waiter("table_exists")
        waiter.wait(TableName=table_name)
        print(f"Created table: {table_name}")


def setup_tables():
    if not USE_AWS:
        return

    create_table_if_not_exists(MANAGERS_TABLE, "manager_id")
    create_table_if_not_exists(EMPLOYEES_TABLE, "employee_id")
    create_table_if_not_exists(TASKS_TABLE, "task_id")


def seed_demo_data():
    if not USE_AWS:
        return

    managers_table = dynamodb_resource.Table(MANAGERS_TABLE)
    employees_table = dynamodb_resource.Table(EMPLOYEES_TABLE)
    tasks_table = dynamodb_resource.Table(TASKS_TABLE)

    if "Item" not in managers_table.get_item(Key={"manager_id": "manager1"}):
        managers_table.put_item(
            Item={
                "manager_id": "manager1",
                "name": "Main Manager",
                "email": "manager@example.com",
                "password": "manager123"
            }
        )

    if "Item" not in employees_table.get_item(Key={"employee_id": "E101"}):
        employees_table.put_item(
            Item={
                "employee_id": "E101",
                "name": "Ravi",
                "email": "ravi@example.com",
                "password": "emp123"
            }
        )

    if "Item" not in employees_table.get_item(Key={"employee_id": "E102"}):
        employees_table.put_item(
            Item={
                "employee_id": "E102",
                "name": "Priya",
                "email": "priya@example.com",
                "password": "emp123"
            }
        )

    if "Item" not in tasks_table.get_item(Key={"task_id": "T101"}):
        tasks_table.put_item(
            Item={
                "task_id": "T101",
                "employee_id": "E101",
                "task_name": "Prepare weekly report",
                "status": "Pending",
                "priority": "High",
                "deadline": "2026-04-15",
                "remarks": "Submit before evening",
                "submitted_on": "",
                "completion_note": ""
            }
        )


# =========================
# common helpers
# =========================
def send_notification(subject, message):
    if USE_AWS and USE_SNS and SNS_TOPIC_ARN != "YOUR_SNS_TOPIC_ARN":
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    else:
        print(f"[SNS MOCK] {subject} - {message}")


def get_all_managers():
    if USE_AWS:
        table = dynamodb_resource.Table(MANAGERS_TABLE)
        response = table.scan()
        items = response.get("Items", [])
        return {item["manager_id"]: item for item in items}
    return managers


def get_all_employees():
    if USE_AWS:
        table = dynamodb_resource.Table(EMPLOYEES_TABLE)
        response = table.scan()
        items = response.get("Items", [])
        return {item["employee_id"]: item for item in items}
    return employees


def get_all_tasks():
    if USE_AWS:
        table = dynamodb_resource.Table(TASKS_TABLE)
        response = table.scan()
        items = response.get("Items", [])
        return {item["task_id"]: item for item in items}
    return tasks


def get_manager(manager_id):
    if USE_AWS:
        table = dynamodb_resource.Table(MANAGERS_TABLE)
        response = table.get_item(Key={"manager_id": manager_id})
        return response.get("Item")
    return managers.get(manager_id)


def get_employee(employee_id):
    if USE_AWS:
        table = dynamodb_resource.Table(EMPLOYEES_TABLE)
        response = table.get_item(Key={"employee_id": employee_id})
        return response.get("Item")
    return employees.get(employee_id)


def get_task(task_id):
    if USE_AWS:
        table = dynamodb_resource.Table(TASKS_TABLE)
        response = table.get_item(Key={"task_id": task_id})
        return response.get("Item")
    return tasks.get(task_id)


def get_employee_tasks(employee_id):
    all_tasks = get_all_tasks()
    return [task for task in all_tasks.values() if task["employee_id"] == employee_id]


def task_deadline_message(deadline_str):
    today = datetime.today().date()
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

    if today < deadline:
        return f"before deadline ({deadline_str})"
    elif today == deadline:
        return f"on deadline ({deadline_str})"
    else:
        return f"after deadline ({deadline_str})"


# =========================
# routes
# =========================
@app.route("/")
def home():
     return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        if role == "manager":
            manager = get_manager(username)
            if manager and manager["password"] == password:
                session["role"] = "manager"
                session["username"] = username
                return redirect(url_for("manager_dashboard"))
            else:
                error = "Invalid manager credentials"

        elif role == "employee":
            employee = get_employee(username)
            if employee and employee["password"] == password:
                session["role"] = "employee"
                session["username"] = username
                return redirect(url_for("employee_dashboard"))
            else:
                error = "Invalid employee credentials"

    return render_template("login.html", error=error)


@app.route("/signup/employee", methods=["GET", "POST"])
def employee_signup():
    message = ""
    error = ""

    if request.method == "POST":
        employee_id = request.form["employee_id"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_employee = get_employee(employee_id)

        if existing_employee:
            error = "Employee ID already exists"
        else:
            item = {
                "employee_id": employee_id,
                "name": name,
                "email": email,
                "password": password
            }

            if USE_AWS:
                table = dynamodb_resource.Table(EMPLOYEES_TABLE)
                table.put_item(Item=item)
            else:
                employees[employee_id] = item

            message = "Employee signup successful. Please login."

    return render_template(
        "signup.html",
        role_title="Employee",
        form_action="/signup/employee",
        id_label="Employee ID",
        id_name="employee_id",
        message=message,
        error=error
    )


@app.route("/signup/manager", methods=["GET", "POST"])
def manager_signup():
    message = ""
    error = ""

    if request.method == "POST":
        manager_id = request.form["manager_id"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_manager = get_manager(manager_id)

        if existing_manager:
            error = "Manager ID already exists"
        else:
            item = {
                "manager_id": manager_id,
                "name": name,
                "email": email,
                "password": password
            }

            if USE_AWS:
                table = dynamodb_resource.Table(MANAGERS_TABLE)
                table.put_item(Item=item)
            else:
                managers[manager_id] = item

            message = "Manager signup successful. Please login."

    return render_template(
        "signup.html",
        role_title="Manager",
        form_action="/signup/manager",
        id_label="Manager ID",
        id_name="manager_id",
        message=message,
        error=error
    )

@app.route("/manager_dashboard")
def manager_dashboard():
    if session.get("role") != "manager":
        return redirect(url_for("login"))

    current_manager = get_manager(session["username"])
    all_employees = get_all_employees()
    all_tasks = get_all_tasks()

    return render_template(
        "manager_dashboard.html",
        employees=all_employees.values(),
        tasks=all_tasks.values(),
        manager_name=current_manager["name"]
    )


@app.route("/employee_dashboard")
def employee_dashboard():
    if session.get("role") != "employee":
        return redirect(url_for("login"))

    employee = get_employee(session["username"])
    employee_tasks = get_employee_tasks(session["username"])

    return render_template(
        "employee_dashboard.html",
        employee=employee,
        tasks=employee_tasks
    )


@app.route("/add_task", methods=["POST"])
def add_task():
    if session.get("role") != "manager":
        return redirect(url_for("login"))

    task_id = request.form["task_id"]
    employee_id = request.form["employee_id"]
    task_name = request.form["task_name"]
    status = request.form["status"]
    priority = request.form["priority"]
    deadline = request.form["deadline"]
    remarks = request.form["remarks"]

    item = {
        "task_id": task_id,
        "employee_id": employee_id,
        "task_name": task_name,
        "status": status,
        "priority": priority,
        "deadline": deadline,
        "remarks": remarks,
        "submitted_on": "",
        "completion_note": ""
    }

    if USE_AWS:
        table = dynamodb_resource.Table(TASKS_TABLE)
        table.put_item(Item=item)
    else:
        tasks[task_id] = item

    send_notification(
        "New Task Assigned",
        f"Task '{task_name}' assigned to employee {employee_id}. Deadline: {deadline}. Status: {status}"
    )

    return redirect(url_for("manager_dashboard"))

@app.route("/update_task", methods=["POST"])
def update_task():
    if session.get("role") != "employee":
        return redirect(url_for("login"))

    task_id = request.form["task_id"]
    status = request.form["status"]
    remarks = request.form["remarks"]

    task = get_task(task_id)

    if task and task["employee_id"] == session["username"]:
        task_name = task["task_name"]

        if USE_AWS:
            table = dynamodb_resource.Table(TASKS_TABLE)
            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression="SET #st = :s, remarks = :r",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={
                    ":s": status,
                    ":r": remarks
                }
            )
        else:
            tasks[task_id]["status"] = status
            tasks[task_id]["remarks"] = remarks

        send_notification(
            "Task Status Updated",
            f"""
                Task Update Notification

                Employee: {session['username']}
                Task ID: {task_id}
                Task Name: {task_name}
                New Status: {status}

                Remarks:
                {remarks}
                """
        )

    return redirect(url_for("employee_dashboard"))

@app.route("/submit_task", methods=["POST"])
def submit_task():
    if session.get("role") != "employee":
        return redirect(url_for("login"))

    task_id = request.form["task_id"]
    completion_note = request.form["completion_note"]
    submitted_on = datetime.today().strftime("%Y-%m-%d")

    task = get_task(task_id)

    if task and task["employee_id"] == session["username"]:
        deadline_info = task_deadline_message(task["deadline"])

        if USE_AWS:
            table = dynamodb_resource.Table(TASKS_TABLE)
            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression="SET #st = :s, completion_note = :c, submitted_on = :d",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={
                    ":s": "Completed",
                    ":c": completion_note,
                    ":d": submitted_on
                }
            )
        else:
            tasks[task_id]["status"] = "Completed"
            tasks[task_id]["completion_note"] = completion_note
            tasks[task_id]["submitted_on"] = submitted_on

        send_notification(
            "Task Submitted by Employee",
            f"Employee {session['username']} submitted task '{task_id}' as completed {deadline_info}. Submitted on: {submitted_on}. Note: {completion_note}"
        )

    return redirect(url_for("employee_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# startup
# =========================
if __name__ == "__main__":
    if USE_AWS:
        setup_tables()
        seed_demo_data()

    app.run(debug=True)