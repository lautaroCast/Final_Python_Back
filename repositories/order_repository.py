"""Order repository for database operations."""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.order import OrderModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.order_schema import OrderSchema


class OrderRepository(BaseRepositoryImpl):
    """Repository for Order entity database operations."""

    def __init__(self, db: Session):
        super().__init__(OrderModel, OrderSchema, db)

    def find_by_client(self, client_id: int, skip: int = 0, limit: int = 100) -> List[OrderSchema]:
        """Find orders by client ID with pagination."""
        try:
            stmt = select(self.model).where(self.model.client_id == client_id).offset(skip).limit(limit)
            models = self.session.scalars(stmt).all()
            return [self.schema.model_validate(model) for model in models]
        except Exception as e:
            self.logger.error(f"Error finding orders for client {client_id}: {e}")
            raise