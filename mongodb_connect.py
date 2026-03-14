from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

db = client["people_record"]

home_country_code = "USA"


def build_record(id, info):
    numeric_id = int(str(id).split(".")[0]) 
    return {
        "created_at" : datetime.datetime.utcnow(),
        "person_id": numeric_id, 
        "passport_type": info.get('Type'),
        "Country_Code": info.get("Country_Code"),
        "Passport_No": info.get("Passport_No"),
        "Surname": info.get("Surname"),
        "Given_Name": info.get("Given_Name"),
        "DOB": info.get("DOB"),
        "POB": info.get("POB"),
        "POI": info.get("POI"),
        "DOI": info.get("DOI"),
        "DOE": info.get("DOE"),
        "crime": info.get("crime", None), 
        "passport_validity_time": info.get("passport_validity_time", None),
        "visa_status": info.get("visa_status", None),
        "student_sevis_data": info.get("student_sevis_data", None), 
        "i94_form_completed": info.get("i94_form_completed", None), 
        "customs_declaration_completed": info.get("customs_declaration_completed", None), 
        "biometrics_captured": info.get("biometrics_captured", None) 
    }


def entry_db(id, info):
    entry_collection = db["daily_entry"]
    non_exit_collection = db["non_exit"]
    all_collection = db["all-records"]

    record = build_record(id, info)

    entry_collection.insert_one(record)

    if info["Country_Code"] != home_country_code:
        non_exit_collection.insert_one(record)
        all_collection.insert_one(record)
    print("Entry logged")


def exit_db(id, info):
    exit_collection = db["daily_exit"]
    non_exit_collection = db["non_exit"]

    record = build_record(id, info)
    exit_collection.insert_one(record)

    numeric_id = int(str(id).split(".")[0]) 
    if info["Country_Code"] != home_country_code:
        non_exit_collection.delete_one({"person_id": numeric_id}) 
    print("Exit logged")

def get_data(id):
    collection = db["all-records"]
    numeric_id = int(str(id).split(".")[0]) 
    return collection.find_one({"person_id": numeric_id})