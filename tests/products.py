def test_get_all_products(authorized_client):
    response = authorized_client.get("/products/getall")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list) # Check if the response is a list
    
def test_create_product(authorized_client,test_user):
    response= authorized_client.post("/products/post", json={"name": "Test Product", "details": {"description": "A product for testing"}, "price": 999})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"
    assert response.json()["owner"]["id"] == test_user["id"]

def test_get_product_by_id(authorized_client,test_user):
    # First, create a product
    create_response = authorized_client.post("/products/post", json={"name": "Testing Product", "details": {"description": "A product to get by id"}, "price": 909})
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    # Now, retrieve the product by ID
    response = authorized_client.get(f"/products/get/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == product_id
    assert product["name"] == "Testing Product"
    assert product["owner"]["id"] == test_user["id"]

def test_update_product(authorized_client,test_user):
    create_response = authorized_client.post(
        "/products/post",
        json={
            "name": "Original Product",
            "price": 10,
            "details": {"description": "Before update"},
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    response= authorized_client.put(f"/products/update/{product_id}", json={"name": "Updated Product", "details": {"description": "A product to delete"},  "price": 190})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"


def test_delete_product(authorized_client,test_user):
    # First, create a product to delete
    create_response = authorized_client.post("/products/post", json={"name": "Product to Delete", "price": 990, "details": {"description": "A product to delete"},})
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # Now, delete the product
    response = authorized_client.delete(f"/products/delete/{product_id}")
    assert response.status_code == 204
    
    # Verify that the product no longer exists
    get_response = authorized_client.get(f"/products/get/{product_id}")
    assert get_response.status_code == 404

def test_order_product(authorized_client,test_user):
    # First, create a product to order
    create_response = authorized_client.post("/products/post", json={"name": "Product to Order", "details": {"description": "This product will be ordered"}, "price": 900})
    assert create_response.status_code == 201, create_response.text
    product_id = create_response.json()["id"]
    
    # Now, order the product
    response = authorized_client.post(f"/products/order/{product_id}")
    assert response.status_code == 201
    assert response.json()["message"] == "Order placed successfully"