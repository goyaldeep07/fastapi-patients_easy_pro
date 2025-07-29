"""
uvicorn main:app --reload
http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from typing import Optional, Annotated, Literal
import json

app = FastAPI()
class Patient(BaseModel):
    """{"name": "Ananya Verma", "city": "Guwahati", "age": 28, "gender": "female", "height": 1.65, "weight": 90.0, "bmi": 33.06, "verdict": "Obese"}"""
    id: Annotated[str, Field(description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(description="The name of the patient", example="John Doe", min_length=1, max_length=100)]
    city: Annotated[str, Field(description="City of the patient", example="Delhi", min_length=1, max_length=100)]
    age: Annotated[int, Field(description="The age of the patient", example=30, ge=0)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(description="Gender of the patient", example="female")]
    height: Annotated[float, Field(description="The height of the patient in meters", example=1.75, gt=0)]
    weight: Annotated[float, Field(gt=0, description="Weight in kg", example=70.5)]

    @computed_field
    @property
    def bmi(self) -> float:
        """Calculate Body Mass Index (BMI)"""
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        """Determine the verdict based on BMI"""
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            return "Normal weight"
        elif 25 <= bmi_value < 29.9:
            return "Overweight"
        else:
            return "Obese"

def load_data():
    with open("patients.json", "r") as file:
        json_data = json.load(file)
    return json_data

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file, indent=4)

@app.get("/")
def hello():
    return {"message": "Hello, World!"}


@app.get("/about")
def about():
    return {"message": "CampusX is a community of learners and educators."}


@app.get("/view")
def view():
    data = load_data()
    return {"data": data}

# /patients?city=Delhi&sort_by=age

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to view", example="P001")):
    data = load_data()
    if patient_id in data:
        return {"patient": data[patient_id]}
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Field to sort by", example="age"), order: str = Query("asc", description="Order of sorting", example="asc")):
    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields: 
        raise HTTPException(status_code=400, detail="Invalid sort field, must be one of: " + ", ".join(valid_fields))
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order, must be 'asc' or 'desc'")
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    return {"sorted_patients": sorted_data}

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    patient_id = patient.id
    if patient_id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    data[patient_id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return {"message": "Patient created successfully", "patient": data[patient_id]}