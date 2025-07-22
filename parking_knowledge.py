import os
import json
import weaviate
from typing import List, Dict, Optional
from dotenv import load_dotenv
import contextlib
import urllib.parse

load_dotenv()

class ParkingKnowledgeBase:
    """Dynamic parking knowledge base that uses actual data from files and Weaviate."""
    
    def __init__(self):
        self.data_file = "sample/datav3.json"
        self.parking_data = self._load_parking_data()
        
    def _create_google_maps_link(self, address: str) -> str:
        """Create a Google Maps link for the given address."""
        if not address or address == 'Address not available':
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
        if not address or address == 'Address not available':
            return "📍 Address not available"
        
        maps_link = self._create_google_maps_link(address)
        # Use HTML link format for better Streamlit compatibility
        return f'📍 <a href="{maps_link}" target="_blank">{address}</a>'
    
    def _format_address_with_markdown_link(self, address: str) -> str:
        """Format address with markdown link as fallback."""
        if not address or address == 'Address not available':
            return "📍 Address not available"
        
        maps_link = self._create_google_maps_link(address)
        return f"📍 [{address}]({maps_link})"
    
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
    
    @contextlib.contextmanager
    def _get_weaviate_client(self):
        """Context manager for Weaviate client to ensure proper cleanup."""
        client = None
        try:
            client = weaviate.connect_to_local(
                host="127.0.0.1",
                headers={"X-OpenAI-Api-Key": os.environ.get("HYPERMODE_API_KEY")} if os.environ.get("HYPERMODE_API_KEY") else None
            )
            if client and client.is_ready():
                yield client
            else:
                yield None
        except Exception as e:
            print(f"Weaviate connection error: {e}")
            yield None
        finally:
            if client:
                try:
                    client.close()
                except:
                    pass
    
    def _search_weaviate(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Weaviate for relevant parking information."""
        try:
            with self._get_weaviate_client() as client:
                if not client:
                    return []
                
                collection = client.collections.get("Chunk")
                response = collection.query.near_text(
                    query=query,
                    limit=limit
                )
                
                results = []
                for obj in response.objects:
                    results.append({
                        'title': obj.properties.get('title', ''),
                        'content': obj.properties.get('content', ''),
                        'source': obj.properties.get('source', ''),
                        'hourly_rate': obj.properties.get('hourly_rate', 0),
                        'phone': obj.properties.get('phone', ''),
                        'hours': obj.properties.get('hours', '')
                    })
                return results
        except Exception as e:
            print(f"Weaviate search error: {e}")
            return []
    
    def get_affordable_parking(self) -> str:
        """Get information about affordable parking options."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        # Sort by hourly rate and get cheapest options
        affordable_garages = sorted(
            [g for g in self.parking_data if g.get('hourlyRate') and g.get('hourlyRate') > 0],
            key=lambda x: x.get('hourlyRate', 999)
        )[:5]
        
        if not affordable_garages:
            return "No pricing information available at this time."
        
        response = "**Most Affordable Parking Options:**\n\n"
        for garage in affordable_garages:
            name = garage.get('name', 'Unknown')
            rate = garage.get('hourlyRate', 'N/A')
            address = garage.get('address', 'Address not available')
            phone = garage.get('phone', '')
            
            response += f"• **{name}**: ${rate}/hour\n"
            response += f"  {self._format_address_with_link(address)}\n"
            if phone:
                response += f"  📞 {phone}\n"
            response += "\n"
        
        # Add general tips
        response += "**Money-Saving Tips:**\n"
        response += "• Look for early bird specials\n"
        response += "• Check evening and weekend rates\n"
        response += "• Consider monthly parking for regular visits\n"
        
        return response
    
    def get_area_parking(self, area_keywords: List[str]) -> str:
        """Get parking information for specific areas."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        # Search for garages in the specified area
        area_garages = []
        for garage in self.parking_data:
            name = garage.get('name', '').lower()
            address = garage.get('address', '').lower()
            
            if any(keyword.lower() in name or keyword.lower() in address 
                   for keyword in area_keywords):
                area_garages.append(garage)
        
        if not area_garages:
            # Try Weaviate search as fallback
            search_query = " ".join(area_keywords) + " parking garage"
            weaviate_results = self._search_weaviate(search_query)
            if weaviate_results:
                response = f"**Parking near {' '.join(area_keywords).title()}:**\n\n"
                for result in weaviate_results:
                    response += f"• **{result['title']}**\n"
                    response += f"  {result['content']}\n\n"
                return response
            
            return f"No specific parking information found for {' '.join(area_keywords)}. Try searching for nearby landmarks or neighborhoods."
        
        response = f"**Parking in {' '.join(area_keywords).title()} Area:**\n\n"
        for garage in area_garages[:5]:  # Limit to top 5
            name = garage.get('name', 'Unknown')
            rate = garage.get('hourlyRate', 'N/A')
            address = garage.get('address', 'Address not available')
            hours = garage.get('hours', 'Hours not available')
            phone = garage.get('phone', '')
            
            response += f"• **{name}**\n"
            response += f"  💰 ${rate}/hour\n"
            response += f"  {self._format_address_with_link(address)}\n"
            response += f"  🕒 {hours}\n"
            if phone:
                response += f"  📞 {phone}\n"
            response += "\n"
        
        return response
    
    def get_24_7_parking(self) -> str:
        """Get information about 24/7 parking options."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        always_open = []
        for garage in self.parking_data:
            hours = garage.get('hours', '').lower()
            if 'always' in hours or '24' in hours or 'open' in hours:
                always_open.append(garage)
        
        if not always_open:
            return "**24/7 Parking Information:**\n\nMost downtown garages offer 24/7 access. Contact individual garages to confirm hours."
        
        response = "**24/7 Parking Options:**\n\n"
        for garage in always_open:
            name = garage.get('name', 'Unknown')
            rate = garage.get('hourlyRate', 'N/A')
            address = garage.get('address', 'Address not available')
            phone = garage.get('phone', '')
            
            response += f"• **{name}**: ${rate}/hour\n"
            response += f"  {self._format_address_with_link(address)}\n"
            if phone:
                response += f"  📞 {phone}\n"
            response += "\n"
        
        return response
    
    def get_ev_parking(self) -> str:
        """Get information about EV charging parking."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        ev_garages = []
        for garage in self.parking_data:
            features = garage.get('features', [])
            if any('ev' in str(feature).lower() or 'electric' in str(feature).lower() or 'charging' in str(feature).lower() 
                   for feature in features):
                ev_garages.append(garage)
        
        response = "**EV Charging Parking Information:**\n\n"
        
        if ev_garages:
            response += "**Garages with EV Charging:**\n"
            for garage in ev_garages:
                name = garage.get('name', 'Unknown')
                rate = garage.get('hourlyRate', 'N/A')
                address = garage.get('address', 'Address not available')
                phone = garage.get('phone', '')
                
                response += f"• **{name}**: ${rate}/hour\n"
                response += f"  {self._format_address_with_link(address)}\n"
                if phone:
                    response += f"  📞 {phone}\n"
                response += "\n"
        
        response += "**General EV Parking Tips:**\n"
        response += "• Many newer garages include EV charging stations\n"
        response += "• Check ChargePoint and EVgo networks\n"
        response += "• Some locations offer free charging with parking\n"
        response += "• Use PlugShare app to find charging locations\n"
        
        return response
    
    def get_features_info(self) -> str:
        """Get information about parking garage features."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        # Analyze features across all garages
        all_features = []
        for garage in self.parking_data:
            features = garage.get('features', [])
            all_features.extend(features)
        
        # Count feature frequency
        feature_counts = {}
        for feature in all_features:
            if feature:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        response = "**Common Parking Garage Features:**\n\n"
        
        if feature_counts:
            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            response += "**Most Common Features:**\n"
            for feature, count in sorted_features[:10]:
                response += f"• {feature} (available at {count} locations)\n"
            response += "\n"
        
        response += "**Standard Amenities:**\n"
        response += "• Covered parking (weather protection)\n"
        response += "• Security cameras and lighting\n"
        response += "• Credit card payment options\n"
        response += "• Attendant services (varies by location)\n"
        
        return response
    
    def get_general_info(self) -> str:
        """Get general parking information."""
        if not self.parking_data:
            return "Unable to load parking data at this time."
        
        # Calculate statistics
        rates = [g.get('hourlyRate', 0) for g in self.parking_data if g.get('hourlyRate') and g.get('hourlyRate') > 0]
        
        response = "**San Francisco Parking Guide:**\n\n"
        
        if rates:
            avg_rate = sum(rates) / len(rates)
            min_rate = min(rates)
            max_rate = max(rates)
            
            response += f"**Pricing Overview:**\n"
            response += f"• Average rate: ${avg_rate:.2f}/hour\n"
            response += f"• Lowest rate: ${min_rate}/hour\n"
            response += f"• Highest rate: ${max_rate}/hour\n"
            response += f"• Total garages: {len(self.parking_data)}\n\n"
        
        response += "**Popular Areas:**\n"
        response += "• **Downtown/Financial District**: Business-focused, higher rates\n"
        response += "• **Union Square**: Central location, premium pricing\n"
        response += "• **SOMA**: Good balance of location and price\n"
        response += "• **Mission Bay**: Newer area, competitive rates\n\n"
        
        response += "**Pro Tips:**\n"
        response += "• Compare rates using parking apps\n"
        response += "• Look for early bird and evening specials\n"
        response += "• Consider validation at nearby businesses\n"
        response += "• Check for event-related rate changes\n"
        
        return response
