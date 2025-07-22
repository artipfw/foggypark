from langchain.llms.base import LLM
from typing import Optional, List
from dotenv import load_dotenv
import requests
import os
from parking_knowledge import ParkingKnowledgeBase
from response_enhancer import ParkingResponseEnhancer

class HypermodeLLM(LLM):
    """Custom LLM wrapper with dynamic parking knowledge fallback."""
    load_dotenv()
    api_url: str = os.getenv("HYPERMODE_BASE_URL", "https://models.hypermode.host/v1")
    model: str = os.getenv("HYPERMODE_MODEL", "gpt-4o")
    api_key: str = os.getenv("HYPERMODE_API_KEY")
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "hypermode"

    def _get_knowledge_base(self) -> ParkingKnowledgeBase:
        """Get knowledge base instance."""
        if not hasattr(self, '_kb_instance'):
            self._kb_instance = ParkingKnowledgeBase()
        return self._kb_instance

    def _get_response_enhancer(self) -> ParkingResponseEnhancer:
        """Get response enhancer instance."""
        if not hasattr(self, '_enhancer_instance'):
            self._enhancer_instance = ParkingResponseEnhancer()
        return self._enhancer_instance

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if not self.api_key:
            return self._get_dynamic_fallback_response(prompt, "API key not found")

        # Try OpenAI API directly
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant specializing in San Francisco parking information."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": 512
            }

            response = requests.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                response_json = response.json()
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    message = response_json["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        # Enhance the response with Google Maps links
                        enhancer = self._get_response_enhancer()
                        enhanced_content = enhancer.add_maps_section(content)
                        return enhanced_content

            return self._get_dynamic_fallback_response(prompt, f"API error: {response.status_code}")

        except Exception as e:
            return self._get_dynamic_fallback_response(prompt, str(e))

    def _get_dynamic_fallback_response(self, prompt: str, error_msg: str) -> str:
        """Provide dynamic fallback responses based on actual parking data."""

        prompt_lower = prompt.lower()

        try:
            knowledge_base = self._get_knowledge_base()

            # Analyze prompt and route to appropriate knowledge base method
            if any(word in prompt_lower for word in ['cheap', 'affordable', 'low cost', 'budget', 'cheapest']):
                response = knowledge_base.get_affordable_parking()

            elif any(word in prompt_lower for word in ['union square', 'downtown', 'financial district', 'soma', 'mission bay']):
                # Extract area keywords
                area_keywords = []
                areas = ['union square', 'downtown', 'financial district', 'soma', 'mission bay', 'embarcadero', 'chinatown', 'nob hill']
                for area in areas:
                    if area in prompt_lower:
                        area_keywords.extend(area.split())

                if not area_keywords:
                    # Try to extract other location words
                    words = prompt_lower.split()
                    location_words = [w for w in words if len(w) > 3 and w not in ['parking', 'garage', 'near', 'find', 'show', 'where']]
                    area_keywords = location_words[:3]  # Take first few meaningful words

                response = knowledge_base.get_area_parking(area_keywords)

            elif any(word in prompt_lower for word in ['24/7', 'always open', 'late night', 'overnight', '24 hours', 'all night']):
                response = knowledge_base.get_24_7_parking()

            elif any(word in prompt_lower for word in ['ev', 'electric', 'charging', 'tesla', 'charge']):
                response = knowledge_base.get_ev_parking()

            elif any(word in prompt_lower for word in ['features', 'amenities', 'covered', 'security', 'services']):
                response = knowledge_base.get_features_info()

            else:
                # General parking information
                response = knowledge_base.get_general_info()

            # Add technical note if there was an API error
            if "API key not found" not in error_msg:
                response += f"\n\n*Note: Currently using offline data due to API connectivity issues.*"

            return response

        except Exception as e:
            # Final fallback if knowledge base fails
            return f"""I'm experiencing technical difficulties, but I can still help with parking information!

**San Francisco Parking Quick Guide:**

**Budget Options:** Look for garages in SOMA and Mission Bay areas
**Downtown:** Union Square and Financial District have premium pricing
**24/7 Access:** Most downtown garages offer round-the-clock access
**EV Charging:** Many newer facilities include charging stations

**General Tips:**
- Compare rates using parking apps
- Look for early bird specials
- Check for validation at nearby businesses
- Consider public transit for longer stays

Please try your question again, or ask about specific neighborhoods!

*Technical note: {error_msg} | Knowledge base error: {str(e)}*"""
