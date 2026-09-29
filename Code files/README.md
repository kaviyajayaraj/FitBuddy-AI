# FitBuddy — AI Fitness Plan Generator

A FastAPI + Jinja2 + SQLite web app based on the supplied FitBuddy project document. It supports 7-day workout plans, nutrition/recovery tips, feedback-based revisions, a coach dashboard, and JSON API endpoints.

## Requirements
- Python 3.10+
- Optional: Google AI Studio API key for live Gemini generation

## Run in VS Code (Windows PowerShell)
1. Extract the ZIP and open the `FitBuddy` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
4. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Optional live Gemini AI: copy `.env.example` to `.env`, then add your API key to `GOOGLE_API_KEY`. Keep `.env` private; it is ignored by Git. Model IDs can be changed in `.env` if needed.
6. Start the app from the project root:
   ```powershell
   uvicorn app.main:app --reload
   ```
7. Open:
   - Web app: http://127.0.0.1:8000
   - API docs: http://127.0.0.1:8000/docs
   - Health check: http://127.0.0.1:8000/api/health
   - Users API: http://127.0.0.1:8000/api/users

Without an API key, FitBuddy uses a clearly labelled local fallback response so you can test the complete flow. With a valid key, requests use the configured Gemini models.

## Test the app
1. Fill the home form and click **Generate my 7-day plan**.
2. Confirm the plan and nutrition tip appear.
3. Submit feedback such as “Add more cardio and one extra recovery day”.
4. Open **Coach dashboard** to inspect original and updated plans.
5. Test `/api/health` and `/api/users` in a browser or `/docs`.

## Project structure
```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── database.py
│   ├── ai_service.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   └── all_users.html
│   └── static/style.css
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Notes
- The SQLite database `fitbuddy.db` is created automatically at first launch.
- The coach dashboard is a demonstration endpoint and has no authentication. Add authentication and authorization before exposing it publicly.
- This is general fitness information, not medical advice. Consult a qualified professional if you have health concerns, and stop exercises that cause pain.
