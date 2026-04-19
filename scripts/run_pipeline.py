from __future__ import annotations

from app.core.database import Base, SessionLocal, engine
from app.models.entities import Incident, SourceDocument
from app.services.briefer import BriefingService
from app.services.extractor import IncidentExtractor
from app.services.mapper import MapService
from app.services.news_ingestor import GoogleNewsRSSIngestor


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ingestor_stats = GoogleNewsRSSIngestor(db).ingest()
        extractor = IncidentExtractor(db)
        before_unextracted = extractor.count_unextracted_documents()
        extracted = extractor.extract_new_documents()
        after_unextracted = extractor.count_unextracted_documents()
        map_path = MapService(db).build_map()
        brief_path = BriefingService(db).build_daily_html()
        print({
            "status": "ok",
            "message": (
                "No new articles were ingested; existing DB reused."
                if ingestor_stats["inserted"] == 0 and db.query(SourceDocument).count() > 0
                else "Pipeline completed."
            ),
            "ingest": ingestor_stats,
            "extract": {
                "before_unextracted": before_unextracted,
                "extracted": extracted,
                "after_unextracted": after_unextracted,
            },
            "totals": {
                "documents": db.query(SourceDocument).count(),
                "incidents": db.query(Incident).count(),
            },
            "map": map_path,
            "brief": brief_path,
        })
    finally:
        db.close()


if __name__ == "__main__":
    main()
