from datetime import date

from app import Task


def test_task_creation():
    """Test if a task is created with the correct default values."""
    title = "Test Study Session"
    task = Task(title=title)
    
    assert task.title == title
    assert task.is_done is False
    assert task.task_date == str(date.today())
    assert task.priority == 2

def test_task_to_dict():
    """Test if the to_dict method returns the correct dictionary format."""
    task = Task(title="Complete Assignment", priority=3)
    data = task.to_dict()
    
    assert data["title"] == "Complete Assignment"
    assert data["priority"] == 3
    assert "date" in data
