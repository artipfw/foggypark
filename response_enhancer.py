#!/usr/bin/env python3
"""
Response Enhancer - Adds Google Maps links to parking responses
"""

import re
import urllib.parse
from typing import Dict, List
import json
import os

class ParkingResponseEnhancer:
    """Enhances parking responses by adding Google Maps links to addresses."""
    
    def __init__(self):
        self.data_file = "sample/datav3.json"
        self.parking_data = self._load_parking_data()
        self.address_cache = self._build_address_cache()
    
    def _load_parking_data(self) -> List[Dict]:
        """Load parking data from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                return data.get("garages", [])
            return []
        except Exception as e:
            print(f"Error loading parking data: {e}")
            return []
    
    def _build_address_cache(self) -> Dict[str, str]:
        """Build a cache of garage names to addresses for quick lookup."""
        cache = {}
        for garage in self.parking_data:
            name = garage.get('name', '').strip()
            address = garage.get('address', '').strip()
            if name and address:
                cache[name.lower()] = address
        return cache
    
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
    
    def _extract_addresses_from_response(self, response: str) -> List[str]:
        """Extract potential addresses from the response text."""
        addresses = []
        
        # Pattern 1: Street addresses (number + street name + street type)
        street_pattern = r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Place|Pl)\b'
        street_matches = re.findall(street_pattern, response, re.IGNORECASE)
        addresses.extend(street_matches)
        
        # Pattern 2: Known garage names from our data (exact match)
        for garage_name, garage_address in self.address_cache.items():
            if garage_name in response.lower():
                addresses.append(garage_address)
        
        # Pattern 3: Partial garage name matching (for cases like "8th Aveclement Lot")
        response_words = response.lower().split()
        for garage_name, garage_address in self.address_cache.items():
            garage_words = garage_name.split()
            # Check if any significant words from garage name appear in response
            if len(garage_words) >= 2:
                matches = sum(1 for word in garage_words if word in response_words)
                if matches >= 2:  # At least 2 words match
                    addresses.append(garage_address)
        
        # Pattern 4: Look for lot/garage patterns with street names
        lot_pattern = r'([A-Za-z]+(?:/[A-Za-z]+)*)\s+(?:Lot|Garage)'
        lot_matches = re.findall(lot_pattern, response, re.IGNORECASE)
        for match in lot_matches:
            # Try to find corresponding address in our data
            for garage_name, garage_address in self.address_cache.items():
                if match.lower() in garage_name.lower():
                    addresses.append(garage_address)
                    break
        
        # Pattern 5: Area names that can be mapped
        area_addresses = {
            'union square': 'Union Square, San Francisco, CA',
            'financial district': 'Financial District, San Francisco, CA',
            'chinatown': 'Chinatown, San Francisco, CA',
            'soma': 'SOMA, San Francisco, CA',
            'mission bay': 'Mission Bay, San Francisco, CA',
            'embarcadero': 'Embarcadero, San Francisco, CA',
            'north beach': 'North Beach, San Francisco, CA',
            'castro': 'Castro District, San Francisco, CA',
            'marina district': 'Marina District, San Francisco, CA',
            'nob hill': 'Nob Hill, San Francisco, CA',
            'russian hill': 'Russian Hill, San Francisco, CA',
            'pacific heights': 'Pacific Heights, San Francisco, CA',
            'downtown': 'Downtown San Francisco, CA',
            'downtown sf': 'Downtown San Francisco, CA'
        }
        
        response_lower = response.lower()
        for area, area_address in area_addresses.items():
            if area in response_lower:
                addresses.append(area_address)
        
        return list(set(addresses))  # Remove duplicates
    
    def enhance_response(self, response: str) -> str:
        """Enhance response by adding Google Maps links to detected addresses."""
        if not response:
            return response
        
        enhanced_response = response
        addresses = self._extract_addresses_from_response(response)
        
        # Add Google Maps links for detected addresses
        for address in addresses:
            maps_link = self._create_google_maps_link(address)
            if maps_link:
                # Create HTML link
                html_link = f'<a href="{maps_link}" target="_blank">{address}</a>'
                
                # Replace the address in the response with the linked version
                # Use word boundaries to avoid partial matches
                pattern = re.escape(address)
                enhanced_response = re.sub(
                    f'\\b{pattern}\\b', 
                    html_link, 
                    enhanced_response, 
                    flags=re.IGNORECASE
                )
        
        return enhanced_response
    
    def add_maps_section(self, response: str) -> str:
        """Add a maps section at the end of parking responses."""
        if not any(word in response.lower() for word in ['parking', 'garage', 'lot', 'address']):
            return response
        
        addresses = self._extract_addresses_from_response(response)
        
        # If no specific addresses found, add general parking search links
        if not addresses:
            if any(word in response.lower() for word in ['cheapest', 'affordable', 'budget', 'cheap']):
                addresses = ['Affordable Parking San Francisco, CA']
            elif 'downtown' in response.lower():
                addresses = ['Downtown San Francisco Parking']
            elif any(area in response.lower() for area in ['union square', 'financial district', 'soma']):
                # Extract the area mentioned
                for area in ['union square', 'financial district', 'soma', 'mission bay']:
                    if area in response.lower():
                        addresses.append(f"{area.title()} Parking, San Francisco, CA")
            else:
                addresses = ['San Francisco Parking Garages']
        
        if not addresses:
            return response
        
        maps_section = "\n\n**🗺️ Quick Maps Access:**\n"
        for i, address in enumerate(addresses[:5], 1):  # Limit to 5 addresses
            maps_link = self._create_google_maps_link(address)
            if maps_link:
                maps_section += f"{i}. [📍 {address}]({maps_link})\n"
        
        return response + maps_section
