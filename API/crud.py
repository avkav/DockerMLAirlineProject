from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models_db, schemas_db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_passenger_satisfaction(db: Session, passenger: schemas_db.Questions_passenger_satisfactionCreate) -> models_db.Questions_passenger_satisfaction:
    try:
        db_passenger = models_db.Questions_passenger_satisfaction(**passenger.model_dump())
        db.add(db_passenger)
        db.commit()
        db.refresh(db_passenger)
        logger.info(f"Created passenger satisfaction record with id {db_passenger.id}")
        return db_passenger
    except SQLAlchemyError as e:
        logger.error(f"Error creating passenger satisfaction record: {str(e)}")
        db.rollback()
        raise



def update_passenger_satisfaction(db: Session, passenger_id: int, predicted_satisfaction: str) -> models_db.Questions_passenger_satisfaction:
    try:
        # Buscar el registro en la base de datos
        db_passenger = db.query(models_db.Questions_passenger_satisfaction).filter(models_db.Questions_passenger_satisfaction.id == passenger_id).first()

        if db_passenger is None:
            raise Exception(f"Passenger with id {passenger_id} not found.")

        # Actualizar el campo predicted_satisfaction
        db_passenger.predicted_satisfaction = predicted_satisfaction
        
        # Confirmar los cambios en la base de datos
        db.commit()
        db.refresh(db_passenger)
        logger.info(f"Updated passenger satisfaction record with id {db_passenger.id}")
        return db_passenger
    except SQLAlchemyError as e:
        logger.error(f"Error updating passenger satisfaction record: {str(e)}")
        db.rollback()
        raise


     


