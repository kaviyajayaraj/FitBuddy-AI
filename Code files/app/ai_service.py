"""Gemini integration with a safe local demo fallback when GOOGLE_API_KEY is absent."""
import os
from dotenv import load_dotenv
load_dotenv()

def _gemini(prompt: str, model: str) -> str | None:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key: return None
    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model=model, contents=prompt)
        return (response.text or "").strip() or None
    except Exception as exc:
        # Do not expose secrets or raw provider errors to the browser.
        print(f"Gemini request failed ({type(exc).__name__}); using local fallback.")
        return None

def generate_workout_gemini(username, age, weight, goal, intensity):
    prompt = f"""Create a safe, practical 7-day beginner-friendly fitness plan.
User: {username}; age: {age}; weight: {weight} kg; goal: {goal}; intensity: {intensity}.
For each day include focus, 5-10 minute warm-up, exercises with sets/reps or duration,
and cooldown/recovery. Include rest/recovery days. Use clear plain text, one day per section.
Avoid extreme advice. Mention stopping if pain occurs and adapting to ability."""
    result = _gemini(prompt, os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-pro"))
    if result: return result
    return f"""DAY 1 — Full-body foundation
Warm-up: 5–10 minutes easy walking and mobility.
Main: Chair squats 2×10; wall push-ups 2×8; glute bridges 2×10; marching 2×1 minute.
Cooldown: Gentle stretching for 5 minutes.

DAY 2 — Cardio
Warm-up: 5 minutes easy pace.
Main: Brisk walk 15–25 minutes at a conversational pace.
Cooldown: Slow walk and gentle calf/hamstring stretches.

DAY 3 — Strength
Warm-up: 5–10 minutes mobility.
Main: Sit-to-stand 2×10; bird-dog 2×8/side; incline push-ups 2×8; calf raises 2×12.
Cooldown: Easy stretching.

DAY 4 — Recovery
20 minutes gentle walking or mobility. Keep effort easy.

DAY 5 — Cardio + core
Warm-up: 5 minutes easy walking.
Main: Walk 15–25 minutes; dead bug 2×8/side; standing knee raises 2×10/side.
Cooldown: Gentle stretching.

DAY 6 — Full-body
Warm-up: 5–10 minutes mobility.
Main: Chair squats 2×10; wall push-ups 2×8; glute bridges 2×10; bird-dog 2×8/side.
Cooldown: Gentle stretching.

DAY 7 — Rest
Rest or take a comfortable easy walk.

Demo plan for goal: {goal}; selected intensity: {intensity}.
Increase difficulty gradually only when the current level feels comfortable."""

def generate_nutrition_tip_with_flash(goal):
    prompt = f"Give one concise, practical, general nutrition or recovery tip for this fitness goal: {goal}. Avoid medical claims."
    result = _gemini(prompt, os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash"))
    if result: return result
    tips = {
        "Muscle gain": "Include a source of protein in regular meals and eat enough overall to support training and recovery.",
        "Weight loss": "Build meals around vegetables, protein-rich foods, and high-fibre carbohydrates; aim for sustainable portions.",
        "General wellness": "Stay hydrated throughout the day and include a variety of vegetables, fruit, whole grains, and protein.",
        "Flexibility": "Support recovery with regular hydration and balanced meals; avoid forcing stretches through pain."
    }
    return tips.get(goal, "Stay hydrated and choose balanced meals that support your activity and recovery.")

def update_workout_plan(original_plan, feedback, goal, intensity):
    prompt = f"""Revise this 7-day workout plan according to the user's feedback.
Goal: {goal}; intensity: {intensity}
Original plan:
{original_plan}
User feedback: {feedback}
Keep a clear day-by-day structure, include recovery, and avoid unsafe or extreme advice."""
    result = _gemini(prompt, os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-pro"))
    if result: return result
    return original_plan + f"\n\nUPDATED PLAN NOTE (local demo): Your requested change was: {feedback}. Adjust the relevant sessions gradually, preserve recovery, and stop if you feel pain. Add yoga/cardio/rest as appropriate to your feedback."
