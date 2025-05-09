import time

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import datetime
import os
import tempfile
import shutil
import requests

from database.database import get_db
from models import CodeExercise, TestCase, CodeSubmission, CodeChat, CodeChatMessage

# Import AI-related libraries for code generation and analysis
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline

from models.code_exercises import CodeSearchResult

router = APIRouter()


# Pydantic models for request/response
class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_hidden: bool = False


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseResponse(TestCaseBase):
    id: int
    code_exercise_id: int
    created_at: datetime.datetime
    input_data: str
    expected_output: str
    is_hidden: bool = False

    class Config:
        from_attributes = True


class CodeExerciseBase(BaseModel):
    title: Optional[str]
    description: Optional[str]
    difficulty: Optional[str] = None
    category: Optional[str] = None
    lecture_id: Optional[int] = None
    boilerplate_code: Optional[str] = None
    language: Optional[str] = None


class CodeExerciseCreate(CodeExerciseBase):
    test_cases: Optional[List[TestCaseCreate]] = None


class CodeExerciseResponse(CodeExerciseBase):
    id: int
    created_at: datetime.datetime
    test_cases: Optional[List[TestCaseResponse]] = None

    class Config:
        from_attributes = True


class CodeSubmissionBase(BaseModel):
    code: str
    language: str


class CodeSubmissionCreate(CodeSubmissionBase):
    user_id: int
    code_exercise_id: int


class CodeSubmissionResponse(CodeSubmissionBase):
    id: int
    user_id: int
    code_exercise_id: int
    status: str
    created_at: datetime.datetime
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    results: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CodeChatMessageBase(BaseModel):
    sender: str
    message: str
    code_snippet: Optional[str] = None


class CodeChatMessageCreate(CodeChatMessageBase):
    pass


class CodeChatMessageResponse(CodeChatMessageBase):
    id: int
    code_chat_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CodeChatBase(BaseModel):
    user_id: int
    code_exercise_id: Optional[int] = None
    code_submission_id: Optional[int] = None


class CodeChatCreate(CodeChatBase):
    pass


class CodeChatResponse(CodeChatBase):
    id: int
    created_at: datetime.datetime
    messages: List[CodeChatMessageResponse] = []

    class Config:
        from_attributes = True


class TestCaseGenerationRequest(BaseModel):
    code_exercise_id: int
    problem_description: str
    sample_code: Optional[str] = None
    num_test_cases: int = 3


class TestCaseGenerationResponse(BaseModel):
    test_cases: List[TestCaseBase]


# Initialize AI model for code generation and analysis
# Note: In a production environment, you would want to load these models more efficiently
model_name = "mistralai/Mistral-7B-Instruct-v0.1"  # You can use a more code-specific model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512
)
llm = HuggingFacePipeline(pipeline=pipe)


# Add new model for search request

# API Routes
@router.post("/", response_model=CodeExerciseResponse)
def create_code_exercise(exercise: CodeExerciseCreate, db: Session = Depends(get_db)):
    """Create a new coding exercise with optional test cases."""
    db_exercise = CodeExercise(
        title=exercise.title,
        description=exercise.description,
        difficulty=exercise.difficulty,
        category=exercise.category,
        lecture_id=exercise.lecture_id,
        boilerplate_code=exercise.boilerplate_code,
        language=exercise.language
    )
    db.add(db_exercise)
    db.flush()

    # Add test cases if provided
    if exercise.test_cases:
        for tc in exercise.test_cases:
            db_test_case = TestCase(
                code_exercise_id=db_exercise.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=tc.is_hidden
            )
            db.add(db_test_case)

    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.get("/", response_model=List[CodeExerciseResponse])
