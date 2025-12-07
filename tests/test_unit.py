from datetime import date, timedelta
from os import environ
from unittest.mock import patch

from app import _build_postgres_uri
from models import Task, User


def test_task_is_overdue():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # overdue
    task1 = Task(title="Task 1", due_date=yesterday, is_completed=False)
    assert task1.is_overdue()
    
    # not overdue, due date tomorrow
    task2 = Task(title="Task 2", due_date=tomorrow, is_completed=False)
    assert not task2.is_overdue()
    
    # not overdue, completed task
    task3 = Task(title="Task 3", due_date=yesterday, is_completed=True)
    assert not task3.is_overdue()
    
def test_user_password():
    user = User(username="test")
    
    user.set_password("supersecurepwd")
    assert user.password_hash != "supersecurepwd"
    
    assert user.check_password("supersecurepwd")
    assert not user.check_password("notsupersecurepwd")
    
def test_build_postgres_uri():
    
    env_vars = {
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "supersecurepwd",
        "POSTGRES_HOST": "testhost",
        "POSTGRES_PORT": "5433",
        "POSTGRES_DB": "testdb"
    }

    with patch.dict(environ, env_vars, clear=True):
        uri = _build_postgres_uri()
    assert uri == "postgresql+psycopg2://testuser:supersecurepwd@testhost:5433/testdb"