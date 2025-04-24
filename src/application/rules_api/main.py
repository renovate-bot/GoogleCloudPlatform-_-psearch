# 
# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List
from google.cloud import firestore
import logging
from config import config
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title="PSearch Rules API",
    description="""
    API for managing search boost and bury rules in PSearch.
    
    This API allows you to:
    * Create boost/bury rules for products
    * Retrieve existing rules
    * Update rule configurations
    * Delete rules
    
    Rules can be based on:
    * Product categories
    * Brands
    * Price ranges
    * Specific product IDs
    """,
    version="1.0.0",
    contact={
        "name": "PSearch Team",
        "url": "https://github.com/yourusername/psearch",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firestore client
try:
    db = firestore.Client(
        project=config.PROJECT_ID,
        database=config.FIRESTORE_DATABASE
    )
    logger.info(f"Successfully initialized Firestore client for project: {config.PROJECT_ID}")
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {str(e)}")
    raise

class RuleType(str, Enum):
    BOOST = "boost"
    BURY = "bury"

class ConditionType(str, Enum):
    CATEGORY = "category"
    BRAND = "brand"
    PRICE_RANGE = "price_range"
    PRODUCT_ID = "product_id"

class Rule(BaseModel):
    """
    Represents a search rule for boosting or burying products in search results.
    """
    type: RuleType = Field(
        description="Type of rule - either boost to increase visibility or bury to decrease visibility"
    )
    conditionType: ConditionType = Field(
        description="Type of condition to apply the rule"
    )
    condition: str = Field(
        description="""
        The condition value to match against. Format depends on conditionType:
        * For category: Category name (e.g., "Electronics")
        * For brand: Brand name (e.g., "Apple")
        * For price_range: Min-max format (e.g., "0-100")
        * For product_id: Product ID (e.g., "prod_123")
        """
    )
    score: float = Field(
        gt=0,
        description="Score to apply when rule matches. Must be greater than 0. Higher values for boost, lower values for bury."
    )

    @field_validator('condition')
    def validate_condition(cls, v: str, info):
        if not v.strip():
            raise ValueError('Condition cannot be empty')
        
        # Get the condition type from the values
        condition_type = info.data.get('conditionType')
        if condition_type == ConditionType.PRICE_RANGE:
            try:
                min_price, max_price = map(float, v.split('-'))
                if min_price >= max_price:
                    raise ValueError()
            except:
                raise ValueError('Price range must be in format min-max (e.g., 0-100)')
        
        return v.strip()

class RuleInDB(Rule):
    """
    Represents a rule as stored in the database, including its ID.
    """
    id: str = Field(description="Unique identifier for the rule")

class RuleResponse(BaseModel):
    """
    Response model for rule operations.
    """
    message: str = Field(description="Operation result message")
    rule: Optional[RuleInDB] = Field(description="The affected rule, if applicable")

class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    """
    status: str = Field(description="Health status of the service")
    project_id: str = Field(description="GCP project ID")
    database: str = Field(description="Firestore database name")
    collection: str = Field(description="Firestore collection name")

@app.get(
    "/api/rules",
    response_model=List[RuleInDB],
    tags=["Rules"],
    summary="Get all rules",
    description="Retrieves all boost and bury rules from the database."
)
async def get_rules():
    try:
        collection = db.collection(config.FIRESTORE_COLLECTION)
        logger.info(f"Fetching rules from collection: {config.FIRESTORE_COLLECTION}")
        docs = collection.stream()
        rules = []
        
        for doc in docs:
            rule_data = doc.to_dict()
            rule_data['id'] = doc.id
            rules.append(rule_data)
        
        logger.info(f"Successfully fetched {len(rules)} rules")
        return rules
    except Exception as e:
        logger.error(f"Error fetching rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/api/rules",
    response_model=RuleInDB,
    tags=["Rules"],
    summary="Create a new rule",
    description="""
    Creates a new boost or bury rule.
    
    The rule can be based on:
    * Product category
    * Brand
    * Price range (format: min-max, e.g., "0-100")
    * Specific product ID
    
    The score determines the impact:
    * For boost rules: higher scores increase visibility
    * For bury rules: higher scores decrease visibility
    """
)
async def create_rule(rule: Rule):
    try:
        logger.info(f"Creating new rule: {rule.dict()}")
        collection = db.collection(config.FIRESTORE_COLLECTION)
        doc_ref = collection.document()
        rule_dict = rule.model_dump()
        doc_ref.set(rule_dict)
        
        response = {
            "id": doc_ref.id,
            **rule_dict
        }
        logger.info(f"Successfully created rule with ID: {doc_ref.id}")
        return response
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put(
    "/api/rules/{rule_id}",
    response_model=RuleInDB,
    tags=["Rules"],
    summary="Update an existing rule",
    description="Updates an existing rule by its ID. All fields must be provided."
)
async def update_rule(
    rule_id: str,
    rule: Rule = Body(...)
):
    try:
        logger.info(f"Updating rule {rule_id} with data: {rule.dict()}")
        doc_ref = db.collection(config.FIRESTORE_COLLECTION).document(rule_id)
        if not doc_ref.get().exists:
            logger.warning(f"Rule {rule_id} not found")
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule_dict = rule.model_dump()
        doc_ref.update(rule_dict)
        response = {
            "id": rule_id,
            **rule_dict
        }
        logger.info(f"Successfully updated rule {rule_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(
    "/api/rules/{rule_id}",
    response_model=RuleResponse,
    tags=["Rules"],
    summary="Delete a rule",
    description="Deletes an existing rule by its ID."
)
async def delete_rule(rule_id: str):
    try:
        logger.info(f"Deleting rule {rule_id}")
        doc_ref = db.collection(config.FIRESTORE_COLLECTION).document(rule_id)
        if not doc_ref.get().exists:
            logger.warning(f"Rule {rule_id} not found")
            raise HTTPException(status_code=404, detail="Rule not found")
        
        doc_ref.delete()
        logger.info(f"Successfully deleted rule {rule_id}")
        return {"message": "Rule deleted successfully", "rule": None}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Checks the health of the API and its connection to Firestore."
)
async def health_check():
    try:
        # Try to access Firestore to verify connection
        db.collection(config.FIRESTORE_COLLECTION).limit(1).get()
        return {
            "status": "healthy",
            "project_id": config.PROJECT_ID,
            "database": config.FIRESTORE_DATABASE,
            "collection": config.FIRESTORE_COLLECTION
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 