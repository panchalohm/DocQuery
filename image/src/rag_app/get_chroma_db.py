import shutil
import os
import sys
from langchain_community.vectorstores import Chroma
from .get_embedding_function import get_embedding_function

CHROMA_PATH = os.environ.get("CHROMA_PATH", "data/chroma")
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
CHROMA_DB_INSTANCE = None  # Reference to singleton instance of ChromaDB


def get_chroma_db():
    global CHROMA_DB_INSTANCE
    if not CHROMA_DB_INSTANCE:

        # Doing this way for AWS Lambda's base Python image to work with updated version of SQLite
        # In lambda runtime, we need to copy ChromaDB to /tmp so it can have write permissions.
        if IS_USING_IMAGE_RUNTIME:
            __import__("pysqlite3")
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
            copy_chroma_to_top()

        # Prepare the DB.
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=get_runtime_chroma_path(),
            embedding_function=get_embedding_function(),
        )
        print(f"✅ Init ChromaDB {CHROMA_DB_INSTANCE} from {get_runtime_chroma_path()}")

    return CHROMA_DB_INSTANCE

# Only using when in image runtime
def copy_chroma_to_top():
    dst_chroma_path = get_runtime_chroma_path()

    # Check if path exists
    if not os.path.exists(dst_chroma_path):
        os.makedirs(dst_chroma_path)

    # Create the path if it doesn't and then copies everything over
    tmp_contents = os.listdir(dst_chroma_path)
    if len(tmp_contents) == 0:
        print(f"Copying ChromaDB from {CHROMA_PATH} to {dst_chroma_path}")
        os.makedirs(dst_chroma_path, exist_ok=True)
        shutil.copytree(CHROMA_PATH, dst_chroma_path, dirs_exist_ok=True)
    else:
        print(f"✅ ChromaDB already exists in {dst_chroma_path}")


# Returns where the chroma directort depending on image runtime environment
def get_runtime_chroma_path():
    if IS_USING_IMAGE_RUNTIME:
        return f"/tmp/{CHROMA_PATH}" # For Lambda
    else:
        return CHROMA_PATH