def list_code_exercises(
        skip: int = 0,
        limit: int = 100,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        lecture_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """List all coding exercises with optional filtering."""
    query = db.query(CodeExercise)

    if difficulty:
        query = query.filter(CodeExercise.difficulty == difficulty)
    if category:
        query = query.filter(CodeExercise.category == category)
    if lecture_id:
        query = query.filter(CodeExercise.lecture_id == lecture_id)

    exercises = query.offset(skip).limit(limit).all()
    return exercises


@router.get("/{exercise_id}", response_model=CodeExerciseResponse)
def get_code_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Get a specific coding exercise by ID."""
    exercise = db.query(CodeExercise).filter(CodeExercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Code exercise not found")
    return exercise


@router.put("/{exercise_id}", response_model=CodeExerciseResponse)
def update_code_exercise(exercise_id: int, exercise: CodeExerciseBase, db: Session = Depends(get_db)):
    """Update a code exercise."""
    db_exercise = db.query(CodeExercise).filter(CodeExercise.id == exercise_id).first()
    if not db_exercise:
        raise HTTPException(status_code=404, detail="Code exercise not found")

    # Update fields
    for field, value in exercise.dict(exclude_unset=True).items():
        setattr(db_exercise, field, value)

    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.post("/{exercise_id}/test-cases", response_model=TestCaseGenerationResponse)
def generate_test_cases(request: TestCaseGenerationRequest, db: Session = Depends(get_db)):
    """Generate test cases for a coding exercise using AI."""
    # Get the exercise
    exercise = db.query(CodeExercise).filter(CodeExercise.id == request.code_exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Code exercise not found")

    # Prepare prompt for the AI model with better test case generation guidance
    prompt = f"""You are an expert programming instructor and test case designer. Generate {request.num_test_cases} comprehensive test cases for the following programming problem.

    Problem Description:
    {request.problem_description}

    For each test case:
    1. Analyze the problem requirements and constraints
    2. Consider edge cases and boundary conditions specific to this problem
    3. Include a mix of normal cases and special cases
    4. Test different aspects of the problem requirements
    5. Ensure the input and output formats match the problem requirements
    6. Consider potential error cases and invalid inputs

    For each test case, provide:
    1. A brief description of what the test case is checking
    2. The exact input data
    3. The expected output
    4. An explanation of why this output is expected
    5. Any special considerations or edge cases this test case covers

    Format each test case EXACTLY as follows:

    TEST CASE [number]:
    DESCRIPTION: [what this test case verifies]
    INPUT_DATA: [exact input]
    EXPECTED_OUTPUT: [exact expected output]
    EXPLANATION: [why this output is expected]
    EDGE_CASE: [yes/no] - [explanation if yes]

    Make the test cases thorough and ensure they cover various scenarios.
    """

    if request.sample_code:
        prompt += f"\n\nHere's a sample solution to help understand the expected behavior:\n```\n{request.sample_code}\n```\n\nAnalyze this code and ensure the test cases cover its functionality and potential edge cases."

    # Generate test cases using the AI model
    response = llm.invoke(prompt)

    # Parse the response to extract test cases
    test_cases = []
    current_tc = {}
    description = None

    try:
        # Split response into test case blocks
        test_blocks = response.split('TEST CASE')[1:]  # Skip empty first part

        for block in test_blocks:
            lines = block.strip().split('\n')
            current_tc = {}

            for line in lines:
                line = line.strip()
                if line.startswith('DESCRIPTION:'):
                    description = line[12:].strip()
                elif line.startswith('INPUT_DATA:'):
                    current_tc['input_data'] = line[11:].strip()
                elif line.startswith('EXPECTED_OUTPUT:'):
                    current_tc['expected_output'] = line[16:].strip()

                    # If we have both input and output, create a test case
                    if 'input_data' in current_tc and current_tc['input_data']:
                        # Filter out placeholder test cases
                        input_data = current_tc['input_data']
                        if (not '[exact' in input_data and 
                            not '{exact' in input_data and
                            input_data.strip() != '' and
                            not input_data.lower() == 'sample input'):
                            
                            test_case = TestCaseBase(
                                input_data=current_tc['input_data'],
                                expected_output=current_tc['expected_output'],
                                is_hidden=False
                            )
                            test_cases.append(test_case)
                        current_tc = {}

        # If we didn't get enough test cases, generate some backup cases
        if len(test_cases) < request.num_test_cases:
            # Generate additional test cases with a different prompt
            backup_prompt = f"""Generate {request.num_test_cases - len(test_cases)} additional test cases for this problem:
            {request.problem_description}

            Focus on edge cases and special conditions.
            Format: 
            INPUT_DATA: [input]
            EXPECTED_OUTPUT: [output]
            """

            backup_response = llm.invoke(backup_prompt)

            # Parse backup test cases
            current_tc = {}
            for line in backup_response.split('\n'):
                line = line.strip()
                if line.startswith('INPUT_DATA:'):
                    current_tc['input_data'] = line[11:].strip()
                elif line.startswith('EXPECTED_OUTPUT:'):
                    current_tc['expected_output'] = line[16:].strip()
                    if 'input_data' in current_tc:
                        # Filter out placeholder test cases
                        input_data = current_tc['input_data']
                        if (not '[exact' in input_data and 
                            not '{exact' in input_data and
                            input_data.strip() != '' and
                            not input_data.lower() == 'sample input'):
                            test_cases.append(TestCaseBase(**current_tc))
                        current_tc = {}
                        if len(test_cases) >= request.num_test_cases:
                            break

    except Exception as e:
        # If parsing fails, create intelligent default test cases based on problem type
        problem_desc = request.problem_description.lower()
        test_cases = []

        # Use LLM to analyze the problem and generate appropriate test cases
        analysis_prompt = f"""Analyze this programming problem and suggest appropriate test cases:
        {request.problem_description}

        What type of problem is this? (e.g., sorting, arithmetic, string manipulation)
        What are the key edge cases to test?
        What are some typical input/output examples?

        Format your response as:
        PROBLEM_TYPE: [type]
        TEST_CASES:
        INPUT_DATA: [input]
        EXPECTED_OUTPUT: [output]
        """

        analysis = llm.invoke(analysis_prompt)

        # Parse the analysis and create test cases
        current_tc = {}
        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith('INPUT_DATA:'):
                current_tc['input_data'] = line[11:].strip()
            elif line.startswith('EXPECTED_OUTPUT:'):
                current_tc['expected_output'] = line[16:].strip()
                if 'input_data' in current_tc:
                    # Filter out placeholder test cases
                    input_data = current_tc['input_data']
                    if (not '[exact' in input_data and 
                        not '{exact' in input_data and
                        input_data.strip() != '' and
                        not input_data.lower() == 'sample input'):
                        test_cases.append(TestCaseBase(**current_tc))
                    current_tc = {}
                    if len(test_cases) >= request.num_test_cases:
                        break

        # If we still don't have enough test cases, add some generic ones
        while len(test_cases) < request.num_test_cases:
            case_num = len(test_cases) + 1
            test_cases.append(TestCaseBase(
                input_data=f"5, {case_num}" if case_num % 2 == 0 else f"{case_num}, 5",
                expected_output=f"{5 + case_num}" if case_num % 2 == 0 else f"{5 + case_num}"
            ))

    return TestCaseGenerationResponse(test_cases=test_cases[:request.num_test_cases])


@router.get("/{exercise_id}/test-cases", response_model=List[TestCaseResponse])
def get_submission(exercise_id: int, db: Session = Depends(get_db)):
    """Get a specific code submission by ID."""
    cases = db.query(TestCase).filter(TestCase.code_exercise_id == exercise_id).all()
    if not cases:
        raise HTTPException(status_code=404, detail="cases not found")
    return cases


@router.post("/{exercise_id}/submissions", response_model=CodeSubmissionResponse)
def submit_code(submission: CodeSubmissionCreate, db: Session = Depends(get_db)):
    """Submit code for a coding exercise."""
    # Check if the exercise exists
    exercise = db.query(CodeExercise).filter(CodeExercise.id == submission.code_exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Code exercise not found")

    # Create the submission
    db_submission = CodeSubmission(
        user_id=submission.user_id,
        code_exercise_id=submission.code_exercise_id,
        code=submission.code,
        language=submission.language,
        status="submitted"
    )
    db.add(db_submission)
    db.flush()

    # Get test cases for this exercise
    test_cases = db.query(TestCase).filter(TestCase.code_exercise_id == submission.code_exercise_id).all()

    results = {
        "passed": 0,
        "failed": 0,
        "test_results": []
    }

    # Prepare the prompt for code execution
    def create_execution_prompt(code: str, test_case: TestCase) -> str:
        return f"""You are a code execution engine and code analysis expert. Execute the following {submission.language} code with the given input and provide detailed analysis.

        CODE:
        ```{submission.language}
        {code}
        ```

        INPUT:
        {test_case.input_data}

        Execute the code with this input and provide:
        1. The exact output (no additional text, just the output)
        2. Any errors encountered (if any)
        3. Execution success (true/false)
        4. Performance metrics (execution time, memory usage)
        5. Code analysis:
           - Time complexity
           - Space complexity
           - Potential improvements
           - Edge cases handled
           - Error handling effectiveness

        Format your response exactly as follows:
        OUTPUT: [the exact output]
        ERROR: [error message or "None" if no error]
        SUCCESS: [true/false]
        EXECUTION_TIME: [time in milliseconds]
        MEMORY_USED: [memory in KB]
        ANALYSIS:
        - Time Complexity: [O(...)]
        - Space Complexity: [O(...)]
        - Improvements: [list of potential improvements]
        - Edge Cases: [list of edge cases handled]
        - Error Handling: [assessment of error handling]
        """

    total_execution_time = 0
    max_memory_used = 0

    # Execute code against each test case using LLM
    for tc in test_cases:
        start_time = time.time()

        # Get LLM to execute the code
        execution_prompt = create_execution_prompt(submission.code, tc)
        execution_result = llm.invoke(execution_prompt)

        # Parse LLM response
        output = ""
        error = None
        success = False

        for line in execution_result.split('\n'):
            line = line.strip()
            if line.startswith('OUTPUT:'):
                output = line[7:].strip()
            elif line.startswith('ERROR:'):
                error_msg = line[6:].strip()
                error = None if error_msg == "None" else error_msg
            elif line.startswith('SUCCESS:'):
                success = line[8:].strip().lower() == 'true'

        # Calculate execution time
        exec_time = int((time.time() - start_time) * 1000)
        total_execution_time += exec_time

        # Compare output with expected
        passed = success and output.strip() == tc.expected_output.strip()

        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        results["test_results"].append({
            "test_case_id": tc.id,
            "input": tc.input_data,
            "expected_output": tc.expected_output,
            "actual_output": output if success else error,
            "passed": passed,
            "error": error if not success else None
        })

        # For memory tracking, we'll use a simpler approach since we're using LLM
        max_memory_used = max(max_memory_used, len(submission.code) * 2)  # Simple estimation

    # Update submission with results
    db_submission.status = "completed" if results["failed"] == 0 else "failed"
    db_submission.execution_time = total_execution_time
    db_submission.memory_used = max_memory_used
    db_submission.results = results

    # Add an analysis of the code using LLM
    analysis_prompt = f"""Analyze the following code submission and provide feedback:

    Code:
    ```{submission.language}
    {submission.code}
    ```

    Test Results:
    Passed: {results['passed']}
    Failed: {results['failed']}

    Provide a brief analysis of:
    1. Code quality and style
    2. Potential improvements
    3. Any issues found
    4. Performance considerations

    Keep your response concise and focused on helping the student improve.
    """

    code_analysis = llm.invoke(analysis_prompt)
    db_submission.analysis = code_analysis

    db.commit()
    db.refresh(db_submission)

    return db_submission


@router.get("/{exercise_id}/submissions/{submission_id}", response_model=CodeSubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Get a specific code submission by ID."""
    submission = db.query(CodeSubmission).filter(CodeSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/{exercise_id}/submissions/user/{user_id}", response_model=List[CodeSubmissionResponse])
def get_user_submissions(
        user_id: int,
        exercise_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Get all submissions for a specific user."""
    query = db.query(CodeSubmission).filter(CodeSubmission.user_id == user_id)

    if exercise_id:
        query = query.filter(CodeSubmission.code_exercise_id == exercise_id)

    submissions = query.order_by(CodeSubmission.created_at.desc()).all()
    return submissions


# Code Chat Routes
@router.post("/{exercise_id}/chat", response_model=CodeChatResponse)
def create_code_chat(chat: CodeChatCreate, db: Session = Depends(get_db)):
    """Create a new code chat session."""
    db_chat = CodeChat(
        user_id=chat.user_id,
        code_exercise_id=chat.code_exercise_id,
        code_submission_id=chat.code_submission_id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    # Add initial AI message
    welcome_message = CodeChatMessage(
        code_chat_id=db_chat.id,
        sender="ai",
        message="Hello! I'm your coding assistant. How can I help you with your code today?"
    )
    db.add(welcome_message)
    db.commit()

    # Refresh to include the welcome message
    db.refresh(db_chat)
    return db_chat


@router.get("/chat/{chat_id}", response_model=CodeChatResponse)
def get_code_chat(chat_id: int, db: Session = Depends(get_db)):
    """Get a specific code chat by ID with all messages."""
    chat = db.query(CodeChat).filter(CodeChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.post("/chat/{chat_id}/messages", response_model=CodeChatMessageResponse)
def add_chat_message(
        chat_id: int,
        message: CodeChatMessageCreate,
        db: Session = Depends(get_db)
):
    """Add a message to a code chat."""
    # Check if chat exists
    chat = db.query(CodeChat).filter(CodeChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Add the message
    db_message = CodeChatMessage(
        code_chat_id=chat_id,
        sender=message.sender,
        message=message.message,
        code_snippet=message.code_snippet
    )
    db.add(db_message)
    db.flush()

    # If this is a user message, generate an AI response
    if message.sender == "user":
        # Get context for the AI response
        exercise = None
        submission = None

        if chat.code_exercise_id:
            exercise = db.query(CodeExercise).filter(CodeExercise.id == chat.code_exercise_id).first()

        if chat.code_submission_id:
            submission = db.query(CodeSubmission).filter(CodeSubmission.id == chat.code_submission_id).first()

        # Get previous messages for context (only user messages and AI responses)
        previous_messages = db.query(CodeChatMessage).filter(
            and_(
                CodeChatMessage.code_chat_id == chat_id,
                CodeChatMessage.id != db_message.id
            )
        ).order_by(CodeChatMessage.created_at).all()

        # Prepare prompt for AI
        prompt = "You are an expert programming tutor helping a student with their code. Provide clear, concise responses focused on helping them understand and improve their code. Do not mention that you are an AI or reference the conversation history. Just respond naturally as a tutor would.\n\n"

        if exercise:
            prompt += f"Context - Problem: {exercise.title}\n{exercise.description}\n\n"

        if submission:
            prompt += f"Context - Student's Code:\n```\n{submission.code}\n```\n\n"

            if submission.results:
                prompt += f"Context - Test Results: {submission.results['passed']} tests passed, {submission.results['failed']} tests failed.\n\n"

        # Add conversation history for context
        prompt += "Previous conversation:\n"
        for prev_msg in previous_messages[-5:]:  # Only use last 5 messages
            role = "Student" if prev_msg.sender == "user" else "Tutor"
            prompt += f"{role}: {prev_msg.message}\n"
            if prev_msg.code_snippet:
                prompt += f"Code:\n```\n{prev_msg.code_snippet}\n```\n"

        prompt += f"\nStudent: {message.message}\n"
        if message.code_snippet:
            prompt += f"Code:\n```\n{message.code_snippet}\n```\n"

        prompt += "\nProvide your response as a tutor:"

        # Generate AI response
        ai_response = llm.invoke(prompt)

        # Clean the response
        def clean_ai_response(response: str) -> tuple[str, str | None]:
            # Remove any mentions of being an AI, system prompts, or conversation history
            response = response.replace("As an AI", "As a tutor")
            response = response.replace("As an expert programming tutor", "")

            # Extract code snippets
            code_snippet = None
            message_text = response

            # Look for code blocks
            if "```" in response:
                parts = response.split("```")
                message_parts = []
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Not a code block
                        message_parts.append(part.strip())
                    else:  # Code block
                        if not code_snippet:  # Take the first code block
                            code_snippet = part.strip()
                            if code_snippet.startswith("python"):
                                code_snippet = code_snippet[6:].strip()
                message_text = " ".join(part for part in message_parts if part)

            # Clean up the message
            message_text = message_text.strip()
            if message_text.startswith("Tutor:"):
                message_text = message_text[6:].strip()

            return message_text, code_snippet

        # Clean the AI response
        message_text, code_snippet = clean_ai_response(ai_response)

        # Add AI response
        ai_message = CodeChatMessage(
            code_chat_id=chat_id,
            sender="ai",
            message=message_text,
            code_snippet=code_snippet
        )
        db.add(ai_message)

    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/chat/user/{user_id}", response_model=List[CodeChatResponse])
def get_user_chats(
        user_id: int,
        exercise_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Get all code chats for a specific user."""
    query = db.query(CodeChat).filter(CodeChat.user_id == user_id)

    if exercise_id:
        query = query.filter(CodeChat.code_exercise_id == exercise_id)

    chats = query.order_by(CodeChat.created_at.desc()).all()
    return chats


# Add this new endpoint after the other endpoints
@router.post("/{exercise_id}/upload-question", response_model=Dict[str, str])
async def upload_question_file(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """Upload a question file and extract text from it."""
    # Check file extension
    allowed_extensions = [".pdf", ".doc", ".docx", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        extracted_text = ""

        # Extract text based on file type
        if file_ext == ".txt":
            # For text files, just read the content
            with open(temp_file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        elif file_ext == ".pdf":
            # For PDF files, use PyPDF2 or a similar library
            try:
                import PyPDF2
                with open(temp_file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        extracted_text += page.extract_text() + "\n"
            except ImportError:
                # Fallback if PyPDF2 is not installed
                extracted_text = "PDF text extraction is not available. Please install PyPDF2."
        elif file_ext in [".doc", ".docx"]:
            # For Word documents, use python-docx or a similar library
            try:
                import docx
                doc = docx.Document(temp_file_path)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            except ImportError:
                # Fallback if python-docx is not installed
                extracted_text = "Word document text extraction is not available. Please install python-docx."

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # If text extraction failed or returned empty, provide a message
        if not extracted_text.strip():
            extracted_text = "Could not extract text from the uploaded file. Please try uploading a different file or paste the question text directly."

        return {"extracted_text": extracted_text}

    except Exception as e:
        # Clean up the temporary file in case of error
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


class BoilerplateRequest(BaseModel):
    exercise_id: int
    language: Optional[str] = 'python'


class BoilerplateResponse(BaseModel):
    boilerplate_code: str
    function_signature: str
    parameters: List[str]
    return_type: str


@router.post("/{exercise_id}/generate-boilerplate", response_model=BoilerplateResponse)
def generate_boilerplate(request: BoilerplateRequest, db: Session = Depends(get_db)):
    """Generate boilerplate code based on the question and selected language."""

    ex = db.query(CodeExercise).filter(CodeExercise.id == request.exercise_id).first()
    # Prepare prompt for the AI model
    prompt = f"""You are an expert programming instructor. Generate appropriate boilerplate code for the following programming question.

    Question:
    {ex.description}

    Language: {request.language}

    Generate:
    1. A function signature with appropriate parameters
    2. Basic function structure
    3. Return type
    4. Any necessary imports or class definitions

    Format your response exactly as follows:
    FUNCTION_SIGNATURE: [the complete function signature]
    PARAMETERS: [list of parameters]
    RETURN_TYPE: [the return type]
    BOILERPLATE_CODE: [the complete boilerplate code]

    Make the boilerplate code clean and follow best practices for {request.language}.
    """

    # Generate boilerplate using the AI model
    response = llm.invoke(prompt)

    # Parse the response
    function_signature = ""
    parameters = []
    return_type = ""
    boilerplate_code = ""

    try:
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('FUNCTION_SIGNATURE:'):
                function_signature = line[18:].strip()
            elif line.startswith('PARAMETERS:'):
                params_str = line[11:].strip()
                parameters = [p.strip() for p in params_str.split(',')]
            elif line.startswith('RETURN_TYPE:'):
                return_type = line[12:].strip()
            elif line.startswith('BOILERPLATE_CODE:'):
                boilerplate_code = line[17:].strip()
    except Exception as e:
        # If parsing fails, generate a simple boilerplate
        if request.language.lower() == 'python':
            boilerplate_code = "def solution():\n    pass"
            function_signature = "def solution()"
            parameters = []
            return_type = "None"
        elif request.language.lower() == 'javascript':
            boilerplate_code = "function solution() {\n    // Your code here\n}"
            function_signature = "function solution()"
            parameters = []
            return_type = "undefined"
        else:
            boilerplate_code = "public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}"
            function_signature = "public static void main"
            parameters = ["String[] args"]
            return_type = "void"
    ex.boilerplate_code = function_signature

    return BoilerplateResponse(
        boilerplate_code=boilerplate_code,
        function_signature=function_signature,
        parameters=parameters,
        return_type=return_type
    )


class SearchRequest(BaseModel):
    exercise_id: int
    query: Optional[str] = None
    context: Optional[str] = None


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    source: str
    # date: str
    # author: str
    # category: str
    # reading_time: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


@router.post("/{exercise_id}/search-google", response_model=SearchResponse)
async def search_content(exercise_id: int, request: SearchRequest, db: Session = Depends(get_db)):
    """Search for relevant content using Google Custom Search API with caching."""
    try:
        # Check if we have cached results that are less than 24 hours old
        cached_results = db.query(CodeSearchResult).filter(
            CodeSearchResult.code_exercise_id == exercise_id

        ).order_by(CodeSearchResult.created_at.desc()).limit(5).all()

        if cached_results:
            # Update last_accessed timestamp
            for result in cached_results:
                result.last_accessed = datetime.datetime.utcnow()
            db.commit()

            # Convert database results to response model
            results = [
                SearchResult(
                    title=result.title,
                    link=result.link,
                    snippet=result.snippet,
                    source=result.source,
                    # date=result.date
                )
                for result in cached_results
            ]
            return SearchResponse(results=results)

        # If no cached results, perform the search
        api_key = "AIzaSyDqbnNUzjNkeuB9ZDK6q3s8eTUCBx0Vz7I"
        search_engine_id = "92d79bedffa8f4270"

        # Prepare the search query
        query = None
        if request.query:
            query = request.query
        if request.context:
            query = f"{query} {request.context}"
        if not query:
            code_exercise = db.query(CodeExercise).filter(CodeExercise.id == exercise_id).one_or_none()
            query = code_exercise.description
        results = []

        # Make request to Google Custom Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5,  # Number of results to return
            # "sort": "relevance",  # Sort by relevance
            # "gl": "us",  # Region bias
            # "lr": "lang_en"  # Language bias
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Process and format the results

        for item in data.get("items", []):
            result = SearchResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("displayLink", ""),
                # date=item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", "N/A")
            )
            results.append(result)

            # Cache the result in the database
            db_result = CodeSearchResult(
                code_exercise_id=exercise_id,
                query=request.query,
                context=request.context,
                title=result.title,
                link=result.link,
                snippet=result.snippet,
                source=result.source,
                # date=result.date
            )
            db.add(db_result)


        db.commit()
        return SearchResponse(results=results)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/run-tests", response_model=dict)
def run_tests(data: dict, db: Session = Depends(get_db)):
    """Run multiple test cases against the provided code."""
    try:
        code = data.get("code")
        language = data.get("language", "python")
        test_cases = data.get("test_cases", [])
        
        if not code or not test_cases:
            raise HTTPException(status_code=400, detail="Code and test cases are required")
        
        # Filter out invalid test cases with placeholder input
        filtered_test_cases = []
        for tc in test_cases:
            input_data = str(tc.get('input_data', ''))
            if (not '[exact' in input_data and 
                not '{exact' in input_data and
                input_data.strip() != '' and
                not input_data.lower() == 'sample input'):
                filtered_test_cases.append(tc)
        
        # Use filtered test cases
        test_cases = filtered_test_cases
        
        results = []
        
        for test_case in test_cases:
            start_time = time.time()
            
            # Create execution prompt for the LLM
            execution_prompt = f"""You are a code execution engine. Execute the following {language} code with the given input and provide the output.

            CODE:
            ```{language}
            {code}
            ```

            INPUT:
            {test_case['input_data']}

            Execute the code with this input and provide:
            1. The exact output (no additional text, just the output)
            2. Any errors encountered (if any)
            3. Execution success (true/false)

            Format your response exactly as follows:
            OUTPUT: [the exact output]
            ERROR: [error message or "None" if no error]
            SUCCESS: [true/false]
            """
            
            # Execute using LLM
            execution_result = llm.invoke(execution_prompt)
            
            # Parse LLM response
            output = ""
            error = None
            success = False
            
            for line in execution_result.split('\n'):
                line = line.strip()
                if line.startswith('OUTPUT:'):
                    output = line[7:].strip()
                elif line.startswith('ERROR:'):
                    error_msg = line[6:].strip()
                    error = None if error_msg == "None" else error_msg
                elif line.startswith('SUCCESS:'):
                    success = line[8:].strip().lower() == 'true'
            
            # Calculate execution time
            exec_time = int((time.time() - start_time) * 1000)
            
            # Compare output with expected
            passed = success and output.strip() == test_case['expected_output'].strip()
            
            results.append({
                "actual_output": output if success else error,
                "passed": passed,
                "error": error if not success else None,
                "execution_time": exec_time
            })
        
        return {"results": results}
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
