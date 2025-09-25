import httpx
import logging
from typing import Dict, List, Optional, Any
from ..config import settings
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthDataService:
    """Service to fetch real health data from various APIs"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_covid_data(self, country: str = "all") -> Dict[str, Any]:
        """Get COVID-19 data from Disease.sh API (free, no key required)"""
        try:
            url = f"{settings.disease_sh_base_url}/{country}"
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": {
                        "country": data.get("country", "Global"),
                        "cases": data.get("cases", 0),
                        "deaths": data.get("deaths", 0),
                        "recovered": data.get("recovered", 0),
                        "active": data.get("active", 0),
                        "critical": data.get("critical", 0),
                        "updated": data.get("updated", 0)
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching COVID data: {e}")

        return {"success": False, "error": "Unable to fetch COVID data"}

    async def get_vaccination_schedule(self, age_group: str = "adult") -> Dict[str, Any]:
        """Get vaccination schedule information"""
        try:
            # Use CDC API if key is available, otherwise return curated data
            if settings.cdc_api_key:
                headers = {"X-API-Key": settings.cdc_api_key}
                # CDC API endpoint for vaccination schedules
                url = f"{settings.cdc_data_base_url}/vaccination-schedules"
                response = await self.client.get(url, headers=headers)
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Error fetching vaccination data from CDC: {e}")

        # Fallback curated vaccination data
        vaccination_data = {
            "adult": [
                {
                    "vaccine": "COVID-19",
                    "schedule": "Initial series + annual boosters",
                    "importance": "High priority for all adults"
                },
                {
                    "vaccine": "Influenza (Flu)",
                    "schedule": "Annual vaccination",
                    "importance": "Recommended for everyone 6 months and older"
                },
                {
                    "vaccine": "Tdap (Tetanus, Diphtheria, Pertussis)",
                    "schedule": "Every 10 years",
                    "importance": "Essential for wound protection"
                }
            ],
            "child": [
                {
                    "vaccine": "MMR (Measles, Mumps, Rubella)",
                    "schedule": "12-15 months, 4-6 years",
                    "importance": "Critical for school entry"
                },
                {
                    "vaccine": "DTaP (Diphtheria, Tetanus, Pertussis)",
                    "schedule": "2, 4, 6, 15-18 months, 4-6 years",
                    "importance": "Essential childhood protection"
                }
            ]
        }

        return {
            "success": True,
            "data": vaccination_data.get(age_group, vaccination_data["adult"])
        }

    async def get_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """Get drug information from FDA OpenFDA API"""
        try:
            url = f"{settings.fda_base_url}/drug/label.json"
            params = {
                "search": f"openfda.generic_name:{drug_name.lower()}"
            }

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    drug_info = results[0]
                    return {
                        "success": True,
                        "data": {
                            "drug_name": drug_name,
                            "generic_name": drug_info.get("openfda", {}).get("generic_name", ["Unknown"])[0],
                            "brand_name": drug_info.get("openfda", {}).get("brand_name", ["Unknown"])[0],
                            "purpose": drug_info.get("purpose", ["Information not available"])[0] if drug_info.get("purpose") else "Information not available",
                            "warnings": drug_info.get("warnings", ["Please consult healthcare provider"])[0] if drug_info.get("warnings") else "Please consult healthcare provider",
                            "dosage": drug_info.get("dosage_and_administration", ["Consult healthcare provider"])[0] if drug_info.get("dosage_and_administration") else "Consult healthcare provider"
                        }
                    }
        except Exception as e:
            logger.error(f"Error fetching drug information: {e}")

        return {"success": False, "error": f"Unable to find information for {drug_name}"}

    async def get_health_news(self, query: str = "health") -> Dict[str, Any]:
        """Get health news from NewsAPI"""
        try:
            if not settings.news_api_key:
                return self._get_fallback_health_news()

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": settings.news_api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5
            }

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                articles = []
                for article in data.get("articles", [])[:5]:
                    articles.append({
                        "title": article.get("title", "No title"),
                        "description": article.get("description", "No description"),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "Unknown")
                    })
                return {"success": True, "data": articles}
        except Exception as e:
            logger.error(f"Error fetching health news: {e}")

        return self._get_fallback_health_news()

    def _get_fallback_health_news(self) -> Dict[str, Any]:
        """Fallback health news when API is not available"""
        fallback_news = [
            {
                "title": "WHO Updates Global Health Guidelines",
                "description": "World Health Organization releases new guidelines for preventive healthcare",
                "url": "https://who.int",
                "published_at": datetime.now().isoformat(),
                "source": "WHO"
            },
            {
                "title": "Seasonal Flu Vaccination Campaign",
                "description": "Health authorities recommend annual flu vaccination for all eligible individuals",
                "url": "https://cdc.gov",
                "published_at": datetime.now().isoformat(),
                "source": "CDC"
            }
        ]
        return {"success": True, "data": fallback_news}

    async def get_weather_health_advisory(self, location: str) -> Dict[str, Any]:
        """Get weather-based health advisory"""
        try:
            if not settings.openweather_api_key:
                return self._get_general_weather_advisory()

            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": settings.openweather_api_key,
                "units": "metric"
            }

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]

                advisory = self._generate_health_advisory(temp, humidity)

                return {
                    "success": True,
                    "data": {
                        "location": data["name"],
                        "temperature": temp,
                        "humidity": humidity,
                        "advisory": advisory
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")

        return self._get_general_weather_advisory()

    def _generate_health_advisory(self, temp: float, humidity: float) -> List[str]:
        """Generate health advisory based on weather conditions"""
        advisories = []

        if temp > 35:
            advisories.append("🌡️ High temperature - Stay hydrated and avoid prolonged sun exposure")
        elif temp < 5:
            advisories.append("🧊 Low temperature - Dress warmly and protect against hypothermia")

        if humidity > 80:
            advisories.append("💧 High humidity - Be aware of heat index and potential for mold growth")
        elif humidity < 30:
            advisories.append("🏜️ Low humidity - Use moisturizer and stay hydrated")

        if not advisories:
            advisories.append("☀️ Pleasant weather conditions - Good for outdoor activities")

        return advisories

    def _get_general_weather_advisory(self) -> Dict[str, Any]:
        """Fallback weather advisory"""
        return {
            "success": True,
            "data": {
                "location": "General",
                "advisory": ["Stay hydrated", "Dress appropriately for weather", "Protect yourself from extreme conditions"]
            }
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
health_data_service = HealthDataService()
