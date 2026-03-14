from sqlalchemy.orm import Session
from typing import List
from app.models.ai_enrichment_log import AIEnrichmentLog

def log_enrichment(db: Session, entity_type: str, entity_id: str, enrichment_type: str, input_text: str, output_json: dict) -> AIEnrichmentLog:
    log = AIEnrichmentLog(
        entity_type=entity_type,
        entity_id=entity_id,
        enrichment_type=enrichment_type,
        input_text=input_text,
        output_json=output_json,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs_for_entity(db: Session, entity_type: str, entity_id: str) -> List[AIEnrichmentLog]:
    return db.query(AIEnrichmentLog).filter(
        AIEnrichmentLog.entity_type == entity_type,
        AIEnrichmentLog.entity_id == entity_id,
    ).all()
