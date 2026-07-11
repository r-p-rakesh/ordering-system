from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.auth.models import User, RoleEnum
from app.auth.utils import get_current_user
from app.restaurants.models import Restaurant
from app.menu.models import MenuItem, MenuItemVariant
from app.menu.schemas import MenuItemCreate, MenuItemResponse

router = APIRouter(prefix="/menu", tags=["Menu"])


def verify_restaurant_owner(restaurant_id: int, current_user: User, db: Session):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this restaurant")
    return restaurant


@router.post("/items", response_model=MenuItemResponse)
def create_menu_item(
    item: MenuItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != RoleEnum.restaurant_owner:
        raise HTTPException(status_code=403, detail="Only restaurant owners can add menu items")

    verify_restaurant_owner(item.restaurant_id, current_user, db)

    new_item = MenuItem(
        restaurant_id=item.restaurant_id,
        name=item.name,
        description=item.description,
        category=item.category,
        image_url=item.image_url,
    )
    db.add(new_item)
    db.flush()  # assigns new_item.id without fully committing yet

    for v in item.variants:
        db.add(MenuItemVariant(menu_item_id=new_item.id, size=v.size, price=v.price))

    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/items/{restaurant_id}", response_model=list[MenuItemResponse])
def get_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()