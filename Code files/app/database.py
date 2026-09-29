from pathlib import Path
from sqlalchemy import create_engine, String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "fitbuddy.db"
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(80))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_pk: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[User] = relationship(back_populates="plans")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def save_user(db, data):
    user = db.query(User).filter_by(user_id=data.user_id).first()
    if user:
        user.username, user.age, user.weight = data.username, data.age, data.weight
        user.goal, user.intensity = data.goal, data.intensity
    else:
        user = User(**data.model_dump())
        db.add(user)
    db.commit(); db.refresh(user)
    return user

def save_plan(db, user, plan, tip):
    record = Plan(user_pk=user.id, original_plan=plan, nutrition_tip=tip)
    db.add(record); db.commit(); db.refresh(record)
    return record

def get_latest_plan(db, user_id):
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user: return None, None
    plan = db.query(Plan).filter_by(user_pk=user.id).order_by(Plan.id.desc()).first()
    return user, plan

def update_plan(db, plan, updated, feedback, tip):
    plan.updated_plan, plan.feedback, plan.nutrition_tip = updated, feedback, tip
    db.commit(); db.refresh(plan)
    return plan

def get_all_users(db):
    return db.query(User).order_by(User.created_at.desc()).all()

def delete_user(db, user_id):
    user = db.query(User).filter_by(user_id=user_id).first()
    if user:
        db.delete(user); db.commit(); return True
    return False
