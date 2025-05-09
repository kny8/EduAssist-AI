from sqlalchemy import Column, BigInteger, Text, ForeignKey, TIMESTAMP, func, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from models.base import Base


class CodeExercise(Base):
    """
    Represents a coding exercise or problem that students can solve.
    """
    __tablename__ = "code_exercises"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Text, nullable=True)  # e.g., "Easy", "Medium", "Hard"
    category = Column(Text, nullable=True)  # e.g., "Arrays", "Strings", "Algorithms"
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    lecture_id = Column(BigInteger, ForeignKey("public.lectures.id"), nullable=True)
    boilerplate_code = Column(Text, nullable=True)  # Default code structure for the exercise
    language = Column(Text, nullable=True)  # Default programming language for the exercise

    # Relationships
    # test_cases = relationship("TestCase", back_populates="code_exercise", cascade="all, delete-orphan")
    # submissions = relationship("CodeSubmission", back_populates="code_exercise")

    def __repr__(self):
        return f"<CodeExercise(id={self.id}, title={self.title}, difficulty={self.difficulty})>"


class TestCase(Base):
    """
    Represents a test case for a coding exercise.
    """
    __tablename__ = "test_cases"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code_exercise_id = Column(BigInteger, ForeignKey("public.code_exercises.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)  # Whether this test case is hidden from students
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    code_exercise = relationship("CodeExercise", backref="test_cases")

    def __repr__(self):
        return f"<TestCase(id={self.id}, code_exercise_id={self.code_exercise_id}, is_hidden={self.is_hidden})>"


class CodeSubmission(Base):
    """
    Represents a student's submission for a coding exercise.
    """
    __tablename__ = "code_submissions"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    code_exercise_id = Column(BigInteger, ForeignKey("public.code_exercises.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(Text, nullable=False)  # e.g., "python", "javascript", "java"
    status = Column(Text, nullable=False)  # e.g., "submitted", "running", "completed", "error"
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Execution results
    execution_time = Column(Integer, nullable=True)  # in milliseconds
    memory_used = Column(Integer, nullable=True)  # in KB
    results = Column(JSONB, nullable=True)  # Stores test case results in JSON format

    # Relationships
    code_exercise = relationship("CodeExercise", backref="submissions")

    def __repr__(self):
        return f"<CodeSubmission(id={self.id}, user_id={self.user_id}, status={self.status})>"


class CodeChat(Base):
    """
    Represents a chat session specifically for coding assistance.
    This extends the regular chat functionality with code-specific features.
    """
    __tablename__ = "code_chats"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    code_exercise_id = Column(BigInteger, ForeignKey("public.code_exercises.id"), nullable=True)
    code_submission_id = Column(BigInteger, ForeignKey("public.code_submissions.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    # messages = relationship("CodeChatMessage", back_populates="code_chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CodeChat(id={self.id}, user_id={self.user_id})>"


class CodeChatMessage(Base):
    """
    Represents a message in a code chat session.
    """
    __tablename__ = "code_chat_messages"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code_chat_id = Column(BigInteger, ForeignKey("public.code_chats.id"), nullable=False)
    sender = Column(Text, nullable=False)  # "user" or "ai"
    message = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True)  # Optional code snippet included in the message
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    code_chat = relationship("CodeChat", backref="messages")

    def __repr__(self):
        return f"<CodeChatMessage(id={self.id}, sender={self.sender})>"


class CodeSearchResult(Base):
    __tablename__ = "code_search_results"
    __table_args__ = {"schema": "public"}
    id = Column(BigInteger, primary_key=True, index=True)
    code_exercise_id = Column(BigInteger, ForeignKey("public.code_exercises.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, index=True)
    context = Column(Text, nullable=True)
    title = Column(Text)
    link = Column(Text)
    snippet = Column(Text)
    source = Column(Text)
    date = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    last_accessed = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=True)

    # Relationship with CodeExercise
    code_exercise = relationship("CodeExercise", backref="search_results")
