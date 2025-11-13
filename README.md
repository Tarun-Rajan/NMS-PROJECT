🌐 Disaster Recovery Dashboard

A real-time Disaster Recovery & Failover Simulation System built using Flask + TailwindCSS.
It simulates multiple servers, monitors their health, and automatically promotes a Primary server when failures occur.

🚀 Features

Add, Start, Fail, Recover servers

Automatic Primary → Backup failover

Exactly one Primary at all times

Real-time status updates

Response time + last updated timestamp

Clean dashboard UI

Live event logs

🛠️ Tech Stack

Flask (Backend)

HTML + Tailwind CSS (Frontend)

Axios (API calls)

📂 Running the Project
# Clone the repo
git clone <your-repo-link>
cd disaster-recovery-dashboard

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # (Windows)

# Install dependencies
pip install flask

# Run app
python dashboard_controller.py


Open ➜ http://127.0.0.1:8000

📘 Description

The system simulates a distributed server environment:

First available UP server becomes Primary

Others remain Backup

If Primary fails → next UP server is auto-promoted

When server recovers → joins as Backup

Logs track every action

Perfect for demonstrating High Availability, Failover, and Distributed System basics.
