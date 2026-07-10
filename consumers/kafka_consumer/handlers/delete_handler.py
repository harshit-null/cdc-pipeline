def handle_delete(event):
    product = event["before"]

    print("=" * 60)
    print("DELETE EVENT")
    print(product)