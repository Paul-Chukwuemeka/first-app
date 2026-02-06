from fastapi import APIRouter,status,HTTPException,Depends
from utils.db import get_db
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from models.product_model import Product
from utils.secure import verify_roles
from models.userModel import roles, User
from decimal import Decimal

router = APIRouter()

class newProduct(BaseModel):
    name: str
    price : Decimal 
    description : Optional[str] = None
    

class UserOut(BaseModel):
    user_id: UUID
    username: str
    
    class Config:
        orm_mode = True
        
        
class ProductOut(BaseModel):
    product_id : UUID
    name : str
    price : Decimal
    description : Optional[str] = None
    vendor: UserOut
    
    class Config:
        orm_mode = True
        

# add new product
@router.post("/products/add",response_model=ProductOut)
def add_products(product: newProduct ,db:Session = Depends(get_db),user = Depends(verify_roles(roles.vendor))):
    try:
        new = Product(
            name=product.name,
            price = product.price,
            description = product.description,
            vendor_id = user.user_id
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        
        return new
        
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=400,detail=err)

# get all products


@router.get("/products",response_model=list[ProductOut])
def get_all_products(db:Session = Depends(get_db)):
    try: 
        all = db.query(Product).options(joinedload(Product.vendor)).all()
        return all
        
    except IntegrityError as err:
        raise HTTPException(status_code=400,detail=err)


 
# get products of logged in vendor
    
@router.get("/products/mine", response_model=list[ProductOut])
def get_vendor_products(db:Session = Depends(get_db), user = Depends(verify_roles(roles.vendor))):
    try:
        products = db.query(Product).options(joinedload(Product.vendor)).filter(Product.vendor_id == user.user_id).all()
        if not products:
            raise HTTPException(status_code=400,detail="No products")
        return products
    except IntegrityError as err:
        raise HTTPException(status_code=400,detail=err)
    
    
    
    
# get products by vendor id
@router.get("/products/vendor/{id}", response_model= list[ProductOut])
def get_vendor_products_by_id(id: UUID,db:Session = Depends(get_db)):
    try: 
        vendor =  db.query(User).filter(User.user_id == id).first()
        if not vendor:
            raise HTTPException(status_code=404,detail="Vendor does no exist")    
        found = db.query(Product).options(joinedload(Product.vendor)).filter(Product.vendor_id == id).all()
        if not found:
            raise HTTPException(status_code=404,detail="no product by this vendor")    
        return found
        
    except IntegrityError as err:
        raise HTTPException(status_code=400,detail=err)


# get products by id
@router.get("/products/{id}", response_model= ProductOut)
def get_products_by_id(id: UUID,db:Session = Depends(get_db)):
    try: 
        found = db.query(Product).options(joinedload(Product.vendor)).filter(Product.product_id == id).first()
        if not found:
            raise HTTPException(status_code=404,detail="Product not found")    
        return found
        
    except IntegrityError as err:
        raise HTTPException(status_code=400,detail=err)
 
