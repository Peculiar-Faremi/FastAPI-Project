def test_get_all_products(authorized_client):
    response = authorized_client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list) # Check if the response is a list
    