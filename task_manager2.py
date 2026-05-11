# ===== Task Manager (fixed) ===========
# Fixes made:
# - Use the logged-in username (curr_user) consistently (was calling view_mine(username) where 'username' was undefined).
# - Enforce that only the admin can register new users (as per the spec).
# - Improve robustness when reading user.txt and tasks.txt (skip blank/malformed lines).
# - Make assigned_date consistent (store as datetime) and validate inputs when editing.
# - Improve view_all output formatting and remove stray debug prints.
# - Validate username when editing a task (ensure it exists).
# - Centralize saving of tasks to tasks.txt in save_tasks().
# - display_statistics now reads the generated files task_overview.txt and user_overview.txt,
#   generating them first if they don't exist (assignment requirement).
# - Various small UX / safety improvements and clearer messages.
import os
from datetime import datetime

DATETIME_STRING_FORMAT = "%Y-%m-%d"

# helper: save tasks to disk


def save_tasks(task_list, filename="tasks.txt"):
    with open(filename, "w") as task_file:
        lines = []
        for t in task_list:
            str_attrs = [
                t['username'],
                t['title'],
                t['description'],
                t['due_date'].strftime(DATETIME_STRING_FORMAT),
                t['assigned_date'].strftime(DATETIME_STRING_FORMAT),
                "Yes" if t['completed'] else "No"
            ]
            lines.append(";".join(str_attrs))
        task_file.write("\n".join(lines))


# Create tasks.txt if it doesn't exist
if not os.path.exists("tasks.txt"):
    with open("tasks.txt", "w") as default_file:
        pass

# Read tasks safely (skip blank/malformed lines)
task_list = []
with open("tasks.txt", 'r') as task_file:
    for line in task_file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";")
        if len(parts) != 6:
            # Skip malformed lines but print a warning for developer
            print(f"Warning: skipping malformed task line: {line}")
            continue
        try:
            task = {
                'username': parts[0],
                'title': parts[1],
                'description': parts[2],
                'due_date': datetime.strptime(parts[3], DATETIME_STRING_FORMAT),
                'assigned_date': datetime.strptime(parts[4], DATETIME_STRING_FORMAT),
                'completed': True if parts[5].strip().lower() == "yes" else False
            }
            task_list.append(task)
        except Exception as e:
            print(f"Warning: could not parse dates for line: {line} ({e})")
            continue


# ====Login Section====

# If no user.txt file, write one with a default account
if not os.path.exists("user.txt"):
    with open("user.txt", "w") as default_file:
        default_file.write("admin;password\n")

# Read in user_data (skip blank lines)
username_password = {}
with open("user.txt", 'r') as user_file:
    for line in user_file:
        line = line.strip()
        if not line:
            continue
        if ";" not in line:
            print(f"Warning: skipping malformed user line: {line}")
            continue
        try:
            username, password = line.split(";", 1)
            username_password[username] = password
        except ValueError:
            print(f"Warning: skipping malformed user line: {line}")
            continue

logged_in = False
curr_user = None
while not logged_in:
    print("LOGIN")
    entered_user = input("Username: ").strip()
    entered_pass = input("Password: ").strip()
    if entered_user not in username_password:
        print("User does not exist")
        continue
    elif username_password[entered_user] != entered_pass:
        print("Wrong password")
        continue
    else:
        print("Login Successful!")
        logged_in = True
        curr_user = entered_user


# Function to register a new user (admin only)
def reg_user():
    '''Add a new user to the user.txt file'''
    new_username = input("New Username: ").strip()
    if not new_username:
        print("Username cannot be empty.")
        return

    if new_username in username_password:
        print("\nUser already exists")
        return

    new_password = input("New Password: ").strip()
    confirm_password = input("Confirm Password: ").strip()

    if new_password == confirm_password:
        username_password[new_username] = new_password
        # write user file
        with open("user.txt", "w") as out_file:
            for uname, pwd in username_password.items():
                out_file.write(f"{uname};{pwd}\n")
        print("New user added.")
    else:
        print("Passwords do not match.")

# Add a new task


def add_task():
    '''Allow a user to add a new task to tasks.txt file'''
    task_username = input("Name of person assigned to task: ").strip()
    if task_username not in username_password:
        print("User does not exist. Please enter a valid username")
        return
    task_title = input("Title of Task: ").strip()
    task_description = input("Description of Task: ").strip()
    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ").strip()
            due_date_time = datetime.strptime(
                task_due_date, DATETIME_STRING_FORMAT)
            break
        except ValueError:
            print("Invalid datetime format. Please use the format specified (YYYY-MM-DD)")

    curr_date = datetime.today()
    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }

    task_list.append(new_task)
    save_tasks(task_list)
    generate_report(task_list, username_password)
    print("Task successfully added.")

# View all tasks


