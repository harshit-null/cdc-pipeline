def handle_create(event):
    product = event["after"]

    print("=" * 60)
    print("CREATE EVENT")
    print(product)