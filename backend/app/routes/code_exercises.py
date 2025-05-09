from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.services.code_generation import code_generation_service
from app.schemas.code_generation import CodeGenerationResponse, TestCase
from app.models.code_exercises import CodeExercise, TestCase as DBTestCase, CodeSearchResult
from app.database import get_db
from sqlalchemy.sql import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import logger
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/generate-template")
async def generate_code_template(data: dict):
    """Generate a code template including function signature and initial test cases."""
    try:
        response = await code_generation_service.generate_code_template(data["question"])
        
        # Format the response for the frontend
        return {
            "function_signature": response.function_signature.full_signature,
            "parameters": response.function_signature.parameters,
            "return_type": response.function_signature.return_type,
            "test_cases": [
                {
                    "input_data": tc.input_data,
                    "expected_output": tc.expected_output,
                    "explanation": tc.explanation
                }
                for tc in response.sample_test_cases
            ],
            "implementation_hints": response.implementation_hints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-cases/next")
async def generate_next_test_case(data: dict):
    """Generate the next test case based on current code and existing cases."""
    try:
        new_test_case = await code_generation_service.generate_additional_test_case(
            question=data["question"],
            existing_cases=data.get("existing_cases", []),
            current_code=data.get("current_code", "")
        )
        
        return {
            "test_case": {
                "input_data": new_test_case.input_data,
                "expected_output": new_test_case.expected_output,
                "explanation": new_test_case.explanation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-test")
async def run_test(data: dict):
    """Run a specific test case against the provided code."""
    try:
        test_case = TestCase(
            input_data=data["test_case"]["input_data"],
            expected_output=data["test_case"]["expected_output"],
            explanation=data["test_case"].get("explanation", "")
        )
        
        result = await code_generation_service.execute_test_case(
            code=data["code"],
            test_case=test_case
        )
        
        return {
            "passed": result.passed,
            "actual_output": result.actual_output,
            "error_message": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_code(data: dict):
    """Analyze code for errors, optimizations, and best practices."""
    try:
        analysis = await code_generation_service.analyze_code(
            code=data["code"],
            problem=data["question"]
        )
        
        return {
            "logical_errors": analysis.logical_errors,
            "optimization_suggestions": analysis.optimization_suggestions,
            "security_concerns": analysis.security_concerns,
            "best_practices": analysis.best_practices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-error")
async def explain_error(data: dict):
    """Get a detailed explanation of an error."""
    try:
        explanation = await code_generation_service.get_error_explanation(
            error=data["error"],
            code=data["code"]
        )
        
        return {
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{exercise_id}/test-cases", response_model=List[TestCaseSchema])
async def get_test_cases(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all test cases for a specific code exercise.
    
    Args:
        exercise_id (int): The ID of the code exercise
        db (AsyncSession): Database session
        
    Returns:
        List[TestCaseSchema]: List of test cases for the exercise
    """
    try:
        # First check if the exercise exists
        exercise_query = select(CodeExercise).where(CodeExercise.id == exercise_id)
        exercise = await db.execute(exercise_query)
        exercise = exercise.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail=f"Exercise with id {exercise_id} not found")

        # Query to get all test cases for the exercise
        query = select(TestCase).where(TestCase.code_exercise_id == exercise_id)
        result = await db.execute(query)
        test_cases = result.scalars().all()
        
        return test_cases or []
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching test cases for exercise {exercise_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching test cases: {str(e)}"
        )

@router.get("/{exercise_id}/test-cases/{test_case_index}", response_model=TestCaseSchema)
async def get_single_test_case(
    exercise_id: int,
    test_case_index: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single test case for a specific code exercise.
    
    Args:
        exercise_id (int): The ID of the code exercise
        test_case_index (int): The index of the test case to fetch
        db (AsyncSession): Database session
        
    Returns:
        TestCaseSchema: The requested test case
    """
    try:
        # Query to get all test cases for the exercise
        query = select(TestCase).where(TestCase.code_exercise_id == exercise_id)
        result = await db.execute(query)
        test_cases = result.scalars().all()
        
        if not test_cases:
            raise HTTPException(status_code=404, detail="No test cases found for this exercise")
            
        if test_case_index >= len(test_cases):
            raise HTTPException(status_code=404, detail="No more test cases available")
            
        return test_cases[test_case_index]
        
    except Exception as e:
        logger.error(f"Error fetching test case {test_case_index} for exercise {exercise_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching test case: {str(e)}"
        )

@router.post("/run-single-test")
async def run_single_test(data: dict):
    """Run a single test case against the provided code."""
    try:
        test_case = TestCase(
            input_data=data["test_case"]["input_data"],
            expected_output=data["test_case"]["expected_output"],
            explanation=data["test_case"].get("explanation", "")
        )
        
        result = await code_generation_service.execute_test_case(
            code=data["code"],
            test_case=test_case
        )
        
        return {
            "passed": result.passed,
            "actual_output": result.actual_output,
            "error_message": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_content(data: dict, db: AsyncSession = Depends(get_db)):
    """Search for relevant content for a code exercise and store results."""
    try:
        exercise_id = data["code_exercise_id"]
        query = data.get("query", "")

        # First check if we have recent cached results
        cached_results_query = select(CodeSearchResult).where(
            and_(
                CodeSearchResult.code_exercise_id == exercise_id,
                CodeSearchResult.query == query,
                # Only use cache if less than 24 hours old
                CodeSearchResult.created_at >= func.now() - timedelta(hours=24)
            )
        ).order_by(CodeSearchResult.created_at.desc())

        cached_results = await db.execute(cached_results_query)
        cached_results = cached_results.scalars().all()

        if cached_results:
            # Update last_accessed timestamp
            for result in cached_results:
                result.last_accessed = func.now()
            await db.commit()
            
            return {
                "results": [
                    {
                        "title": result.title,
                        "link": result.link,
                        "snippet": result.snippet,
                        "source": result.source,
                        "date": result.date
                    }
                    for result in cached_results
                ]
            }

        # If no cached results, perform new search
        # Get the exercise to include its description in the search
        exercise_query = select(CodeExercise).where(CodeExercise.id == exercise_id)
        exercise = await db.execute(exercise_query)
        exercise = exercise.scalar_one_or_none()

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Perform the search using the code generation service
        search_results = await code_generation_service.search_google(
            query=f"{exercise.description} {query}".strip(),
            num_results=5
        )

        # Store the results in the database
        for result in search_results:
            db_result = CodeSearchResult(
                code_exercise_id=exercise_id,
                query=query,
                title=result["title"],
                link=result["link"],
                snippet=result["snippet"],
                source=result.get("source", ""),
                date=result.get("date", ""),
                context=exercise.description
            )
            db.add(db_result)

        await db.commit()

        return {"results": search_results}

    except Exception as e:
        logger.error(f"Error performing content search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )

@router.get("/{exercise_id}/search-results")
async def get_recent_search_results(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the 5 most recent search results for a code exercise."""
    try:
        # Query to get the most recent search results
        query = select(CodeSearchResult).where(
            CodeSearchResult.code_exercise_id == exercise_id
        ).order_by(
            CodeSearchResult.created_at.desc()
        ).limit(5)
        
        result = await db.execute(query)
        search_results = result.scalars().all()
        
        return {
            "results": [
                {
                    "title": result.title,
                    "link": result.link,
                    "snippet": result.snippet,
                    "source": result.source,
                    "date": result.date,
                    "created_at": result.created_at.isoformat()
                }
                for result in search_results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching search results for exercise {exercise_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching search results: {str(e)}"
        ) 