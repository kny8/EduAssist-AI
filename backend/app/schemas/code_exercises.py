from datetime import datetime
from pydantic import BaseModel

class TestCaseSchema(BaseModel):
    """Schema for test cases"""
    id: int
    code_exercise_id: int
    input_data: str
    expected_output: str
    is_hidden: bool = False
    created_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 