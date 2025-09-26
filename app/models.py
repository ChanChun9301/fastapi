from sqlalchemy import Column, Integer, String, ForeignKey,Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import date

from .database import Base
Base = declarative_base()

class Course(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)  # RichTextField = long text
    image = Column(String, nullable=True)        # Store image path or URL
    created = Column(Date, default=date.today)
    videos = relationship("Video", back_populates="course")

    def __repr__(self):
        return f"<Course(title={self.title})>"

class Video(Base):
    __tablename__ = "video"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    language = Column(String(255))  # You can validate choices at the Pydantic level
    author = Column(String(255))
    file = Column(String(1000), nullable=True)  # File path
    description = Column(String, nullable=True) # RichTextField = long text
    created = Column(Date, default=date.today)
    duration = Column(Integer)
    course_id = Column(Integer, ForeignKey("course.id"))
    course = relationship("Course", back_populates="videos")

    def __repr__(self):
        return f"<Video(title={self.title}, course_id={self.course_id})>"
