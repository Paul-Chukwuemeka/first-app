from fastapi import APIRouter,status,HTTPException,Depends
from utils.db import get_db
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from models.cart_model import Cart,CartItem
from utils.secure import getUser
from models.userModel import User
from models.product_model import Product

router = APIRouter()

class Product_type(BaseModel):
    id: UUID
    quantity: int
    


@router.get("/cart")
def get_cart(db:Session = Depends(get_db),user = Depends(getUser)):
        found = db.query(Cart).options(joinedload(Cart.items)).filter(Cart.user_id == user.user_id).first()
        if not found:
            raise HTTPException(status_code=404,detail="Cart not found")
        return found
    


@router.post("/cart/add")
def add_to_cart(product: Product_type,db:Session = Depends(get_db),user = Depends(getUser)):
    try:
        found = db.query(Cart).options(joinedload(Cart.items)).filter(Cart.user_id == user.user_id).first()
        productInStore = db.query(Product).filter(Product.product_id == product.id).first()
        if not found:
            raise HTTPException(status_code=404,detail="Cart not found")
        if not productInStore:
            raise HTTPException(status_code=404,detail="product not found")
        
        if productInStore.available_units < product.quantity: 
            raise HTTPException(status_code=400,detail="request exceed units")
        
        for item in found.items:
            if item.item_id == product.id:
                raise HTTPException(status_code= 409,detail="Item already exits in cart")
        
        
        
        new_item = CartItem(
            item_id = product.id,
            quantity = product.quantity,
            cart_id = found.id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return new_item
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=404,detail="Cart not found")
    

@router.delete("/cart/remove/{id}")
def remove_item(id:UUID,db:Session = Depends(get_db),user = Depends(getUser)):
    try:      
        item = db.query(CartItem).options(joinedload(CartItem.cart)).filter(CartItem.id == id).first()
        if not item:
          raise HTTPException(status_code=404,detail="item not found in cart")
        if item.cart.user_id != user.user_id:
          raise HTTPException(status_code=402,detail="This user can not delete this item") 
        db.delete(item)
        db.commit()
        return "item has been deleted"
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=404,detail="Cart not found")


@router.patch("/cart/update")
def update_item_quantity(q:Product_type,db:Session= Depends(get_db),user= Depends(getUser)):
    try:
        item = db.query(CartItem).options(joinedload(CartItem.cart)).filter(CartItem.id == q.id).first()
        if not item:
            raise HTTPException(status_code=404,detail="item not found in cart")
        productInStore = db.query(Product).filter(Product.product_id == item.item_id).first()
        if not productInStore:
            raise HTTPException(status_code=404,detail="product not found")
        if productInStore.available_units < q.quantity: 
            raise HTTPException(status_code=400,detail="request exceed units")
        item.quantity = q.quantity
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=404,detail="Cart not found")
