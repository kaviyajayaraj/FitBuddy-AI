from pathlib import Path
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, save_user, save_plan, get_latest_plan, update_plan, get_all_users, delete_user
from app.schemas import UserInput
from app.ai_service import generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate(request: Request, username: str = Form(...), user_id: str = Form(...),
             age: int = Form(...), weight: float = Form(...), goal: str = Form(...),
             intensity: str = Form(...), db: Session = Depends(get_db)):
    try:
        data = UserInput(username=username.strip(), user_id=user_id.strip(), age=age,
                         weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    user = save_user(db, data)
    workout = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
    tip = generate_nutrition_tip_with_flash(data.goal)
    plan = save_plan(db, user, workout, tip)
    return templates.TemplateResponse(request=request, name="result.html", context={
        "user": user, "plan": plan, "workout_plan": workout, "nutrition_tip": tip,
        "display_plan": workout, "updated": False
    })

@router.post("/submit-feedback", response_class=HTMLResponse)
def feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...),
             db: Session = Depends(get_db)):
    user, plan = get_latest_plan(db, user_id.strip())
    if not user or not plan:
        return templates.TemplateResponse(request=request, name="result.html", status_code=404,
            context={"error": "No plan found for that User ID. Generate a plan first."})
    updated = update_workout_plan(plan.original_plan, feedback, user.goal, user.intensity)
    tip = generate_nutrition_tip_with_flash(user.goal)
    update_plan(db, plan, updated, feedback, tip)
    return templates.TemplateResponse(request=request, name="result.html", context={
        "user": user, "plan": plan, "workout_plan": plan.original_plan,
        "display_plan": updated, "nutrition_tip": tip, "updated": True
    })

@router.get("/view-all-users", response_class=HTMLResponse)
def view_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users})

@router.post("/delete-user")
def remove_user(user_id: str = Form(...), db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)

@router.get("/api/health")
def health():
    return {"status": "ok", "app": "FitBuddy"}

@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    return [{"user_id": u.user_id, "username": u.username, "age": u.age,
             "weight": u.weight, "goal": u.goal, "intensity": u.intensity,
             "plans": [{"original_plan": p.original_plan, "updated_plan": p.updated_plan,
                        "feedback": p.feedback, "nutrition_tip": p.nutrition_tip} for p in u.plans]}
            for u in get_all_users(db)]
