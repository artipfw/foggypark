#!/usr/bin/env python3
"""
Simple test script for the enhanced Weaviate indexer (no Weaviate connection required)
"""

from weaviate_indexer import WeaviateIndexer

def test_data_loading():
    """Test data loading and hash calculation without Weaviate connection."""
    print("🧪 Testing Enhanced Weaviate Indexer - Data Loading")
    print("=" * 60)
    
    indexer = WeaviateIndexer()
    
    # Test data loading and hash calculation
    print("\n📝 Test: Data loading and hash calculation")
    docs, content_hash = indexer.load_data()
    
    if docs:
        print(f"✅ Successfully loaded {len(docs)} documents")
        print(f"🔍 Content hash: {content_hash}")
        
        # Show sample document
        if docs:
            print(f"\n📄 Sample document:")
            sample_doc = docs[0]
            for key, value in sample_doc.items():
                print(f"  {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
    else:
        print("❌ Failed to load data")
        return False
    
    # Test metadata operations
    print(f"\n📝 Test: Metadata operations")
    
    # Test saving metadata
    indexer.save_metadata(content_hash, len(docs))
    print("✅ Metadata saved")
    
    # Test loading metadata
    metadata = indexer.load_metadata()
    if metadata:
        print("✅ Metadata loaded:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Failed to load metadata")
        return False
    
    # Test change detection
    print(f"\n📝 Test: Change detection")
    needs_update = indexer.check_if_update_needed(content_hash)
    print(f"Update needed: {needs_update}")
    
    # Test with different hash
    fake_hash = "different_hash_123"
    needs_update = indexer.check_if_update_needed(fake_hash)
    print(f"Update needed with different hash: {needs_update}")
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"\nGenerated files:")
    print(f"- weaviate_indexer.log (indexer logs)")
    print(f"- indexer_metadata.json (metadata)")
    
    return True

if __name__ == "__main__":
    success = test_data_loading()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
