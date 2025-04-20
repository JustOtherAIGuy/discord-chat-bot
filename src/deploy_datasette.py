import modal
from pathlib import Path
import os

app = modal.App("discord-bot-datasette")

# Create an image with Datasette and its dependencies
image = modal.Image.debian_slim().pip_install(
    "datasette",
    "sqlite-utils",
)

# Mount the database directory
current_dir = Path(__file__).parent
db_path = current_dir / "bot_interactions.db"

@app.function(
    image=image,
    mounts=[Mount.from_local_file(db_path, remote_path="/data/bot_interactions.db")],
)
@asgi_app()
def database():
    from datasette.app import Datasette
    ds = Datasette(
        ["/data/bot_interactions.db"],
        settings={
            "default_page_size": 50,
            "sql_time_limit_ms": 2000,
        }
    )
    return ds.database()