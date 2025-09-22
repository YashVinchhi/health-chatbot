import httpx
import logging
from typing import Dict, List, Optional, Any
from config import settings
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class IndiaHealthDataService:
    """Service to fetch real Indian health data from government and local APIs"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.covid19_india_base = "https://api.covid19india.org"
        self.data_gov_in_base = "https://api.data.gov.in"

    async def get_covid_india_data(self, state: str = "India") -> Dict[str, Any]:
        """Get COVID-19 data for India from covid19india.org API (free)"""
        try:
            url = f"{self.covid19_india_base}/data.json"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()

                # Extract state-specific or national data
                if state.lower() == "india":
                    # National data
                    statewise = data.get("statewise", [])
                    india_data = next((item for item in statewise if item.get("state") == "Total"), {})
                else:
                    # State-specific data
                    statewise = data.get("statewise", [])
                    india_data = next((item for item in statewise if item.get("state").lower() == state.lower()), {})

                if india_data:
                    return {
                        "success": True,
                        "data": {
                            "state": india_data.get("state", "India"),
                            "confirmed": int(india_data.get("confirmed", 0)),
                            "active": int(india_data.get("active", 0)),
                            "recovered": int(india_data.get("recovered", 0)),
                            "deaths": int(india_data.get("deaths", 0)),
                            "delta_confirmed": int(india_data.get("deltaconfirmed", 0)),
                            "delta_deaths": int(india_data.get("deltadeaths", 0)),
                            "last_updated": india_data.get("lastupdatedtime", ""),
                            "state_notes": india_data.get("statenotes", "")
                        }
                    }
        except Exception as e:
            logger.error(f"Error fetching COVID India data: {e}")

        return {"success": False, "error": "Unable to fetch COVID-19 data for India"}

    async def get_vaccination_india_data(self) -> Dict[str, Any]:
        """Get vaccination data for India"""
        try:
            url = f"{self.covid19_india_base}/v4/min/data.min.json"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                india_data = data.get("TT", {})  # TT = Total (India)

                return {
                    "success": True,
                    "data": {
                        "total_vaccinated": india_data.get("total", {}).get("vaccinated", 0),
                        "total_doses": india_data.get("total", {}).get("vaccinated1", 0) + india_data.get("total", {}).get("vaccinated2", 0),
                        "first_dose": india_data.get("total", {}).get("vaccinated1", 0),
                        "second_dose": india_data.get("total", {}).get("vaccinated2", 0),
                        "precaution_dose": india_data.get("total", {}).get("precautiondose", 0),
                        "today_vaccinated": india_data.get("delta", {}).get("vaccinated", 0)
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching vaccination data: {e}")

        return {"success": False, "error": "Unable to fetch vaccination data"}

    async def get_indian_health_schemes(self) -> Dict[str, Any]:
        """Get information about Indian government health schemes"""
        schemes = [
            {
                "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
                "description": "World's largest health insurance scheme providing coverage up to ₹5 lakh per family",
                "beneficiaries": "10.74 crore+ families",
                "coverage": "₹5 lakh per family per year",
                "helpline": "14555"
            },
            {
                "name": "Janani Suraksha Yojana (JSY)",
                "description": "Safe motherhood intervention for reducing maternal and neonatal mortality",
                "beneficiaries": "Pregnant women from BPL families",
                "benefits": "Cash assistance for institutional delivery",
                "helpline": "104"
            },
            {
                "name": "Mission Indradhanush",
                "description": "Immunization program to achieve full immunization coverage",
                "target": "Children under 2 years and pregnant women",
                "vaccines": "12 vaccine-preventable diseases",
                "helpline": "1075"
            },
            {
                "name": "Rashtriya Swasthya Bima Yojana (RSBY)",
                "description": "Health insurance scheme for BPL families",
                "coverage": "₹30,000 per family per year",
                "beneficiaries": "BPL families",
                "helpline": "1800-11-1204"
            }
        ]

        return {
            "success": True,
            "data": schemes
        }

    async def get_indian_emergency_contacts(self, state: str = "national") -> Dict[str, Any]:
        """Get India-specific emergency contacts"""

        national_contacts = {
            "medical_emergency": "102",
            "police": "100",
            "fire": "101",
            "women_helpline": "1091",
            "child_helpline": "1098",
            "senior_citizen_helpline": "14567",
            "covid_helpline": "1075",
            "mental_health_helpline": "9152987821"
        }

        state_helplines = {
            "delhi": {
                "health_helpline": "011-22307145",
                "covid_helpline": "011-22307145",
                "ambulance": "102"
            },
            "maharashtra": {
                "health_helpline": "020-26127394",
                "covid_helpline": "020-26127394",
                "ambulance": "102"
            },
            "karnataka": {
                "health_helpline": "080-23212757",
                "covid_helpline": "080-23212757",
                "ambulance": "102"
            },
            "tamil nadu": {
                "health_helpline": "044-24335253",
                "covid_helpline": "044-24335253",
                "ambulance": "102"
            },
            "gujarat": {
                "health_helpline": "079-26301400",
                "covid_helpline": "079-26301400",
                "ambulance": "102"
            },
            "west bengal": {
                "health_helpline": "033-23412600",
                "covid_helpline": "1800-313-444222",
                "ambulance": "102"
            },
            "uttar pradesh": {
                "health_helpline": "0522-2237735",
                "covid_helpline": "18001805145",
                "ambulance": "102"
            }
        }

        result = {
            "national": national_contacts,
            "state_specific": state_helplines.get(state.lower(), {})
        }

        return {
            "success": True,
            "data": result
        }

    async def get_indian_hospitals_nearby(self, city: str = "delhi") -> Dict[str, Any]:
        """Get list of major hospitals in Indian cities"""

        hospital_data = {
            "delhi": [
                {"name": "AIIMS Delhi", "type": "Government", "speciality": "Multi-specialty", "phone": "011-26588500"},
                {"name": "Apollo Hospital Delhi", "type": "Private", "speciality": "Multi-specialty", "phone": "011-26925858"},
                {"name": "Fortis Hospital Delhi", "type": "Private", "speciality": "Multi-specialty", "phone": "011-42776222"},
                {"name": "Max Healthcare Delhi", "type": "Private", "speciality": "Multi-specialty", "phone": "011-26925050"}
            ],
            "mumbai": [
                {"name": "Tata Memorial Hospital", "type": "Government", "speciality": "Cancer", "phone": "022-24177000"},
                {"name": "Kokilaben Hospital", "type": "Private", "speciality": "Multi-specialty", "phone": "022-42696969"},
                {"name": "Nanavati Hospital", "type": "Private", "speciality": "Multi-specialty", "phone": "022-26262626"},
                {"name": "Lilavati Hospital", "type": "Private", "speciality": "Multi-specialty", "phone": "022-26757000"}
            ],
            "bangalore": [
                {"name": "Manipal Hospital", "type": "Private", "speciality": "Multi-specialty", "phone": "080-25023200"},
                {"name": "Apollo Hospital Bangalore", "type": "Private", "speciality": "Multi-specialty", "phone": "080-26304050"},
                {"name": "Fortis Hospital Bangalore", "type": "Private", "speciality": "Multi-specialty", "phone": "080-66214444"},
                {"name": "NIMHANS", "type": "Government", "speciality": "Neurosciences & Mental Health", "phone": "080-26995000"}
            ]
        }

        return {
            "success": True,
            "data": hospital_data.get(city.lower(), []),
            "city": city
        }

    async def get_indian_weather_health_advisory(self, city: str = "delhi") -> Dict[str, Any]:
        """Get weather-related health advisory for Indian cities"""
        try:
            if not settings.openweather_api_key:
                return self._get_seasonal_health_advisory()

            # Get weather data for Indian city
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": f"{city},IN",  # IN for India
                "appid": settings.openweather_api_key,
                "units": "metric"
            }

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                aqi_advisory = await self._get_air_quality_advisory(city)

                advisory = self._generate_india_weather_health_advisory(temp, humidity, city)

                return {
                    "success": True,
                    "data": {
                        "city": data["name"],
                        "temperature": temp,
                        "humidity": humidity,
                        "weather_advisory": advisory,
                        "air_quality_advisory": aqi_advisory,
                        "monsoon_advisory": self._get_monsoon_advisory()
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching weather advisory: {e}")

        return self._get_seasonal_health_advisory()

    def _generate_india_weather_health_advisory(self, temp: float, humidity: float, city: str) -> List[str]:
        """Generate India-specific health advisory based on weather"""
        advisories = []

        # Temperature-based advisories
        if temp > 40:
            advisories.append("🌡️ Extreme heat warning - Risk of heat stroke. Stay indoors, drink ORS")
        elif temp > 35:
            advisories.append("☀️ High temperature - Avoid outdoor activities 11 AM - 4 PM")
        elif temp < 10:
            advisories.append("🧊 Cold wave - Protect against hypothermia, especially elderly")

        # Humidity-based advisories
        if humidity > 85:
            advisories.append("💧 Very high humidity - Risk of heat rash and fungal infections")
        elif humidity < 30:
            advisories.append("🏜️ Low humidity - Risk of respiratory issues, use humidifier")

        # City-specific advisories
        if city.lower() in ["delhi", "gurgaon", "noida"]:
            advisories.append("🏭 Air pollution advisory - Use N95 masks outdoors")
        elif city.lower() in ["mumbai", "kolkata"]:
            advisories.append("🌊 Coastal city - Watch for monsoon-related diseases")

        return advisories if advisories else ["☀️ Pleasant weather - Good for outdoor activities"]

    async def _get_air_quality_advisory(self, city: str) -> str:
        """Get air quality advisory for Indian cities"""
        # This would integrate with actual AQI APIs
        aqi_advisories = {
            "delhi": "AQI: Poor - Use N95 masks, avoid outdoor exercise",
            "mumbai": "AQI: Moderate - Sensitive people should limit outdoor activities",
            "bangalore": "AQI: Good - Safe for outdoor activities",
            "kolkata": "AQI: Moderate - Use masks during peak traffic hours"
        }

        return aqi_advisories.get(city.lower(), "Check local AQI before outdoor activities")

    def _get_monsoon_advisory(self) -> str:
        """Get monsoon-related health advisory"""
        current_month = datetime.now().month

        if current_month in [6, 7, 8, 9]:  # Monsoon season
            return "🌧️ Monsoon season - Prevent dengue, malaria. Use mosquito nets, avoid waterlogging"
        elif current_month in [10, 11]:  # Post-monsoon
            return "🦟 Post-monsoon - Peak season for vector-borne diseases. Use repellents"
        else:
            return "☀️ Dry season - Stay hydrated, protect from dust"

    def _get_seasonal_health_advisory(self) -> Dict[str, Any]:
        """Fallback seasonal health advisory"""
        return {
            "success": True,
            "data": {
                "city": "General India",
                "advisory": [
                    "Stay hydrated - Drink 8-10 glasses of water daily",
                    "Protect from air pollution - Use masks in polluted areas",
                    "Seasonal diseases - Be aware of dengue, malaria during monsoons"
                ]
            }
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
india_health_service = IndiaHealthDataService()
