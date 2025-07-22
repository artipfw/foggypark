#!/usr/bin/env python3
"""
Test script to demonstrate the improved Weaviate indexer functionality
"""

import os
import json
import time
from weaviate_indexer import WeaviateIndexer

def test_indexer():
    """Test the enhanced indexer functionality."""
    print("🧪 Testing Enhanced Weaviate Indexer")
    print("=" * 50)
    
    indexer = WeaviateIndexer()
    
    # Test 1: First run (should index everything)
    print("\n📝 Test 1: Initial indexing")
    success = indexer.run_indexing()
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Second run (should skip - no changes)
    print("\n📝 Test 2: Re-run without changes")
    success = indexer.run_indexing()
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Force update
    print("\n📝 Test 3: Force update")
    success = indexer.run_indexing(force_update=True)
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n🎉 Testing completed!")
    print("\nCheck the following files:")
    print("- weaviate_indexer.log (detailed logs)")
    print("- indexer_metadata.json (indexing metadata)")

if __name__ == "__main__":
    test_indexer()
