from handlers.create_handler import handle_create
from handlers.update_handler import handle_update
from handlers.delete_handler import handle_delete


def route_event(event):
    op = event.get("op")

    if op == "c":
        handle_create(event)

    elif op == "u":
        handle_update(event)

    elif op == "d":
        handle_delete(event)

    elif op == "r":
        handle_create(event)   # Snapshot event

    else:
        print(f"Unknown operation: {op}")