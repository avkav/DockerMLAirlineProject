from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models_db, schemas_db
from database import engine, get_db
import joblib
import os
from dotenv import load_dotenv
import crud
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

models_db.Base.metadata.create_all(bind=engine)

app = FastAPI()

MODEL_PATH = os.getenv("MODEL_PATH", "rf_model.pkl")
print(f"Trying to load model from: {MODEL_PATH}")

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

@app.post("/submit_and_predict/", response_model=schemas_db.Questions_passenger_satisfaction)
def submit_and_predict(passenger: schemas_db.Questions_passenger_satisfactionCreate, db: Session = Depends(get_db)):
    logger.debug(f"Received passenger data: {passenger}")
    if model is None:
        logger.error("Model not loaded")
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Preparar los datos para el modelo
        passenger_data = [
            [
                passenger.gender,
                1 if passenger.customer_type == "Loyal Customer" else 0,
                passenger.age,
                1 if passenger.travel_type == "Business Travel" else 0,
                0 if passenger.trip_class == "Eco" else (1 if passenger.trip_class == "Eco Plus" else 2),
                passenger.flight_distance,
                passenger.inflight_wifi_service,
                passenger.departure_arrival_time_convenient,
                passenger.online_booking,
                passenger.gate_location,
                passenger.food_and_drink,
                passenger.online_boarding,
                passenger.seat_comfort,
                passenger.inflight_entertainment,
                passenger.onboard_service,
                passenger.leg_room_service,
                passenger.baggage_handling,
                passenger.checkin_service,
                passenger.inflight_service,
                passenger.cleanliness,
                passenger.departure_delay_in_minutes,
            ]
        ]
        logger.debug(f"Prepared passenger data: {passenger_data}")

        # Realizar la predicción
        prediction = model.predict(passenger_data)
        predicted_satisfaction = "Satisfied" if prediction[0] == 1 else "Neutral or Dissatisfied"
        logger.debug(f"Prediction: {predicted_satisfaction}")
        
        # Crear el objeto de pasajero con la predicción
        passenger_dict = passenger.model_dump()

        # Crear pasajero en la base de datos sin la predicción
        db_passenger = crud.create_passenger_satisfaction(db=db, passenger=schemas_db.Questions_passenger_satisfactionCreate(**passenger_dict))
        logger.debug("Passenger data saved to database")

        # Actualizar la satisfacción predicha
        db_passenger = crud.update_passenger_satisfaction(db=db, passenger_id=db_passenger.id, predicted_satisfaction=predicted_satisfaction)
        logger.debug("Predicted satisfaction updated in database")
        
        # Devolver la respuesta con los datos actualizados
        return schemas_db.Questions_passenger_satisfaction(
            id=db_passenger.id,
            predicted_satisfaction=schemas_db.Satisfaction(predicted_satisfaction),
            **passenger_dict
        )

    except Exception as e:
        logger.exception("Error occurred during prediction or database operation")
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)