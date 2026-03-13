from image_extract import convert
from mongodb_connect import entry_db

a = convert("123.png").dict()
entry_db(123, a)