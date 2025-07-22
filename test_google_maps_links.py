#!/usr/bin/env python3
"""
Test script for Google Maps links functionality
"""

from parking_knowledge import ParkingKnowledgeBase
from mcp_location_service import MCPLocationService

def test_parking_knowledge_links():
    """Test Google Maps links in parking knowledge base."""
    print("🧪 Testing Parking Knowledge Base Google Maps Links...")
    
    kb = ParkingKnowledgeBase()
    
    # Test affordable parking
    print("\n1. Testing Affordable Parking:")
    response = kb.get_affordable_parking()
    print(response[:500] + "..." if len(response) > 500 else response)
    
    # Test area parking
    print("\n2. Testing Area Parking (Union Square):")
    response = kb.get_area_parking(['union', 'square'])
    print(response[:500] + "..." if len(response) > 500 else response)
    
    # Test 24/7 parking
    print("\n3. Testing 24/7 Parking:")
    response = kb.get_24_7_parking()
    print(response[:500] + "..." if len(response) > 500 else response)

def test_mcp_location_links():
    """Test Google Maps links in MCP location service."""
    print("\n🧪 Testing MCP Location Service Google Maps Links...")
    
    service = MCPLocationService()
    
    # Test helper methods
    print("\n1. Testing Google Maps link creation:")
    test_address = "123 Market Street"
    link = service._create_google_maps_link(test_address)
    print(f"Address: {test_address}")
    print(f"Google Maps Link: {link}")
    
    formatted = service._format_address_with_link(test_address)
    print(f"Formatted: {formatted}")

def test_url_encoding():
    """Test URL encoding for various address formats."""
    print("\n🧪 Testing URL Encoding...")
    
    kb = ParkingKnowledgeBase()
    
    test_addresses = [
        "123 Market Street",
        "456 Mission St, Suite 100",
        "789 California Street & Powell",
        "Union Square Garage",
        "Financial District Parking"
    ]
    
    for address in test_addresses:
        link = kb._create_google_maps_link(address)
        print(f"Address: {address}")
        print(f"Link: {link}")
        print()

if __name__ == "__main__":
    test_parking_knowledge_links()
    test_mcp_location_links()
    test_url_encoding()
    print("\n✅ Google Maps links testing completed!")
