"""Product service with Redis caching integration and sanitized logging."""
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from models.product import ProductModel
from repositories.product_repository import ProductRepository
from schemas.product_schema import ProductSchema
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)  # P11: Sanitized logging


class ProductService(BaseServiceImpl):
    """Service for Product entity with caching."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=ProductRepository,
            model=ProductModel,
            schema=ProductSchema,
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "products"

    def get_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None, category_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[ProductSchema]:
        """
        Get all products with optional search and category filters, with caching.

        Cache key pattern:
        - No filters: products:list:skip:{skip}:limit:{limit}
        - With filters: products:list:skip:{skip}:limit:{limit}:search:{search}:category:{category_id}:active:{is_active}

        TTL: 5 minutes (default REDIS_CACHE_TTL)

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)
            search: Optional search term (searches in name and description)
            category_id: Optional category ID to filter by
            is_active: Optional boolean to filter active products

        Returns:
            List of ProductSchema objects
        """
        # Build cache key with all filters
        cache_key = self.cache.build_key(
            self.cache_prefix,
            "list",
            skip=skip,
            limit=limit,
            search=search or "",
            category=category_id or "",
            active=str(is_active) if is_active is not None else ""
        )

        # Try to get from cache
        cached_products = self.cache.get(cache_key)
        if cached_products is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return [ProductSchema(**p) for p in cached_products]

        # Cache miss - get from database with filters
        logger.debug(f"Cache MISS: {cache_key}")
        products, total = self._repository.find_all_with_filters(
            skip=skip,
            limit=limit,
            search=search,
            category_id=category_id,
            is_active=is_active
        )

        # Convert models to schemas using Pydantic from_attributes
        product_schemas = [
            ProductSchema.model_validate(p, from_attributes=True)
            for p in products
        ]

        # Cache the result (convert to dict for JSON serialization)
        products_dict = [p.model_dump() for p in product_schemas]
        self.cache.set(cache_key, products_dict)

        return product_schemas

    def get_one(self, id_key: int) -> ProductSchema:
        """
        Get single product by ID with caching

        Cache key pattern: products:id:{id_key}
        TTL: 5 minutes
        """
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        # Try cache first
        cached_product = self.cache.get(cache_key)
        if cached_product is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return ProductSchema(**cached_product)

        # Get from database
        logger.debug(f"Cache MISS: {cache_key}")
        product = super().get_one(id_key)

        # Cache the result
        self.cache.set(cache_key, product.model_dump())

        return product

    def save(self, schema: ProductSchema) -> ProductSchema:
        """
        Create new product and invalidate list cache
        """
        product = super().save(schema)

        # Invalidate list cache (all paginated lists)
        self._invalidate_list_cache()

        return product

    def update(self, id_key: int, schema: ProductSchema) -> ProductSchema:
        """
        Update product with transactional cache invalidation

        Args:
            id_key: Product ID to update
            schema: Validated ProductSchema with new data

        Returns:
            Updated product schema

        Raises:
            InstanceNotFoundError: If product doesn't exist
            ValueError: If validation fails
        """
        # Build cache keys BEFORE update (prepare for invalidation)
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        try:
            # Update in database (atomic transaction)
            product = super().update(id_key, schema)

            # Only invalidate cache AFTER successful DB commit
            self.cache.delete(cache_key)
            self._invalidate_list_cache()

            logger.info(f"Product {id_key} updated and cache invalidated successfully")
            return product

        except Exception as e:
            # If update fails, cache remains consistent (no invalidation)
            logger.error(f"Failed to update product {id_key}: {e}")
            raise

    def delete(self, id_key: int) -> None:
        """
        Delete product with validation to prevent loss of sales history

        Raises:
            ValueError: If product has associated order details (sales history)
            InstanceNotFoundError: If product doesn't exist
        """
        from models.order_detail import OrderDetailModel
        from sqlalchemy import select

        # Check if product has sales history
        stmt = select(OrderDetailModel).where(
            OrderDetailModel.product_id == id_key
        ).limit(1)

        # Get session from repository
        has_sales = self._repository.session.scalars(stmt).first()

        if has_sales:
            logger.error(
                f"Cannot delete product {id_key}: has associated sales history"
            )
            raise ValueError(
                f"Cannot delete product {id_key}: product has associated sales history. "
                f"Consider marking as inactive instead of deleting."
            )

        # Safe to delete
        logger.info(f"Deleting product {id_key} (no sales history)")
        super().delete(id_key)

        # Invalidate specific product cache
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)
        self.cache.delete(cache_key)

        # Invalidate list cache
        self._invalidate_list_cache()

    def _invalidate_list_cache(self):
        """Invalidate all product list caches"""
        pattern = f"{self.cache_prefix}:list:*"
        deleted_count = self.cache.delete_pattern(pattern)
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} product list cache entries")
