import os

import pytest
from app import create_app
from extensions import db
from models import Task, User


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test"
       
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

def test_register_login_flow(client):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "supersecurepwd",
            "confirm": "supersecurepwd"
            },
        follow_redirects=True,
    )
    assert User.query.filter_by(username="testuser").first() is not None

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "supersecurepwd"},
        follow_redirects=True,
    )
    assert b"Logged in successfully." in response.data

def test_task_creation(client, db_session):
    user = User(username="testuser")
    user.set_password("supersecurepwd")
    db_session.add(user)
    db_session.commit()

    client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "supersecurepwd"
            },
        follow_redirects=True,
    )

    client.post(
        "/tasks/new",
        data={
            "title": "CI/CD task",
            "description": "MLP exercise",
            "due_date": "2025-12-7"
            },
        follow_redirects=True,
    )
    assert Task.query.filter_by(title="CI/CD task", user_id=user.id).first() is not None
    

def test_edit_task(client, db_session):
    user = User(username="testuser")
    user.set_password("supersecurepwd")
    db_session.add(user)
    db_session.commit()
    task = Task(title="CI/CD task", user_id=user.id)
    db_session.add(task)
    db_session.commit()
    
    client.post(
        "/login",
        data={
            "username": "testuser", 
            "password": "supersecurepwd"
            },
        follow_redirects=True,
    )
    client.post(
        f"/tasks/{task.id}/edit",
        data={
            "title": "Updated CI/CD task",
            "description": "Updated desc",
            "due_date": "2025-12-14"
            },
        follow_redirects=True,
    )
    updated_task = Task.query.get(task.id)
    assert updated_task.title == "Updated CI/CD task"
    assert updated_task.description == "Updated desc"
    assert str(updated_task.due_date) == "2025-12-14"