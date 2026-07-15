# Phần 1: Báo cáo lỗi cấu hình
# Dưới đây là 3 lỗi sai đang phá vỡ cấu trúc quan hệ của hệ thống:

# 1. Lỗi ở quan hệ 1-N (Khoa ↔ Sinh viên)

# Tên lỗi: Sai tên thuộc tính tham chiếu trong đồng bộ ngược (back_populates).

# Vị trí dòng code gây lỗi: students = relationship("Student", back_populates="department_id") (nằm trong class Department).

# Nguyên nhân: Thuộc tính back_populates yêu cầu bạn truyền vào tên của biến relationship ở Model đối diện, chứ không phải tên của cột khóa ngoại (Foreign Key). Ở class Student, biến relationship được đặt tên là department, không phải department_id.

# Cách khắc phục: Sửa back_populates="department_id" thành back_populates="department".

# 2. Lỗi ở quan hệ 1-1 (Sinh viên ↔ Hồ sơ bảo mật)

# Tên lỗi: Thiếu tham số giới hạn danh sách (ORM) và ràng buộc duy nhất (Database) cho quan hệ 1-1.

# Vị trí dòng code gây lỗi: * Trong Student: profile = relationship("Profile", back_populates="student")

# Trong Profile: student_id = Column(Integer, ForeignKey("students.id"))

# Nguyên nhân: Theo mặc định, khi thiết lập khóa ngoại, SQLAlchemy ORM sẽ coi đó là quan hệ 1-N (Một sinh viên trả về một danh sách các hồ sơ). Để ép nó thành 1-1 ở tầng ORM, bạn phải báo cho SQLAlchemy biết không sử dụng danh sách bằng tham số uselist=False. Đồng thời, ở tầng Database, cột khóa ngoại student_id cần phải là duy nhất (unique=True) để không có 2 hồ sơ nào trỏ về cùng 1 sinh viên.

# Cách khắc phục: * Ở class Student, thêm uselist=False vào relationship: profile = relationship("Profile", back_populates="student", uselist=False).

# Ở class Profile, thêm unique=True vào khóa ngoại: student_id = Column(Integer, ForeignKey("students.id"), unique=True).

# 3. Lỗi ở quan hệ N-N (Sinh viên ↔ Môn học)

# Tên lỗi: Thiếu khai báo bảng trung gian (secondary).

# Vị trí dòng code gây lỗi: courses = relationship("Course", back_populates="students") (trong class Student) và khai báo tương tự trong class Course.

# Nguyên nhân: Trong quan hệ Nhiều - Nhiều, cơ sở dữ liệu không thể liên kết trực tiếp hai bảng mà phải thông qua một bảng trung gian (ở đây là student_course). Nếu bạn không chỉ định rõ bảng trung gian này thông qua tham số secondary trong ORM, SQLAlchemy sẽ báo lỗi không tìm thấy đường dẫn liên kết.

# Cách khắc phục: Thêm tham số secondary=student_course vào relationship ở class Student (và có thể cả ở Course nếu cần truy xuất ngược chiều chuẩn xác).



#Sourch code
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base # Giả định Base đã được khai báo từ hệ thống

# 1. Bảng trung gian cho quan hệ Nhiều - Nhiều (Student - Course)
student_course = Table(
    "student_course", 
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

# 2. Khai báo các Model
class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    # [ĐÃ SỬA]: back_populates trỏ đúng vào tên biến relationship "department" ở class Student
    students = relationship("Student", back_populates="department")


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    
    # Quan hệ 1 - N với Department (Nhiều Sinh viên thuộc 1 Khoa)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="students")
    
    # [ĐÃ SỬA]: Thêm uselist=False để đảm bảo quan hệ 1-1 ở tầng ORM
    profile = relationship("Profile", back_populates="student", uselist=False)
    
    # [ĐÃ SỬA]: Thêm tham số secondary chỉ định bảng trung gian cho quan hệ N-N
    courses = relationship("Course", secondary=student_course, back_populates="students")


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String(255))
    
    # [ĐÃ SỬA]: Thêm unique=True để đảm bảo quan hệ 1-1 ở tầng Database
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    student = relationship("Student", back_populates="profile")


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    
    # [ĐÃ SỬA]: Thêm tham số secondary chỉ định bảng trung gian đồng bộ với biến courses bên Student
    students = relationship("Student", secondary=student_course, back_populates="courses")