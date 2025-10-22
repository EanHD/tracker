"""Standard API response formats"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope"""
    success: bool = True
    data: T
    meta: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "meta": {"version": "1.0"}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response envelope"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    errors: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Validation error",
                "detail": "Invalid field value",
                "errors": {"field": "Must be positive"}
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata"""
    success: bool = True
    data: list[T]
    meta: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": 1}, {"id": 2}],
                "meta": {
                    "total": 100,
                    "page": 1,
                    "per_page": 10,
                    "pages": 10
                }
            }
        }


def success_response(data: Any, meta: Optional[dict] = None) -> dict:
    """
    Create a standard success response
    
    Args:
        data: Response data
        meta: Optional metadata
        
    Returns:
        Dictionary with success, data, meta keys
    """
    response = {
        "success": True,
        "data": data
    }
    if meta:
        response["meta"] = meta
    return response


def error_response(
    error: str,
    detail: Optional[str] = None,
    errors: Optional[dict] = None
) -> dict:
    """
    Create a standard error response
    
    Args:
        error: Error message
        detail: Detailed error description
        errors: Field-specific errors
        
    Returns:
        Dictionary with success, error, detail, errors keys
    """
    response = {
        "success": False,
        "error": error
    }
    if detail:
        response["detail"] = detail
    if errors:
        response["errors"] = errors
    return response


def paginated_response(
    data: list,
    total: int,
    page: int = 1,
    per_page: int = 10
) -> dict:
    """
    Create a paginated response
    
    Args:
        data: List of items
        total: Total number of items
        page: Current page number (1-indexed)
        per_page: Items per page
        
    Returns:
        Dictionary with success, data, meta keys
    """
    pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }
