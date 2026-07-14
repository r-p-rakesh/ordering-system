from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from database import get_db
from app.auth.models import User, RoleEnum
from app.auth.utils import get_current_user
from app.menu.models import MenuItemVariant
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

COMMISSION_RATE = Decimal("0.05")  # 5%

@router.post("/", response_model=OrderResponse)
def place_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != RoleEnum.customer:
        raise HTTPException(status_code=403, detail="Only customers can place orders")

    total_amount = Decimal("0.00")
    order_items_to_create = []

    for item in order_data.items:
        variant = db.query(MenuItemVariant).filter(MenuItemVariant.id == item.variant_id).first()
        if not variant or variant.menu_item_id != item.menu_item_id:
            raise HTTPException(status_code=404, detail=f"Invalid item/variant: {item.menu_item_id}")

        line_total = variant.price * item.quantity
        total_amount += line_total

        order_items_to_create.append({
            "menu_item_id": item.menu_item_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "price_at_order_time": variant.price,
        })

    commission_amount = (total_amount * COMMISSION_RATE).quantize(Decimal("0.01"))

    new_order = Order(
        customer_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        total_amount=total_amount,
        commission_amount=commission_amount,
    )
    db.add(new_order)
    db.flush()

    for item in order_items_to_create:
        db.add(OrderItem(order_id=new_order.id, **item))

    db.commit()
    db.refresh(new_order)
    return new_order