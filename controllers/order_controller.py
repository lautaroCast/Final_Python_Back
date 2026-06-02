"""Order controller with proper dependency injection."""
from typing import List
from fastapi import Depends, status
from sqlalchemy.orm import Session

from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_schema import OrderSchema
from services.order_service import OrderService
from config.database import get_db


class OrderController(BaseControllerImpl):
    """Controller for Order entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=OrderSchema,
            service_factory=lambda db: OrderService(db),
            tags=["Orders"]
        )

        @self.router.get("/client/{client_id}", response_model=List[OrderSchema], status_code=status.HTTP_200_OK)
        async def get_by_client(
            client_id: int,
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ):
            """Get all orders for a specific client."""
            service = OrderService(db)
            return service.get_by_client(client_id, skip=skip, limit=limit)