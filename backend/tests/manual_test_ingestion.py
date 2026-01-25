import sys
import os
from datetime import date
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Mock database session
class MockSession:
    def add(self, obj):
        print(f"[DB] Adding {type(obj).__name__}: {obj.__dict__.get('amount', obj.__dict__.get('turnover'))}")
    def commit(self):
        print("[DB] Commit")

from app.services.ingestion_service import IngestionService

def test_ingestion():
    db = MockSession()
    service = IngestionService(db)
    
    # Paths to sample data
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sample_data'))
    tally_path = os.path.join(base_dir, 'tally_ledger_sample.csv')
    gst_path = os.path.join(base_dir, 'gstr3b_sample.json')
    
    print("\n--- Testing Tally Ingestion ---")
    if os.path.exists(tally_path):
        service.ingest_ledger(tally_path, "test-entity-id")
    else:
        print("Tally sample not found")

    print("\n--- Testing GST Ingestion ---")
    if os.path.exists(gst_path):
        service.ingest_gst(gst_path, "test-entity-id")
    else:
        print("GST sample not found")

if __name__ == "__main__":
    test_ingestion()
