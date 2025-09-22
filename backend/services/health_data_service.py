import httpx
import logging
from typing import Dict, List, Optional, Any
from config import settings
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

            # Fallback to curated vaccination data
            schedules = {
                "adult": [
                    {
                        "vaccine": "COVID-19",
                        "schedule": "Primary series + annual boosters",
                        "priority": "High",
                        "notes": "Recommended for all adults"
                    },
                    {
                        "vaccine": "Influenza (Flu)",
                        "schedule": "Annual vaccination",
                        "priority": "High",
                        "notes": "Recommended every fall season"
                    },
                    {
                        "vaccine": "Tdap (Tetanus, Diphtheria, Pertussis)",
                        "schedule": "Every 10 years",
                        "priority": "Medium",
                        "notes": "Booster for adult protection"
                    }
                ],
                "child": [
                    {
                        "vaccine": "MMR (Measles, Mumps, Rubella)",
                        "schedule": "12-15 months, 4-6 years",
                        "priority": "High",
                        "notes": "Part of routine childhood immunization"
                    },
                    {
                        "vaccine": "DTaP (Diphtheria, Tetanus, Pertussis)",
                        "schedule": "2, 4, 6, 15-18 months, 4-6 years",
                        "priority": "High",
                        "notes": "Essential childhood protection"
                    }
                ]
            }

            return {
                "success": True,
                "data": schedules.get(age_group, schedules["adult"])
            }

        except Exception as e:
            logger.error(f"Error fetching vaccination schedule: {e}")
            return {"success": False, "error": "Unable to fetch vaccination data"}

    async def get_health_news(self, query: str = "health alert") -> Dict[str, Any]:
        """Get health-related news from NewsAPI"""
        try:
            if not settings.news_api_key:
                return self._get_mock_health_news()

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": settings.news_api_key,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 5
            }

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                articles = []
                for article in data.get("articles", [])[:3]:
                    articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "published": article.get("publishedAt"),
                        "source": article.get("source", {}).get("name")
                    })

                return {"success": True, "data": articles}

        except Exception as e:
            logger.error(f"Error fetching health news: {e}")

        return self._get_mock_health_news()

    def _get_mock_health_news(self) -> Dict[str, Any]:
        """Fallback health news when API is not available"""
        return {
            "success": True,
            "data": [
                {
                    "title": "CDC Updates Vaccination Guidelines",
                    "description": "Latest recommendations for COVID-19 and flu vaccinations",
                    "source": "CDC",
                    "published": datetime.now().isoformat()
                },
                {
                    "title": "Seasonal Health Advisory",
                    "description": "Preparing for flu season - prevention tips",
                    "source": "WHO",
                    "published": datetime.now().isoformat()
                }
            ]
        }

    async def get_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """Get drug information from FDA API"""
        try:
            # FDA OpenFDA API - free to use
            url = f"{settings.fda_base_url}/drug/label.json"
            params = {
                "search": f"openfda.brand_name:{drug_name}",
                "limit": 1
            }

            if settings.fda_api_key:
                params["api_key"] = settings.fda_api_key

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    return {
                        "success": True,
                        "data": {
                            "brand_name": result.get("openfda", {}).get("brand_name", ["Unknown"])[0],
                            "generic_name": result.get("openfda", {}).get("generic_name", ["Unknown"])[0],
                            "purpose": result.get("purpose", ["Information not available"])[0] if result.get("purpose") else "Information not available",
                            "warnings": result.get("warnings", ["Please consult healthcare provider"])[0] if result.get("warnings") else "Please consult healthcare provider"
                        }
                    }

        except Exception as e:
            logger.error(f"Error fetching drug information: {e}")

        return {
            "success": False,
            "error": "Unable to fetch drug information. Please consult a healthcare professional."
        }

    async def get_weather_health_advisory(self, location: str = "global") -> Dict[str, Any]:
        """Get weather-related health advisories"""
        try:
            if not settings.openweather_api_key:
                return self._get_mock_weather_advisory()

            # Get current weather data
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

                # Generate health advisory based on weather
                advisory = self._generate_weather_health_advisory(temp, humidity)

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
            logger.error(f"Error fetching weather advisory: {e}")

        return self._get_mock_weather_advisory()

    def _generate_weather_health_advisory(self, temp: float, humidity: float) -> List[str]:
        """Generate health advisory based on weather conditions"""
        advisories = []

        if temp > 30:
            advisories.append("🌡️ High temperature - Stay hydrated and avoid prolonged sun exposure")
        elif temp < 5:
            advisories.append("🧊 Cold weather - Dress warmly and watch for hypothermia symptoms")

        if humidity > 80:
            advisories.append("💧 High humidity - Take breaks in air-conditioned spaces")
        elif humidity < 30:
            advisories.append("🏜️ Low humidity - Use moisturizers and stay hydrated")

        if not advisories:
            advisories.append("☀️ Pleasant weather conditions - Great for outdoor activities")

        return advisories

    def _get_mock_weather_advisory(self) -> Dict[str, Any]:
        """Fallback weather advisory"""
        return {
            "success": True,
            "data": {
                "location": "General",
                "advisory": ["Stay hydrated and dress appropriately for the weather"]
            }
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
health_data_service = HealthDataService()
