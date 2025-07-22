#!/usr/bin/env python3
"""
Test script for the dynamic parking knowledge base
"""

from parking_knowledge import ParkingKnowledgeBase

def test_knowledge_base():
    """Test the parking knowledge base functionality."""
    print("🧪 Testing Dynamic Parking Knowledge Base")
    print("=" * 50)
    
    kb = ParkingKnowledgeBase()
    
    # Test 1: Affordable parking
    print("\n📝 Test 1: Affordable Parking")
    print("-" * 30)
    response = kb.get_affordable_parking()
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 2: Area-specific parking
    print("\n📝 Test 2: Union Square Parking")
    print("-" * 30)
    response = kb.get_area_parking(['union', 'square'])
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 3: 24/7 parking
    print("\n📝 Test 3: 24/7 Parking")
    print("-" * 30)
    response = kb.get_24_7_parking()
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 4: EV parking
    print("\n📝 Test 4: EV Charging Parking")
    print("-" * 30)
    response = kb.get_ev_parking()
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 5: Features info
    print("\n📝 Test 5: Features Information")
    print("-" * 30)
    response = kb.get_features_info()
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 6: General info
    print("\n📝 Test 6: General Information")
    print("-" * 30)
    response = kb.get_general_info()
    print(response[:200] + "..." if len(response) > 200 else response)
    
    print("\n🎉 Knowledge base testing completed!")

if __name__ == "__main__":
    test_knowledge_base()
