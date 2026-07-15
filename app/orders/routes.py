from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from database import get_db
from app.auth.models import User, RoleEnum
from app.auth.utils import get_current_user
from app.menu.models import MenuItemVariant
from app.orders.models import Order, OrderItem,OrderStatusEnum
from app.orders.schemas import OrderCreate, OrderResponse
from app.orders.schemas import OrderStatusUpdate  
from fastapi import WebSocket, WebSocketDisconnect
from app.orders.websocket import manager
from jose import jwt, JWTError
from app.auth.utils import JWT_SECRET_KEY, JWT_ALGORITHM

from sqlalchemy import func
from app.menu.models import MenuItem
from app.orders.schemas import DashboardSummary, BestSeller
from typing import List


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

@router.get("/restaurant/{restaurant_id}", response_model=list[OrderResponse])
def get_restaurant_orders(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.menu.routes import verify_restaurant_owner
    verify_restaurant_owner(restaurant_id, current_user, db)

    return db.query(Order).filter(Order.restaurant_id == restaurant_id).order_by(Order.created_at.desc()).all()

@router.get("/my-orders", response_model=list[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Order).filter(Order.customer_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    from app.menu.routes import verify_restaurant_owner
    verify_restaurant_owner(order.restaurant_id, current_user, db)

    order.status = status_update.status
    db.commit()
    db.refresh(order)

    await manager.send_to_user(order.customer_id, {
        "order_id": order.id,
        "status": order.status.value,
    })

    return order


@router.websocket("/ws")
async def order_status_socket(websocket: WebSocket):
    await websocket.accept()

    try:
        token = await websocket.receive_text()  # first message must be the JWT
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
    except (JWTError, Exception):
        await websocket.close(code=1008)
        return

    manager.active_connections[user_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)



@router.get("/dashboard/{restaurant_id}/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.menu.routes import verify_restaurant_owner
    verify_restaurant_owner(restaurant_id, current_user, db)

    orders_query = db.query(Order).filter(Order.restaurant_id == restaurant_id)

    total_orders = orders_query.count()
    total_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.restaurant_id == restaurant_id
    ).scalar()
    total_commission = db.query(func.coalesce(func.sum(Order.commission_amount), 0)).filter(
        Order.restaurant_id == restaurant_id
    ).scalar()
    pending_orders = orders_query.filter(
        Order.status.in_([OrderStatusEnum.placed, OrderStatusEnum.preparing])
    ).count()

    return DashboardSummary(
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_commission_paid=total_commission,
        pending_orders=pending_orders,
    )


@router.get("/dashboard/{restaurant_id}/best-sellers", response_model=List[BestSeller])
def get_best_sellers(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.menu.routes import verify_restaurant_owner
    verify_restaurant_owner(restaurant_id, current_user, db)

    results = (
        db.query(
            MenuItem.id,
            MenuItem.name,
            func.sum(OrderItem.quantity).label("total_quantity_sold"),
        )
        .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.restaurant_id == restaurant_id)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return [
        BestSeller(menu_item_id=r[0], name=r[1], total_quantity_sold=r[2])
        for r in results
    ]