from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from app.orders.models import OrderStatusEnum


class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

class OrderItemCreate(BaseModel):
    menu_item_id: int
    variant_id: int
    quantity: int
    addon_ids: Optional[List[int]] = []

class OrderCreate(BaseModel):
    restaurant_id: int
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    variant_id: int
    quantity: int
    price_at_order_time: Decimal

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    restaurant_id: int
    status: str
    total_amount: Decimal
    commission_amount: Decimal
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True



class DashboardSummary(BaseModel):
    total_orders: int
    total_revenue: Decimal
    total_commission_paid: Decimal
    pending_orders: int

class BestSeller(BaseModel):
    menu_item_id: int
    name: str
    total_quantity_sold: int

class RestaurantPerformance(BaseModel):
    restaurant_id: int
    restaurant_name: str
    total_orders: int
    total_revenue: Decimal
    total_commission: Decimal

class AdminDashboardSummary(BaseModel):
    total_orders_platform_wide: int
    total_commission_earned: Decimal
    total_restaurants: int
    restaurant_breakdown: List[RestaurantPerformance]