def view_all():
    '''Print all tasks in a readable format'''
    if not task_list:
        print("No tasks to show.")
        return

    for idx, t in enumerate(task_list, start=1):
        disp_str = f"Task [{idx}]:\t {t['title']}\n"
        disp_str += f"Assigned to:\t {t['username']}\n"
        disp_str += f"Date Assigned:\t {t['assigned_date'].strftime(DATETIME_STRING_FORMAT)}\n"
        disp_str += f"Due Date:\t {t['due_date'].strftime(DATETIME_STRING_FORMAT)}\n"
        disp_str += f"Task Description:\n {t['description']}\n"
        disp_str += f"Completed:\t {'Yes' if t['completed'] else 'No'}\n"
        print(disp_str)

# View and edit tasks assigned to the logged-in user


def view_mine(username):
    '''Displays and allows editing/completing tasks assigned to the logged-in user.'''
    visible_indexes = []

    for idx, t in enumerate(task_list):
        if t['username'] == username:
            visible_indexes.append(idx)
            num = len(visible_indexes)
            disp_str = f"[{num}] Task:\t\t {t['title']}\n"
            disp_str += f"Assigned to:\t {t['username']}\n"
            disp_str += f"Date Assigned:\t {t['assigned_date'].strftime(DATETIME_STRING_FORMAT)}\n"
            disp_str += f"Due Date:\t {t['due_date'].strftime(DATETIME_STRING_FORMAT)}\n"
            disp_str += f"Task Description:\n {t['description']}\n"
            disp_str += f"Completed:\t {'Yes' if t['completed'] else 'No'}\n"
            print(disp_str)

    if not visible_indexes:
        print("No tasks assigned to you.")
        return

    try:
        selected = int(
            input("Enter the number of the task you want to select (or -1 to cancel): "))
    except ValueError:
        print("Invalid input.")
        return
    if selected == -1:
        return
    if selected < 1 or selected > len(visible_indexes):
        print("Invalid selection.")
        return
    task_index = visible_indexes[selected - 1]
    selected_task = task_list[task_index]
    # Prompt for action
    task_function = input(
        "Enter 'm' to mark as complete, 'e' to edit the task, or 'd' to delete the task: "
    ).lower().strip()

    if task_function == 'd':
        confirm = input(
            "Are you sure you want to DELETE this task? "
            "Type 'yes' to confirm: ").strip().lower()
        if confirm == 'yes':
            # remove the task and persist changes
            del task_list[task_index]
            save_tasks(task_list)
            generate_report(task_list, username_password)
            print("Task deleted.")
        else:
            print("Deletion cancelled.")
        return
    # Handle marking complete or editing
    if task_function == 'm':
        if selected_task["completed"]:
            print("Task has already been completed.")
        else:
            selected_task["completed"] = True
            save_tasks(task_list)
            generate_report(task_list, username_password)
            print("Task marked as complete.")
    elif task_function == 'e':
        if selected_task["completed"]:
            print("Cannot edit a completed task.")
            return
        print("\nEdit options:\n1 - Change Username\n2 - Change Due Date")
        choice = input("Select an option: ").strip()
        if choice == "1":
            new_un = input("Enter new username: ").strip()
            if new_un not in username_password:
                print("That username does not exist. Edit cancelled.")
                return
            selected_task["username"] = new_un
            save_tasks(task_list)
            generate_report(task_list, username_password)
            print("Username updated successfully.")
        elif choice == "2":
            new_date = input("Enter new due date (YYYY-MM-DD): ").strip()
            try:
                selected_task["due_date"] = datetime.strptime(
                    new_date, DATETIME_STRING_FORMAT)
            except ValueError:
                print("Invalid date format. Edit cancelled.")
                return
            save_tasks(task_list)
            generate_report(task_list, username_password)
            print("Due date updated successfully.")
        else:
            print("Invalid choice.")
            return
    else:
        print("Invalid option.")

# View completed tasks this is added to menu


def view_completed(username=None):
    '''Show completed tasks. If username passed, show only that user's completed tasks.'''
    matches = []
    for idx, t in enumerate(task_list):
        if t['completed'] and (username is None or t['username'] == username):
            matches.append((idx, t))

    if not matches:
        print("No completed tasks found.")
        return

    for num, (idx, t) in enumerate(matches, start=1):
        disp_str = f"[{num}] Task:\t {t['title']}\n"
        disp_str += f"Assigned to:\t {t['username']}\n"
        disp_str += f"Date Assigned:\t {t['assigned_date'].strftime(DATETIME_STRING_FORMAT)}\n"
        disp_str += f"Due Date:\t {t['due_date'].strftime(DATETIME_STRING_FORMAT)}\n"
        disp_str += f"Task Description:\n {t['description']}\n"
        disp_str += f"Completed:\t {'Yes' if t['completed'] else 'No'}\n"
        print(disp_str)

