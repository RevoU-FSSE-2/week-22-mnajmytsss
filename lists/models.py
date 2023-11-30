from datetime import datetime
from sqlalchemy import Column, Date, Integer, String
from db import db

class List(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    priority = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False)
    dueDate = Column(Date, nullable=False)
    date = Column(Date, default=datetime.utcnow, nullable=False)  # Menggunakan fungsi default tanpa pemanggilan

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "dueDate": self.dueDate.strftime('%Y-%m-%d'),  # Format tanggal sesuai kebutuhan
            "date": self.date.strftime('%Y-%m-%d')  # Format tanggal sesuai kebutuhan
        }
