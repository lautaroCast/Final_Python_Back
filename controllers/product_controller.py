"""Product controller with proper dependency injection."""
from typing import List, Optional
from fastapi import status, Depends
from sqlalchemy.orm import Session

from controllers.base_controller import BaseController
from config.database import get_db
from schemas.product_schema import ProductSchema
from services.product_service import ProductService
from fastapi import APIRouter


class ProductController(BaseController):
    """Controller for Product entity with CRUD operations and advanced search."""

    def __init__(self):
        self.schema = ProductSchema
        self.service_factory = lambda db: ProductService(db)
        self.router = APIRouter(tags=["Products"])
        self._register_routes()

    def _register_routes(self):
        """Register all product routes including search/filter."""
        
        @self.router.get("/filters", status_code=status.HTTP_200_OK)
        async def get_filters():
            """Get all available product categories/filters."""
            return ["electronics", "home", "fashion", "sports", "books", "other"]

        @self.router.get("/", response_model=List[self.schema], status_code=status.HTTP_200_OK)
        async def get_all_with_filters(
            skip: int = 0,
            limit: int = 100,
            search: Optional[str] = None,
            category: Optional[str] = None,
            is_active: Optional[bool] = None,
            db: Session = Depends(get_db)
        ):
            """
            Get all products with optional search and category filters.

            Query Parameters:
            - skip: Number of records to skip (pagination, default: 0)
            - limit: Maximum number of records to return (default: 100)
            - search: Optional search term (searches in product name and description)
            - category: Optional category name to filter by
            - is_active: Optional boolean to filter by active status (true/false)
            """
            service = ProductService(db)
            
            # Resolve category name to category_id if provided
            category_id = None
            if category and category != "all":
                # Import here to avoid circular imports
                from repositories.category_repository import CategoryRepository
                try:
                    category_repo = CategoryRepository(db)
                    all_categories = category_repo.find_all(skip=0, limit=1000)
                    
                    # Find category by name (case-insensitive)
                    for cat in all_categories:
                        if hasattr(cat, 'name') and cat.name and cat.name.lower() == category.lower():
                            category_id = cat.id_key
                            break
                except Exception:
                    # If category lookup fails, ignore and continue without category filter
                    pass
            
            return service.get_all(
                skip=skip,
                limit=limit,
                search=search,
                category_id=category_id,
                is_active=is_active
            )

        @self.router.get("/{id_key}", response_model=self.schema, status_code=status.HTTP_200_OK)
        async def get_one(
            id_key: int,
            db: Session = Depends(get_db)
        ):
            """Get a single product by ID."""
            service = self.service_factory(db)
            return service.get_one(id_key)

        @self.router.post("/", response_model=self.schema, status_code=status.HTTP_201_CREATED)
        async def create(
            schema_in: self.schema,
            db: Session = Depends(get_db)
        ):
            """Create a new product."""
            service = self.service_factory(db)
            return service.save(schema_in)

        @self.router.put("/{id_key}", response_model=self.schema, status_code=status.HTTP_200_OK)
        async def update(
            id_key: int,
            schema_in: self.schema,
            db: Session = Depends(get_db)
        ):
            """Update an existing product."""
            service = self.service_factory(db)
            return service.update(id_key, schema_in)

        @self.router.delete("/{id_key}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete(
            id_key: int,
            db: Session = Depends(get_db)
        ):
            """Delete a product."""
            service = self.service_factory(db)
            from fastapi import HTTPException
            try:
                service.delete(id_key)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
            return None
