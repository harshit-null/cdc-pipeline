def handle_update(event):
    product = event["after"]

    print("=" * 60)
    print("UPDATE EVENT")
    print(product)