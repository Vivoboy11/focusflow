from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from google import genai
from datetime import datetime


# --- DATABASE LOGIC (Local Storage) ---
def load_tasks():
    try:
        with open("tasks.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)


app = FastAPI(title="FocusFlow AI API")

# --- AI CONFIGURATION ---
# IMPORTANT: Paste your actual Gemini API Key here
API_KEY = "AIzaSyDbL2vK72QEN2E4WoItYtrrJIPoSwj3SLc"

client = genai.Client(api_key=API_KEY)
# Using the stable flash model for speed and efficiency
MODEL_ID = "gemini-2.0-flash"


# --- DATA MODELS ---
class ScheduleRequest(BaseModel):
    prompt: str



class TaskItem(BaseModel):
    title: str
    is_done: bool = False
    date: Optional[str] = None


# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "FocusFlow API is online", "version": "1.1.0"}


@app.get("/tasks", response_model=List[TaskItem])
def get_all_tasks():
    """Fetch all tasks from the local JSON database."""
    return load_tasks()


@app.post("/tasks")
def add_manual_task(task: TaskItem):
    """Add a manual task directly to the database."""
    current_tasks = load_tasks()
    new_task = {
        "title": task.title,
        "is_done": task.is_done,
        "date": task.date or datetime.now().strftime("%b %d")
    }
    current_tasks.append(new_task)
    save_tasks(current_tasks)
    return {"message": "Task added", "task": new_task}


@app.post("/generate-schedule")
async def generate_schedule(request: ScheduleRequest):
    """
    The AI Brain: Breaks down user requests into a Pomodoro schedule.
    It automatically saves the generated tasks to the database.
    """
    system_prompt = """
    You are an expert productivity coach. Break the user's request into a structured Pomodoro schedule.
    Include 5-minute short breaks after tasks and 15-minute long breaks after every 4th session.
    You MUST respond ONLY with a valid JSON array of objects.
    Format: [{"task": "Task Name", "duration_minutes": 25}]
    """
    try:
        # Using the modern google-genai SDK
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=request.prompt,
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json"
            }
        )

        # Parse the JSON response
        schedule = json.loads(response.text)

        # Merge into the existing database
        current_tasks = load_tasks()
        for item in schedule:
            current_tasks.append({
                "title": f"{item['duration_minutes']}m • {item['task']}",
                "is_done": False,
                "date": datetime.now().strftime("%b %d")
            })
        save_tasks(current_tasks)

        return {"schedule": schedule, "count": len(schedule)}

    except Exception as e:
        # Catch errors like invalid API keys or JSON formatting issues
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tasks/clear-completed")
def clear_completed():
    """Removes all tasks that are marked as done."""
    current_tasks = load_tasks()
    incomplete = [t for t in current_tasks if not t.get('is_done')]
    save_tasks(incomplete)
    return {"message": "Cleared completed tasks", "remaining": len(incomplete)}


if __name__ == "__main__":
    import uvicorn
    import os
    # The cloud sets the PORT automatically, otherwise fallback to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
