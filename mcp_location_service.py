#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Location Service for Parking Assistant
Provides location-based parking recommendations and geocoding capabilities
"""

import json
import re
import requests
import urllib.parse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Location:
    """Represents a geographic location."""
    name: str
    address: str
    latitude: float
    longitude: float
    confidence: float = 1.0

@dataclass
class ParkingRecommendation:
    """Represents a parking recommendation with location context."""
    garage_name: str
    address: str
    hourly_rate: float
    distance_km: float
    walking_time_min: int
    features: List[str]
    hours: str
    phone: str = ""

class MCPLocationService:
    """MCP service for location-based parking assistance."""
    
    def __init__(self):
        self.sf_landmarks = {
            # Major landmarks and their approximate coordinates
            "union square": (37.7880, -122.4074),
            "financial district": (37.7946, -122.3999),
            "chinatown": (37.7941, -122.4078),
            "north beach": (37.8044, -122.4078),
            "soma": (37.7749, -122.4194),
            "mission district": (37.7599, -122.4148),
            "castro": (37.7609, -122.4350),
            "haight ashbury": (37.7692, -122.4481),
            "marina district": (37.8021, -122.4416),
            "nob hill": (37.7928, -122.4161),
            "russian hill": (37.8014, -122.4161),
            "pacific heights": (37.7930, -122.4274),
            "mission bay": (37.7706, -122.3892),
            "embarcadero": (37.7955, -122.3933),
            "fishermans wharf": (37.8080, -122.4177),
            "pier 39": (37.8087, -122.4098),
            "lombard street": (37.8021, -122.4187),
            "golden gate park": (37.7694, -122.4862),
            "japantown": (37.7857, -122.4300),
            "tenderloin": (37.7837, -122.4151)
        }
        
    def _create_google_maps_link(self, address: str) -> str:
        """Create a Google Maps link for the given address."""
        if not address:
            return ""
        
        # Clean the address - remove extra spaces and normalize
        clean_address = ' '.join(address.split())
        
        # Add San Francisco context if not already present
        if 'san francisco' not in clean_address.lower():
            clean_address = f"{clean_address}, San Francisco, CA"
        
        # Encode the address for URL
        encoded_address = urllib.parse.quote_plus(clean_address)
        return f"https://maps.google.com/maps?q={encoded_address}"
    
    def _format_address_with_link(self, address: str) -> str:
        """Format address with Google Maps link using HTML for Streamlit compatibility."""
        if not address:
            return "📍 Address not available"
        
        maps_link = self._create_google_maps_link(address)
        # Use HTML link format for better Streamlit compatibility
        return f'📍 <a href="{maps_link}" target="_blank">{address}</a>'
        
    def extract_location_from_query(self, query: str) -> Optional[Location]:
        """Extract location information from user query."""
        query_lower = query.lower()
        
        # Check for specific landmarks
        for landmark, coords in self.sf_landmarks.items():
            if landmark in query_lower:
                return Location(
                    name=landmark.title(),
                    address=f"{landmark.title()}, San Francisco, CA",
                    latitude=coords[0],
                    longitude=coords[1],
                    confidence=0.9
                )
        
        # Look for address patterns
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|boulevard|blvd|road|rd|drive|dr)',
            r'[A-Za-z\s]+(?:street|st|avenue|ave|boulevard|blvd|road|rd|drive|dr)\s+(?:and|&|\+)\s+[A-Za-z\s]+(?:street|st|avenue|ave)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                address = match.group(0)
                # Try to geocode the address
                location = self._geocode_address(address)
                if location:
                    return location
        
        # Look for "near" patterns
        near_pattern = r'near\s+([A-Za-z\s]+)'
        match = re.search(near_pattern, query_lower)
        if match:
            location_name = match.group(1).strip()
            # Check if it's a known landmark
            for landmark, coords in self.sf_landmarks.items():
                if landmark in location_name or location_name in landmark:
                    return Location(
                        name=landmark.title(),
                        address=f"Near {landmark.title()}, San Francisco, CA",
                        latitude=coords[0],
                        longitude=coords[1],
                        confidence=0.8
                    )
        
        return None
    
    def _geocode_address(self, address: str) -> Optional[Location]:
        """Geocode an address using a simple geocoding service."""
        # For demo purposes, we'll use a simple pattern matching
        # In production, you'd use a real geocoding service like Google Maps API
        
        # Add San Francisco context if not present
        if "san francisco" not in address.lower() and "sf" not in address.lower():
            address += ", San Francisco, CA"
        
        # Simple pattern matching for common SF streets
        sf_streets = {
            "market street": (37.7879, -122.4075),
            "mission street": (37.7849, -122.4094),
            "valencia street": (37.7599, -122.4209),
            "fillmore street": (37.7849, -122.4324),
            "van ness avenue": (37.7849, -122.4194),
            "geary boulevard": (37.7817, -122.4324),
            "california street": (37.7919, -122.4074),
            "polk street": (37.7919, -122.4194),
            "columbus avenue": (37.7980, -122.4074),
            "broadway": (37.7980, -122.4074)
        }
        
        address_lower = address.lower()
        for street, coords in sf_streets.items():
            if street in address_lower:
                return Location(
                    name=street.title(),
                    address=address,
                    latitude=coords[0],
                    longitude=coords[1],
                    confidence=0.7
                )
        
        return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    
    def find_nearby_parking(self, location: Location, parking_data: List[Dict], max_distance_km: float = 2.0) -> List[ParkingRecommendation]:
        """Find parking options near a specific location."""
        recommendations = []
        
        for garage in parking_data:
            if not garage.get('name'):
                continue
                
            # For demo, we'll use approximate coordinates based on address patterns
            garage_coords = self._estimate_garage_coordinates(garage)
            if not garage_coords:
                continue
                
            distance = self.calculate_distance(
                location.latitude, location.longitude,
                garage_coords[0], garage_coords[1]
            )
            
            if distance <= max_distance_km:
                # Estimate walking time (average walking speed: 5 km/h)
                walking_time = int((distance / 5.0) * 60)  # minutes
                
                recommendation = ParkingRecommendation(
                    garage_name=garage.get('name', 'Unknown'),
                    address=garage.get('address', 'Address not available'),
                    hourly_rate=garage.get('hourlyRate', 0),
                    distance_km=round(distance, 2),
                    walking_time_min=walking_time,
                    features=garage.get('features', []),
                    hours=garage.get('hours', 'Hours not available'),
                    phone=garage.get('phone', '')
                )
                recommendations.append(recommendation)
        
        # Sort by distance
        recommendations.sort(key=lambda x: x.distance_km)
        return recommendations[:5]  # Return top 5 closest
    
    def _estimate_garage_coordinates(self, garage: Dict) -> Optional[Tuple[float, float]]:
        """Estimate garage coordinates based on address patterns."""
        address = garage.get('address', '').lower()
        
        # Simple coordinate estimation based on address patterns
        coordinate_map = {
            'union square': (37.7880, -122.4074),
            'financial district': (37.7946, -122.3999),
            'chinatown': (37.7941, -122.4078),
            'north beach': (37.8044, -122.4078),
            'soma': (37.7749, -122.4194),
            'mission': (37.7599, -122.4148),
            'castro': (37.7609, -122.4350),
            'marina': (37.8021, -122.4416),
            'nob hill': (37.7928, -122.4161),
            'russian hill': (37.8014, -122.4161),
            'pacific heights': (37.7930, -122.4274),
            'embarcadero': (37.7955, -122.3933),
            'fisherman': (37.8080, -122.4177),
            'japantown': (37.7857, -122.4300),
            'fillmore': (37.7849, -122.4324),
            'valencia': (37.7599, -122.4209),
            'market': (37.7879, -122.4075),
            'geary': (37.7817, -122.4324),
            'california': (37.7919, -122.4074),
            'polk': (37.7919, -122.4194),
            'columbus': (37.7980, -122.4074),
            'broadway': (37.7980, -122.4074)
        }
        
        for keyword, coords in coordinate_map.items():
            if keyword in address:
                return coords
        
        # Default to downtown SF if no match
        return (37.7879, -122.4075)
    
    def format_location_response(self, location: Location, recommendations: List[ParkingRecommendation]) -> str:
        """Format the location-based parking response."""
        if not recommendations:
            return f"""**Parking near {location.name}:**

