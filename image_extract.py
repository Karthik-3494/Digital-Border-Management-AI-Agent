from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import base64
import os
from dotenv import load_dotenv

load_dotenv()



class output_structure(BaseModel):
    Type: str = Field(description="indicates the document's purpose and category given in top left")
    Country_Code: str = Field(description="Passport country codes are typically 3-letter (alpha-3) or 2-letter (alpha-2) abbreviations based on the ISO 3166 standard, used to identify the issuing country on travel documents.")
    Passport_No : str = Field(description="a unique alphanumeric identifier, typically 8-9 characters long, located on the bio-data page (photo page) of your passport, usually in the top-right corner")
    Surname: str = Field(description="surname field data")
    Given_Name: str = Field(description="Given Name field data")
    DOB : str = Field(description="Date of Birth")
    POB : str = Field(description="Place of Birth")
    POI : str = Field(description="Place of Issue")
    DOI : str = Field(description="Date of Issue")
    DOE : str = Field(description="Date of expiry")



def convert(id):
    folder = r"C:\Users\karth\OneDrive\Desktop\PROJECTS\digital_border_sys\passport_images"
    path = os.path.join(folder,id)

    model = ChatOpenAI(model = "gpt-4o-mini")

    try: 

        with open(path,"rb") as img:
            encoded_image = base64.b64encode(img.read()).decode("utf-8")

        structured_model = model.with_structured_output(output_structure)

        prompt = HumanMessage(
            content=[
                {"type": "text", 
                "text": "Given the passport scan image, extract the required fields exactly as requested."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                }
            ]
        )

        response = structured_model.invoke([prompt])
    
    except Exception as e:
        print(f"Error : {e}")

    return response
