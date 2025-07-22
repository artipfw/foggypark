import os
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import weaviate
import weaviate.classes.config as wc
from weaviate.classes.config import Configure

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weaviate_indexer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeaviateIndexer:
    """Enhanced Weaviate indexer with intelligent change detection and logging."""

    def __init__(self):
        self.weaviate_url = os.environ.get("WEAVIATE_URL", "localhost")
        self.openai_url = os.environ.get("TEXT2VEC_OPENAI_BASE_URL")
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.collection_name = "Chunk"
        self.data_file = "sample/datav3.json"
        self.metadata_file = "indexer_metadata.json"
        self.client = None

        logger.info("🚀 Initializing Weaviate Indexer")
        logger.info(f"📍 Weaviate URL: {self.weaviate_url}")
        logger.info(f"🤖 OpenAI Model: {self.openai_model}")

    def connect_to_weaviate(self) -> bool:
        """Establish connection to Weaviate instance."""
        try:
            logger.info("🔌 Connecting to Weaviate...")
            self.client = weaviate.connect_to_local(
                host="127.0.0.1",
                headers={"X-OpenAI-Api-Key": os.environ["HYPERMODE_API_KEY"]} if "HYPERMODE_API_KEY" in os.environ else None
            )

            if self.client.is_ready():
                logger.info("✅ Successfully connected to Weaviate")
                return True
            else:
                logger.error("❌ Weaviate is not ready")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to connect to Weaviate: {str(e)}")
            return False

    def load_data(self) -> Tuple[List[Dict], str]:
        """Load parking data and calculate content hash."""
        try:
            logger.info(f"📂 Loading data from {self.data_file}")

            if not os.path.exists(self.data_file):
                logger.error(f"❌ Data file not found: {self.data_file}")
                return [], ""

            with open(self.data_file, "r", encoding='utf-8') as f:
                data = json.load(f)

            # Process garage data
            docs = []
            for garage in data.get("garages", []):
                if garage.get("name"):  # Skip empty entries
                    doc = {
                        "title": garage.get("name", ""),
                        "content": f"Address: {garage.get('address', '')}. "
                                 f"Hourly Rate: {garage.get('hourlyRate', 'N/A')}. "
                                 f"Features: {', '.join(garage.get('features', []))}.",
                        "source": garage.get("website", ""),
                        "garage_id": garage.get("id", ""),
                        "hourly_rate": garage.get("hourlyRate", 0),
                        "phone": garage.get("phone", ""),
                        "hours": garage.get("hours", ""),
                        "last_updated": garage.get("lastUpdated", "")
                    }
                    docs.append(doc)

            # Calculate content hash for change detection
            content_str = json.dumps(docs, sort_keys=True)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()

            logger.info(f"📊 Loaded {len(docs)} garage records")
            logger.info(f"🔍 Content hash: {content_hash}")

            return docs, content_hash

        except Exception as e:
            logger.error(f"❌ Failed to load data: {str(e)}")
            return [], ""

    def load_metadata(self) -> Dict:
        """Load indexing metadata from file."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    metadata = json.load(f)
                logger.info(f"📋 Loaded metadata: {metadata}")
                return metadata
            else:
                logger.info("📋 No existing metadata found")
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Failed to load metadata: {str(e)}")
            return {}

    def save_metadata(self, content_hash: str, doc_count: int) -> None:
        """Save indexing metadata to file."""
        try:
            metadata = {
                "last_indexed": datetime.now().isoformat(),
                "content_hash": content_hash,
                "document_count": doc_count,
                "collection_name": self.collection_name,
                "data_file": self.data_file
            }

            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"💾 Saved metadata: {metadata}")

        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {str(e)}")

    def check_if_update_needed(self, current_hash: str) -> bool:
        """Check if data has changed since last indexing."""
        metadata = self.load_metadata()

        if not metadata:
            logger.info("🆕 No previous indexing found - update needed")
            return True

        last_hash = metadata.get("content_hash", "")

        if current_hash != last_hash:
            logger.info("🔄 Data has changed - update needed")
            logger.info(f"   Previous hash: {last_hash}")
            logger.info(f"   Current hash:  {current_hash}")
            return True
        else:
            logger.info("✅ Data unchanged - no update needed")
            return False

    def collection_exists(self) -> bool:
        """Check if collection exists."""
        try:
            collections = self.client.collections.list_all()
            exists = self.collection_name in collections
            logger.info(f"🗂️ Collection '{self.collection_name}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"❌ Failed to check collection existence: {str(e)}")
            return False

    def create_collection(self) -> bool:
        """Create Weaviate collection with proper schema."""
        try:
            logger.info(f"🏗️ Creating collection '{self.collection_name}'")

            self.client.collections.create(
                generative_config=Configure.Generative.openai(
                    model=self.openai_model,
                    base_url=self.openai_url
                ),
                name=self.collection_name,
                properties=[
                    wc.Property(name="title", data_type=wc.DataType.TEXT),
                    wc.Property(name="content", data_type=wc.DataType.TEXT),
                    wc.Property(name="source", data_type=wc.DataType.TEXT),
                    wc.Property(name="garage_id", data_type=wc.DataType.TEXT),
                    wc.Property(name="hourly_rate", data_type=wc.DataType.NUMBER),
                    wc.Property(name="phone", data_type=wc.DataType.TEXT),
                    wc.Property(name="hours", data_type=wc.DataType.TEXT),
                    wc.Property(name="last_updated", data_type=wc.DataType.TEXT),
                ],
                vectorizer_config=wc.Configure.Vectorizer.text2vec_ollama(
                    api_endpoint="http://host.docker.internal:11434", 
                    model="mxbai-embed-large"
                ),
            )

            logger.info("✅ Collection created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create collection: {str(e)}")
            return False

    def get_existing_document_count(self) -> int:
        """Get count of existing documents in collection."""
        try:
            collection = self.client.collections.get(self.collection_name)
            count = collection.aggregate.over_all(total_count=True).total_count
            logger.info(f"📊 Existing documents in collection: {count}")
            return count
        except Exception as e:
            logger.warning(f"⚠️ Failed to get document count: {str(e)}")
            return 0

    def clear_collection(self) -> bool:
        """Clear all documents from collection without deleting schema."""
        try:
            logger.info(f"🧹 Clearing collection '{self.collection_name}'")
            collection = self.client.collections.get(self.collection_name)

            # Delete all objects
            collection.data.delete_many(where={})

            logger.info("✅ Collection cleared successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to clear collection: {str(e)}")
            return False

    def index_documents(self, docs: List[Dict]) -> bool:
        """Index documents to Weaviate collection."""
        try:
            logger.info(f"📝 Indexing {len(docs)} documents...")

            collection = self.client.collections.get(self.collection_name)

            # Batch insert for better performance
            batch_size = 100
            successful_inserts = 0
            failed_inserts = 0

            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]

                try:
                    # Insert batch
                    for doc in batch:
                        collection.data.insert(doc)
                        successful_inserts += 1

                    logger.info(f"✅ Indexed batch {i//batch_size + 1}/{(len(docs)-1)//batch_size + 1}")

                except Exception as e:
                    logger.error(f"❌ Failed to index batch {i//batch_size + 1}: {str(e)}")
                    failed_inserts += len(batch)

            logger.info(f"📊 Indexing complete: {successful_inserts} successful, {failed_inserts} failed")

            return failed_inserts == 0

        except Exception as e:
            logger.error(f"❌ Failed to index documents: {str(e)}")
            return False

    def run_indexing(self, force_update: bool = False) -> bool:
        """Main indexing process with intelligent update detection."""
        try:
            logger.info("🚀 Starting indexing process...")

            # Connect to Weaviate
            if not self.connect_to_weaviate():
                return False

            # Load data and calculate hash
            docs, content_hash = self.load_data()
            if not docs:
                logger.error("❌ No data to index")
                return False

            # Check if update is needed
            if not force_update and not self.check_if_update_needed(content_hash):
                logger.info("✅ Indexing skipped - no changes detected")
                return True

            # Ensure collection exists
            if not self.collection_exists():
                if not self.create_collection():
                    return False
            else:
                logger.info(f"🗂️ Collection '{self.collection_name}' already exists")

                # Clear existing data for fresh indexing
                if not self.clear_collection():
                    return False

            # Index documents
            if not self.index_documents(docs):
                logger.error("❌ Indexing failed")
                return False

            # Save metadata
            self.save_metadata(content_hash, len(docs))

            logger.info("🎉 Indexing completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Indexing process failed: {str(e)}")
            return False

        finally:
            if self.client:
                self.client.close()
                logger.info("🔌 Weaviate connection closed")

def main():
    """Main function to run the indexer."""
    import argparse

    parser = argparse.ArgumentParser(description="Weaviate Parking Data Indexer")
    parser.add_argument("--force", action="store_true", help="Force update even if no changes detected")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    indexer = WeaviateIndexer()
    success = indexer.run_indexing(force_update=args.force)

    if success:
        logger.info("✅ Indexing process completed successfully")
        exit(0)
    else:
        logger.error("❌ Indexing process failed")
        exit(1)

if __name__ == "__main__":
    main()