# app/services/knowledge/knowledge_route.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.utils.knowledge import ProductKnowledge, knowledge_manager

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Management"])

@router.post("/products")
async def add_product(product: ProductKnowledge):
    """Add a new product to the knowledge base"""
    try:
        result = knowledge_manager.add_product(product)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/search")
async def search_products(query: str, limit: int = 5):
    """Search for products in the knowledge base"""
    try:
        products = knowledge_manager.search_products(query, n_results=limit)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
async def get_all_products(limit: int = 100):
    """Get all products from the knowledge base"""
    try:
        products = knowledge_manager.get_all_products(limit=limit)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductKnowledge):
    """Update an existing product"""
    try:
        result = knowledge_manager.update_product(product_id, product)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product from the knowledge base"""
    try:
        result = knowledge_manager.delete_product(product_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))