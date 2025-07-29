from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe", min_length=1, max_length=100)]
    # name: str = Field(..., description="The name of the patient", example="John Doe", min_length=1, max_length=100)
    age: int = Field(..., description="The age of the patient", example=30, ge=0)
    email: EmailStr
    weight: float = Field(..., description="The weight of the patient in kg", example=70.5, gt=0, strict=True)
    height: Optional[float] = Field(None, description="The height of the patient in cm", example=175.0, gt=0, strict=True)
    married: bool = Field(False, description="Marital status of the patient", example=True, title="Marital Status")
    # allergies: List[str] = []
    allergies: Optional[List[str]] = Field(None, description="List of allergies the patient has", example=["Peanuts", "Penicillin"], max_length=5)
    contact_details: Dict[str, str] = {}
    linked_in: AnyUrl

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return value.strip().upper()  # Ensure name is upper-cased

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        """check email belongs to hdfc.com domain or icici.com domain"""
        valid_domains = ["hdfc.com", "icici.com"]
        # abc@gmail.com
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError(f"Email must be from one of the following domains: {', '.join(valid_domains)}")
        return value
    
    @model_validator(mode='after')
    @classmethod
    def validate_emergency_contact(cls, model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError("Emergency contact phone number is required in contact_details for patients over 60 years old")
        return cls
    
    @computed_field
    @property
    def bmi(self) -> float:
        if self.height and self.weight:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return 0.0

def insert_patient(patient: Patient):
    # Here you would typically insert the patient into a database or data structure
    print(f"Inserting patient: {patient.name}, Age: {patient.age}")
    print(patient.allergies)
    print(patient.email)
    print(patient.bmi)

    return {"message": "Patient inserted successfully", "patient": patient}


# patient_info = {'name': 'John Doe', 'email': 'abc@gmail.com', 'age': "30", 'weight': '70.5', 'married': True, 'contact_details': {'phone': '1234567890'}, "linked_in": 'https://www.linkedin.com/in/johndoe/' }
patient_info = {'name': 'John Doe', 'email': 'abc@icici.com', 'age': "55", 'weight': 70.5, 'height': 172, 'married': True, 'contact_details': {'phone': '1234567890'}, "linked_in": 'https://www.linkedin.com/in/johndoe/' }
patient1 = Patient(**patient_info)
# print(patient1)

insert_patient(patient1)