I found your location at {location.address}, but unfortunately no parking garages were found within 2km of this location.

**Suggestions:**
• Try searching for parking in nearby neighborhoods
• Consider public transportation options
• Look for street parking with meter restrictions
• Check parking apps for real-time availability"""

        response = f"**Parking near {location.name}:**\n\n"
        response += f"{self._format_address_with_link(location.address)}\n\n"
        response += "**Nearby Parking Options:**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            response += f"**{i}. {rec.garage_name}**\n"
            response += f"   💰 ${rec.hourly_rate}/hour\n"
            response += f"   {self._format_address_with_link(rec.address)}\n"
            response += f"   🚶 {rec.walking_time_min} min walk ({rec.distance_km} km)\n"
            response += f"   🕒 {rec.hours}\n"
            
            if rec.phone:
                response += f"   📞 {rec.phone}\n"
            
            if rec.features:
                response += f"   ✨ Features: {', '.join(rec.features[:3])}\n"
            
            response += "\n"
        
        response += "**💡 Tips:**\n"
        response += "• Prices may vary by time of day\n"
        response += "• Check for validation at nearby businesses\n"
        response += "• Consider early bird specials for all-day parking\n"
        
        return response

# MCP Tool Functions
def mcp_extract_location(query: str) -> Dict:
    """MCP tool to extract location from user query."""
    service = MCPLocationService()
    location = service.extract_location_from_query(query)
    
    if location:
        return {
            "success": True,
            "location": {
                "name": location.name,
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "confidence": location.confidence
            }
        }
    else:
        return {
            "success": False,
            "message": "Could not extract location from query"
        }

def mcp_find_nearby_parking(location_data: Dict, parking_data: List[Dict]) -> Dict:
    """MCP tool to find parking near a location."""
    service = MCPLocationService()
    
    location = Location(
        name=location_data["name"],
        address=location_data["address"],
        latitude=location_data["latitude"],
        longitude=location_data["longitude"],
        confidence=location_data.get("confidence", 1.0)
    )
    
    recommendations = service.find_nearby_parking(location, parking_data)
    response_text = service.format_location_response(location, recommendations)
    
    return {
        "success": True,
        "response": response_text,
        "recommendations": [
            {
                "name": rec.garage_name,
                "address": rec.address,
                "rate": rec.hourly_rate,
                "distance_km": rec.distance_km,
                "walking_time_min": rec.walking_time_min,
                "features": rec.features
            }
            for rec in recommendations
        ]
    }

if __name__ == "__main__":
    # Test the MCP service
    service = MCPLocationService()
    
    test_queries = [
        "Find parking near Union Square",
        "I need parking at 123 Market Street",
        "Where can I park close to Chinatown?",
        "Parking options near Financial District"
    ]
    
    print("🧪 Testing MCP Location Service")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        location = service.extract_location_from_query(query)
        if location:
            print(f"✅ Found: {location.name} at ({location.latitude}, {location.longitude})")
        else:
            print("❌ No location found")
