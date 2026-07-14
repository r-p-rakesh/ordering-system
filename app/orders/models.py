from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatusEnum(str, enum.Enum):
    placed = "placed"
    preparing = "preparing"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.placed)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    commission_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("menu_item_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_order_time = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")