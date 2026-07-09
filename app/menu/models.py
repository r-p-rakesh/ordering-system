from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class SizeEnum(str, enum.Enum):
    regular="regular"
    medium = "midium"
    large = "large"

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    image_url = Column(String(255))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    variants = relationship("MenuItemVariant", back_populates="menu_item", cascade="all, delete-orphan")
    addon_links = relationship("MenuItemAddon", back_populates="menu_item", cascade="all, delete-orphan")
class AddOn(Base):
    __tablename__ = "add_ons"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

class MenuItemVariant(Base):
    __tablename__= "menu_item_variants"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id =  Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    size = Column(Enum(SizeEnum), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    menu_item = relationship("MenuItem", back_populates="variants")

class MenuItemAddon(Base):
    __tablename__ = "menu_item_addons"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    addon_id = Column(Integer, ForeignKey("add_ons.id"), nullable=False)

    menu_item = relationship("MenuItem", back_populates="addon_links")
    addon = relationship("AddOn")    