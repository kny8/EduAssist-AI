from pydantic import BaseModel
from typing import List, Optional

class FunctionSignature(BaseModel):
    name: str
    parameters: List[str]
    return_type: str
    docstring: str
    full_signature: str

class TestCase(BaseModel):
    input_data: str
    expected_output: str
    explanation: str

class CodeGenerationResponse(BaseModel):
    function_signature: FunctionSignature
    sample_test_cases: List[TestCase]
    implementation_hints: List[str] 