import os
from datetime import datetime
from pymongo import MongoClient, errors


def context_collector(
    product_name,
    description,
    image_links=None,
    hosting_platform=None,
    target_audience=None,
    additional_info=None,
    user_id=None,
    created_at=None,
    updated_at=None,
    mongodb_uri=None
):
    """
    Collects product marketing info and stores metadata in MongoDB.
    
    Required parameters:
    - product_name: Name of the product
    - description: Description of the product
    
    Optional parameters:
    - image_links: List of image URLs/links (not file paths)
    - hosting_platform: Where the product will be hosted
    - target_audience: Target audience for the product
    - additional_info: Dictionary of additional information
    - user_id: User identifier
    - created_at: Creation timestamp (defaults to current time)
    - updated_at: Update timestamp (defaults to current time)
    - mongodb_uri: MongoDB connection URI (defaults to MONGODB_URI env var)
    
    Returns:
    - Dictionary with inserted_id and image_links
    """
    
    # Validate required fields
    if not product_name or not description:
        raise ValueError("product_name and description are required")
    
    # Set default timestamps
    now = datetime.utcnow()
    if created_at is None:
        created_at = now
    if updated_at is None:
        updated_at = now
    
    # Get MongoDB URI from environment if not provided
    if mongodb_uri is None:
        mongodb_uri = os.environ.get("MONGODB_URI")
    
    if not mongodb_uri:
        raise RuntimeError("MONGODB_URI environment variable not set")
    
    # Validate image_links if provided
    if image_links is not None:
        if not isinstance(image_links, list):
            raise ValueError("image_links must be a list of URLs/links")
        # You can add additional validation here if needed
        # For example, check if links are valid URLs
    
    # Connect to MongoDB for storing product metadata
    try:
        client = MongoClient(mongodb_uri)
        db = client["marketing_db"]
        collection = db["product_marketing"]
        
    except errors.PyMongoError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {e}")
    
    # Prepare document for MongoDB
    document = {
        "product_name": product_name,
        "description": description,
        "created_at": created_at,
        "updated_at": updated_at
    }
    
    # Add optional fields if provided
    if image_links:
        document["images"] = image_links
    if hosting_platform:
        document["hosting_platform"] = hosting_platform
    if target_audience:
        document["target_audience"] = target_audience
    if additional_info:
        document["additional_info"] = additional_info
    if user_id:
        document["user_id"] = user_id
    
    # Insert into MongoDB
    try:
        result = collection.insert_one(document)
        inserted_id = result.inserted_id
    except errors.PyMongoError as e:
        raise RuntimeError(f"Failed to insert document into MongoDB: {e}")
    finally:
        client.close()
    
    return {
        "inserted_id": str(inserted_id),
        "image_links": image_links or []
    }