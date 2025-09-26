from sqlalchemy.orm import Session
from . import models, schemas

def get_courses(db: Session):
    return db.query(models.Course).all()

def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_video(db: Session, course_id: int, video: schemas.VideoCreate):
    db_video = models.Video(**video.dict(), course_id=course_id)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video
