"""Product repository for database operations."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from models.product import ProductModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.product_schema import ProductSchema


class ProductRepository(BaseRepositoryImpl):
    """Repository for Product entity database operations."""

    def __init__(self, db: Session):
        super().__init__(ProductModel, ProductSchema, db)

    def find_all_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[ProductModel], int]:
        """
        Find products with optional search and category filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term (searches in name and description)
            category_id: Optional category ID to filter by
            is_active: Optional boolean to filter by active status

        Returns:
            Tuple of (products list, total count)
        """
        # Build WHERE clause conditions
        conditions = []

        # Add search condition (case-insensitive)
        if search:
            search_term = f"%{search.lower()}%"
            conditions.append(
                (ProductModel.name.ilike(search_term)) |
                (ProductModel.description.ilike(search_term))
            )

        # Add category filter
        if category_id:
            conditions.append(ProductModel.category_id == category_id)
            
        # Add active filter
        if is_active is not None:
            conditions.append(ProductModel.is_active == is_active)

        # Build query
        if conditions:
            stmt = select(ProductModel).where(and_(*conditions))
        else:
            stmt = select(ProductModel)

        # Get total count BEFORE applying pagination
        count_stmt = select(ProductModel).where(and_(*conditions)) if conditions else select(ProductModel)
        total = len(self.session.scalars(count_stmt).all())

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        # Execute and return results
        products = self.session.scalars(stmt).all()
        return products, total