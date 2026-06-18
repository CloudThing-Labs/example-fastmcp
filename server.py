import aiosqlite
from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan

DB = "data.db"

@lifespan
async def db_lifespan(server):
    db = await aiosqlite.connect(DB)
    db.row_factory = aiosqlite.Row
    await db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT,
            price       REAL    NOT NULL DEFAULT 0.0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.commit()
    try:
        yield {"db": db}
    finally:
        await db.close()

mcp = FastMCP("SQLite CRUD Server", lifespan=db_lifespan)

@mcp.tool
async def create_item(name: str, price: float, description: str | None = None, ctx: Context = None) -> dict:
    """Add a new item"""
    db = ctx.lifespan_context["db"]
    cur = await db.execute("INSERT INTO items (name, description, price) VALUES (?, ?, ?)", (name, description, price))
    await db.commit()
    row = await (await db.execute("SELECT * FROM items WHERE id = ?", (cur.lastrowid,))).fetchone()
    return dict(row)

@mcp.tool
async def list_items(name_filter: str | None = None, ctx: Context = None) -> list[dict]:
    """List items. If name_filter is given, search by name (partial match)."""
    db = ctx.lifespan_context["db"]
    if name_filter:
        rows = await (await db.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{name_filter}%",))).fetchall()
    else:
        rows = await (await db.execute("SELECT * FROM items")).fetchall()
    return [dict(r) for r in rows]

@mcp.tool
async def get_item(item_id: int, ctx: Context = None) -> dict:
    """Get one item by ID"""
    db = ctx.lifespan_context["db"]
    row = await (await db.execute("SELECT * FROM items WHERE id = ?", (item_id,))).fetchone()
    if row is None:
        raise ValueError(f"Item {item_id} not found")
    return dict(row)

@mcp.tool
async def update_item(item_id: int, name: str | None = None, description: str | None = None, price: float | None = None, ctx: Context = None) -> dict:
    """Update an item. Only passed fields are changed, others keep their old value."""
    db = ctx.lifespan_context["db"]
    cur = await db.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    old = await cur.fetchone()
    if old is None:
        raise ValueError(f"Item {item_id} not found")
    await db.execute(
        "UPDATE items SET name=?, description=?, price=? WHERE id=?",
        (name if name is not None else old["name"],
         description if description is not None else old["description"],
         price if price is not None else old["price"],
         item_id),
    )
    await db.commit()
    row = await (await db.execute("SELECT * FROM items WHERE id = ?", (item_id,))).fetchone()
    return dict(row)

@mcp.tool
async def delete_item(item_id: int, ctx: Context = None) -> str:
    """Delete an item by ID"""
    db = ctx.lifespan_context["db"]
    cur = await db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    await db.commit()
    if cur.rowcount == 0:
        raise ValueError(f"Item {item_id} not found")
    return f"Deleted item {item_id}"

if __name__ == "__main__":
    mcp.run()