# Generate reports for tasks and users


def generate_report(task_list, username_password):
    """Create task_overview.txt and user_overview.txt based on current data."""
    total_task = len(task_list)
    completed_task = sum(1 for task in task_list if task['completed'])
    incomplete_task = total_task - completed_task

    today = datetime.today()

    overdue_uncompleted = sum(1 for task in task_list if (
        not task["completed"]) and (task["due_date"] < today))

    pct_incomplete = (incomplete_task / total_task * 100) if total_task else 0
    pct_overdue = (overdue_uncompleted / total_task * 100) if total_task else 0

    with open("task_overview.txt", "w") as file:
        file.write(f"Total task: {total_task}\n")
        file.write(f"Completed task: {completed_task}\n")
        file.write(f"Incomplete task: {incomplete_task}\n")
        file.write(f"Overdue & uncompleted: {overdue_uncompleted}\n")
        file.write(f"% Incomplete: {pct_incomplete:.2f}%\n")
        file.write(f"% Overdue: {pct_overdue:.2f}%\n")

    with open("user_overview.txt", "w") as uf:
        uf.write("USER OVERVIEW\n")
        uf.write("----------------------------------------\n")
        uf.write(f"Total users: {len(username_password)}\n")
        uf.write(f"Total tasks: {len(task_list)}\n\n")

        from collections import defaultdict
        user_tasks = defaultdict(list)
        for t in task_list:
            user_tasks[t['username']].append(t)

        total_tasks = len(task_list)

        for user in username_password:
            tasks = user_tasks.get(user, [])
            total_user_tasks = len(tasks)
            completed = sum(1 for t in tasks if t['completed'])
            uncompleted = total_user_tasks - completed
            overdue = sum(1 for t in tasks if (
                not t['completed']) and t['due_date'] < today)

            pct_assigned = (total_user_tasks / total_tasks *
                            100) if total_tasks else 0
            pct_completed = (completed / total_user_tasks *
                             100) if total_user_tasks else 0
            pct_uncompleted = (uncompleted / total_user_tasks *
                               100) if total_user_tasks else 0

            uf.write("----------------------------------------\n")
            uf.write(f"User: {user}\n")
            uf.write(f"Tasks assigned: {total_user_tasks}\n")
            uf.write(f"Percentage of all tasks: {pct_assigned:.2f}%\n")
            uf.write(f"Completed tasks: {completed}\n")
            uf.write(f"Uncompleted tasks: {uncompleted}\n")
            uf.write(f"Overdue tasks: {overdue}\n")
            uf.write(f"% Completed: {pct_completed:.2f}%\n")
            uf.write(f"% Uncompleted: {pct_uncompleted:.2f}%\n\n")

    print("Reports generated: task_overview.txt, user_overview.txt")

# For admin: display statistics from the generated overview files


def display_statistics(task_list, username_password):
    '''For admin: display contents of the generated overview files. If they don't exist, generate them first.'''
    if curr_user != "admin":
        print("Only the admin user may view statistics.")
        return

    # Generate reports if missing
    if not os.path.exists("task_overview.txt") or not os.path.exists("user_overview.txt"):
        print("Overview files missing; generating reports now...")
        generate_report(task_list, username_password)

    # Print the contents of the files
    print("\n=== TASK OVERVIEW ===")
    with open("task_overview.txt", "r") as tf:
        print(tf.read())
    print("=== USER OVERVIEW ===")
    with open("user_overview.txt", "r") as uf:
        print(uf.read())


# ----- Main loop -----
while True:
    print()
    menu = input('''Select one of the following Options below:
    r   - Registering a user (admin only)
    a   - Adding a task
    va  - View all tasks
    vm  - View my tasks
    vc  - View your completed tasks
    vca - View all completed tasks (admin only)
    gr  - Generate reports
    ds  - Display statistics (admin only)
    e   - Exit
    : ''').lower().strip()

    if menu == 'r':
        if curr_user != "admin":
            print("Only admin may register new users.")
        else:
            reg_user()

    elif menu == 'a':
        add_task()

    elif menu == 'va':
        view_all()

    elif menu == 'vm':
        view_mine(curr_user)

    elif menu == 'vc':
        # view completed tasks for the current user
        view_completed(curr_user)

    elif menu == 'vca':
        if curr_user != "admin":
            print("Only admin may view all completed tasks.")
        else:
            view_completed(None)   # show completed tasks for all users

    elif menu == 'gr':
        generate_report(task_list, username_password)

    elif menu == 'ds':
        display_statistics(task_list, username_password)

    elif menu == 'e':
        print('Goodbye!!!')
        break

    else:
        print("=" * 50)
        print(f"Invalid input: '{menu}' — not matched")
        print("=" * 50)
