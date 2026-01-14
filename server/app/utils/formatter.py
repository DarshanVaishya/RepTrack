def format_response(data, message: str | None = None):
    if message:
        return {"success": True, "message": message, "data": data}
    else:
        return {"success": True, "data": data}
