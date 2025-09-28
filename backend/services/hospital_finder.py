"""
Hospital Finder Service with Location-Based Search
Supports Google Maps API and Indian alternatives like MapMyIndia
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Tuple
import logging
import os
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)

class HospitalFinderService:
    """
    Comprehensive hospital finder service with multiple API support
    """

    def __init__(self):
        # API Keys from environment
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.mapmyindia_api_key = os.getenv("MAPMYINDIA_API_KEY")

        # Fallback hospital database
        self.hospital_database = self._load_hospital_database()
        self.emergency_services = self._load_emergency_services()

    def _load_hospital_database(self) -> Dict:
        """Load comprehensive hospital database for major Indian cities"""
        return {
            "Delhi": [
                {
                    "name": "All India Institute of Medical Sciences (AIIMS)",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma", "Cardiology", "Neurology"],
                    "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi - 110029",
                    "phone": "011-26588500",
                    "emergency": "011-26588663",
                    "ambulance": "011-26594040",
                    "coordinates": {"lat": 28.5665, "lng": 77.2072},
                    "24x7": True,
                    "rating": 4.2,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank", "Pharmacy"]
                },
                {
                    "name": "Safdarjung Hospital",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma"],
                    "address": "Ansari Nagar West, New Delhi - 110029",
                    "phone": "011-26165060",
                    "emergency": "011-26165000",
                    "coordinates": {"lat": 28.5745, "lng": 77.2064},
                    "24x7": True,
                    "rating": 3.8,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank"]
                },
                {
                    "name": "Apollo Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Oncology", "Neurology"],
                    "address": "Mathura Road, Sarita Vihar, New Delhi - 110076",
                    "phone": "011-26925858",
                    "emergency": "011-26925801",
                    "coordinates": {"lat": 28.5355, "lng": 77.2814},
                    "24x7": True,
                    "rating": 4.5,
                    "services": ["Emergency", "ICU", "Cardiac Center", "Cancer Center"]
                },
                {
                    "name": "Max Super Speciality Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Orthopedics", "Neurology"],
                    "address": "1, Press Enclave Road, Saket, New Delhi - 110017",
                    "phone": "011-26515050",
                    "emergency": "011-26515090",
                    "coordinates": {"lat": 28.5244, "lng": 77.2066},
                    "24x7": True,
                    "rating": 4.3,
                    "services": ["Emergency", "ICU", "Cardiac Center", "Joint Replacement"]
                }
            ],
            "Mumbai": [
                {
                    "name": "King Edward Memorial Hospital (KEM)",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma"],
                    "address": "Acharya Donde Marg, Parel, Mumbai - 400012",
                    "phone": "022-24129884",
                    "emergency": "022-24143071",
                    "coordinates": {"lat": 19.0176, "lng": 72.8448},
                    "24x7": True,
                    "rating": 4.0,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank"]
                },
                {
                    "name": "Tata Memorial Hospital",
                    "type": "Government",
                    "specialties": ["Oncology", "Cancer Treatment", "Research"],
                    "address": "Dr. E Borges Road, Parel, Mumbai - 400012",
                    "phone": "022-24177000",
                    "emergency": "022-24177000",
                    "coordinates": {"lat": 19.0144, "lng": 72.8479},
                    "24x7": True,
                    "rating": 4.6,
                    "services": ["Cancer Treatment", "ICU", "Radiotherapy", "Chemotherapy"]
                },
                {
                    "name": "Kokilaben Dhirubhai Ambani Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Neurology", "Oncology"],
                    "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bungalows, Andheri West, Mumbai - 400053",
                    "phone": "022-42696969",
                    "emergency": "022-42696911",
                    "coordinates": {"lat": 19.1367, "lng": 72.8267},
                    "24x7": True,
                    "rating": 4.4,
                    "services": ["Emergency", "ICU", "Cardiac Center", "Cancer Center"]
                }
            ],
            "Bangalore": [
                {
                    "name": "Victoria Hospital (BMCRI)",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma"],
                    "address": "Fort Road, Chamarajpet, Bangalore - 560002",
                    "phone": "080-26700435",
                    "emergency": "080-26700200",
                    "coordinates": {"lat": 12.9581, "lng": 77.5753},
                    "24x7": True,
                    "rating": 3.9,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank"]
                },
                {
                    "name": "Apollo Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Neurology", "Orthopedics"],
                    "address": "154/11, Opposite IIM-B, Bannerghatta Road, Bangalore - 560076",
                    "phone": "080-26304050",
                    "emergency": "080-26304080",
                    "coordinates": {"lat": 12.9072, "lng": 77.5953},
                    "24x7": True,
                    "rating": 4.3,
                    "services": ["Emergency", "ICU", "Cardiac Center", "Neurology Center"]
                },
                {
                    "name": "Manipal Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Oncology", "Neurology"],
                    "address": "98, Rustom Bagh, Airport Road, Bangalore - 560017",
                    "phone": "080-25024444",
                    "emergency": "080-25024488",
                    "coordinates": {"lat": 12.9698, "lng": 77.6469},
                    "24x7": True,
                    "rating": 4.2,
                    "services": ["Emergency", "ICU", "Cardiac Center", "Cancer Center"]
                }
            ],
            "Chennai": [
                {
                    "name": "Rajiv Gandhi Government General Hospital",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma"],
                    "address": "Park Town, Chennai - 600003",
                    "phone": "044-25816500",
                    "emergency": "044-25816789",
                    "coordinates": {"lat": 13.0827, "lng": 80.2707},
                    "24x7": True,
                    "rating": 3.7,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank"]
                },
                {
                    "name": "Apollo Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Neurology", "Transplant"],
                    "address": "21, Greams Lane, Off Greams Road, Chennai - 600006",
                    "phone": "044-28296000",
                    "emergency": "044-28296161",
                    "coordinates": {"lat": 13.0615, "lng": 80.2539},
                    "24x7": True,
                    "rating": 4.4,
                    "services": ["Emergency", "ICU", "Heart Institute", "Transplant Center"]
                }
            ],
            "Hyderabad": [
                {
                    "name": "Gandhi Hospital",
                    "type": "Government",
                    "specialties": ["Multi-specialty", "Emergency", "Trauma"],
                    "address": "Secunderabad, Hyderabad - 500003",
                    "phone": "040-27505050",
                    "emergency": "040-27505000",
                    "coordinates": {"lat": 17.4474, "lng": 78.4482},
                    "24x7": True,
                    "rating": 3.8,
                    "services": ["Emergency", "ICU", "Trauma Center", "Blood Bank"]
                },
                {
                    "name": "Apollo Hospital",
                    "type": "Private",
                    "specialties": ["Multi-specialty", "Cardiology", "Neurology", "Oncology"],
                    "address": "Jubilee Hills, Hyderabad - 500033",
                    "phone": "040-23607777",
                    "emergency": "040-23608888",
                    "coordinates": {"lat": 17.4239, "lng": 78.4738},
                    "24x7": True,
                    "rating": 4.5,
                    "services": ["Emergency", "ICU", "Heart Institute", "Cancer Center"]
                }
            ]
        }

    def _load_emergency_services(self) -> Dict:
        """Load emergency services information"""
        return {
            "national": {
                "ambulance": "108",
                "police": "100",
                "fire": "101",
                "disaster_management": "108",
                "women_helpline": "1091",
                "child_helpline": "1098"
            },
            "medical_helplines": {
                "covid_helpline": "1075",
                "health_ministry": "1800-11-4477",
                "ayushman_bharat": "14555",
                "jan_aushadhi": "1800-180-5253"
            },
            "state_ambulance": {
                "Delhi": "102",
                "Mumbai": "102",
                "Bangalore": "102",
                "Chennai": "102",
                "Hyderabad": "102"
            }
        }

    async def find_nearest_hospitals(self, location: str, specialty: Optional[str] = None,
                                   emergency_only: bool = False, radius_km: int = 10) -> Dict:
        """
        Find nearest hospitals based on location and requirements
        """
        try:
            # Try to get coordinates for the location
            coordinates = await self._get_coordinates(location)

            if coordinates:
                # Use API-based search if coordinates available
                hospitals = await self._search_hospitals_by_coordinates(
                    coordinates, specialty, emergency_only, radius_km
                )
            else:
                # Fallback to database search
                hospitals = await self._search_hospitals_in_database(
                    location, specialty, emergency_only
                )

            # Add emergency services information
            emergency_info = self._get_emergency_services_for_location(location)

            return {
                "location": location,
                "hospitals_found": len(hospitals),
                "hospitals": hospitals,
                "emergency_services": emergency_info,
                "search_criteria": {
                    "specialty": specialty,
                    "emergency_only": emergency_only,
                    "radius_km": radius_km
                },
                "instructions": [
                    "Call the hospital before visiting to confirm availability",
                    "In case of emergency, call 108 for immediate ambulance",
                    "Keep your medical documents ready when visiting",
                    "For government hospitals, early morning visits recommended"
                ]
            }

        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
            return {
                "error": "Unable to find hospitals",
                "emergency_contact": "108",
                "advice": "Please call 108 for emergency medical services"
            }

    async def _get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location using geocoding APIs"""
        try:
            # Try Google Maps Geocoding first
            if self.google_maps_api_key:
                coords = await self._google_geocoding(location)
                if coords:
                    return coords

            # Try MapMyIndia geocoding
            if self.mapmyindia_api_key:
                coords = await self._mapmyindia_geocoding(location)
                if coords:
                    return coords

            return None

        except Exception as e:
            logger.error(f"Error getting coordinates: {e}")
            return None

    async def _google_geocoding(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates using Google Maps Geocoding API"""
        try:
            async with httpx.AsyncClient() as client:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    "address": location,
                    "key": self.google_maps_api_key,
                    "region": "in"
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "OK" and data["results"]:
                        location_data = data["results"][0]["geometry"]["location"]
                        return (location_data["lat"], location_data["lng"])

        except Exception as e:
            logger.error(f"Google geocoding error: {e}")

        return None

    async def _mapmyindia_geocoding(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates using MapMyIndia API"""
        try:
            async with httpx.AsyncClient() as client:
                url = "https://atlas.mapmyindia.com/api/places/geocode"
                params = {
                    "address": location,
                    "itemCount": 1
                }
                headers = {"Authorization": f"Bearer {self.mapmyindia_api_key}"}

                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("copResults"):
                        result = data["copResults"][0]
                        return (float(result["latitude"]), float(result["longitude"]))

        except Exception as e:
            logger.error(f"MapMyIndia geocoding error: {e}")

        return None

    async def _search_hospitals_by_coordinates(self, coordinates: Tuple[float, float],
                                             specialty: Optional[str], emergency_only: bool,
                                             radius_km: int) -> List[Dict]:
        """Search hospitals using coordinates and APIs"""
        hospitals = []

        try:
            # Try Google Places API first
            if self.google_maps_api_key:
                google_hospitals = await self._google_places_search(
                    coordinates, specialty, emergency_only, radius_km
                )
                hospitals.extend(google_hospitals)

            # Fallback to database search with distance calculation
            if not hospitals:
                hospitals = await self._search_nearby_in_database(
                    coordinates, specialty, emergency_only, radius_km
                )

        except Exception as e:
            logger.error(f"Error searching hospitals by coordinates: {e}")

        return hospitals

    async def _google_places_search(self, coordinates: Tuple[float, float],
                                  specialty: Optional[str], emergency_only: bool,
                                  radius_km: int) -> List[Dict]:
        """Search hospitals using Google Places API"""
        hospitals = []

        try:
            async with httpx.AsyncClient() as client:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

                # Build search query
                keyword = "hospital"
                if specialty:
                    keyword += f" {specialty}"
                if emergency_only:
                    keyword += " emergency"

                params = {
                    "location": f"{coordinates[0]},{coordinates[1]}",
                    "radius": radius_km * 1000,  # Convert km to meters
                    "type": "hospital",
                    "keyword": keyword,
                    "key": self.google_maps_api_key
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()

                    for place in data.get("results", []):
                        hospital = {
                            "name": place["name"],
                            "address": place.get("vicinity", "Address not available"),
                            "rating": place.get("rating", "Not rated"),
                            "coordinates": {
                                "lat": place["geometry"]["location"]["lat"],
                                "lng": place["geometry"]["location"]["lng"]
                            },
                            "place_id": place["place_id"],
                            "types": place.get("types", []),
                            "open_now": place.get("opening_hours", {}).get("open_now", None),
                            "source": "Google Places"
                        }

                        # Calculate distance
                        distance = self._calculate_distance(
                            coordinates,
                            (hospital["coordinates"]["lat"], hospital["coordinates"]["lng"])
                        )
                        hospital["distance_km"] = round(distance, 2)

                        hospitals.append(hospital)

                    # Sort by distance
                    hospitals.sort(key=lambda x: x["distance_km"])

        except Exception as e:
            logger.error(f"Google Places search error: {e}")

        return hospitals[:10]  # Return top 10

    async def _search_hospitals_in_database(self, location: str, specialty: Optional[str],
                                          emergency_only: bool) -> List[Dict]:
        """Search hospitals in local database"""
        hospitals = []

        # Normalize location
        location_normalized = self._normalize_location(location)

        # Search in database
        if location_normalized in self.hospital_database:
            for hospital in self.hospital_database[location_normalized]:
                # Filter by specialty if specified
                if specialty and not any(specialty.lower() in s.lower() for s in hospital["specialties"]):
                    continue

                # Filter by emergency if specified
                if emergency_only and not hospital.get("24x7", False):
                    continue

                # Add distance placeholder
                hospital["distance_km"] = "Contact for exact location"
                hospital["source"] = "Local Database"

                hospitals.append(hospital)

        return hospitals

    async def _search_nearby_in_database(self, coordinates: Tuple[float, float],
                                       specialty: Optional[str], emergency_only: bool,
                                       radius_km: int) -> List[Dict]:
        """Search nearby hospitals in database using distance calculation"""
        hospitals = []

        for city, city_hospitals in self.hospital_database.items():
            for hospital in city_hospitals:
                if "coordinates" in hospital:
                    distance = self._calculate_distance(
                        coordinates,
                        (hospital["coordinates"]["lat"], hospital["coordinates"]["lng"])
                    )

                    if distance <= radius_km:
                        # Filter by specialty if specified
                        if specialty and not any(specialty.lower() in s.lower() for s in hospital["specialties"]):
                            continue

                        # Filter by emergency if specified
                        if emergency_only and not hospital.get("24x7", False):
                            continue

                        hospital["distance_km"] = round(distance, 2)
                        hospital["source"] = "Local Database"
                        hospitals.append(hospital)

        # Sort by distance
        hospitals.sort(key=lambda x: x["distance_km"])
        return hospitals[:10]

    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers
        r = 6371

        return c * r

    def _normalize_location(self, location: str) -> str:
        """Normalize location name for database lookup"""
        location_mapping = {
            "delhi": "Delhi",
            "new delhi": "Delhi",
            "mumbai": "Mumbai",
            "bombay": "Mumbai",
            "bangalore": "Bangalore",
            "bengaluru": "Bangalore",
            "chennai": "Chennai",
            "madras": "Chennai",
            "hyderabad": "Hyderabad",
            "kolkata": "Kolkata",
            "calcutta": "Kolkata"
        }
        return location_mapping.get(location.lower(), location.title())

    def _get_emergency_services_for_location(self, location: str) -> Dict:
        """Get emergency services information for location"""
        services = self.emergency_services["national"].copy()

        # Add state-specific ambulance if available
        location_normalized = self._normalize_location(location)
        if location_normalized in self.emergency_services["state_ambulance"]:
            services["state_ambulance"] = self.emergency_services["state_ambulance"][location_normalized]

        # Add medical helplines
        services.update(self.emergency_services["medical_helplines"])

        return services

    async def get_hospital_details(self, hospital_name: str, location: Optional[str] = None) -> Dict:
        """Get detailed information about a specific hospital"""
        try:
            # Search in database first
            for city, hospitals in self.hospital_database.items():
                for hospital in hospitals:
                    if hospital_name.lower() in hospital["name"].lower():
                        return {
                            "hospital": hospital,
                            "city": city,
                            "additional_info": {
                                "visiting_hours": "Usually 10:00 AM - 8:00 PM (varies by department)",
                                "documents_needed": ["ID Proof", "Previous medical records if any"],
                                "payment_options": ["Cash", "Insurance", "Credit/Debit Card"],
                                "facilities": hospital.get("services", [])
                            }
                        }

            return {
                "message": f"Hospital '{hospital_name}' not found in database",
                "suggestion": "Please use the hospital finder feature or contact our helpline"
            }

        except Exception as e:
            logger.error(f"Error getting hospital details: {e}")
            return {"error": "Unable to fetch hospital details"}

    async def get_emergency_guidance(self, emergency_type: str) -> Dict:
        """Get emergency guidance and nearest emergency services"""
        emergency_guidance = {
            "heart_attack": {
                "immediate_steps": [
                    "Call 108 immediately",
                    "Give aspirin if available and not allergic",
                    "Keep the person calm and seated",
                    "Loosen tight clothing",
                    "If unconscious, start CPR"
                ],
                "do_not": [
                    "Do not give food or water",
                    "Do not leave the person alone",
                    "Do not drive yourself to hospital"
                ]
            },
            "stroke": {
                "immediate_steps": [
                    "Call 108 immediately",
                    "Note the time symptoms started",
                    "Keep person lying down with head elevated",
                    "Do not give anything by mouth",
                    "Stay with the person"
                ],
                "signs": ["Face drooping", "Arm weakness", "Speech difficulty", "Time to call emergency"]
            },
            "breathing_difficulty": {
                "immediate_steps": [
                    "Call 108 immediately",
                    "Help person sit upright",
                    "Loosen tight clothing",
                    "If has inhaler, help them use it",
                    "Stay calm and reassure"
                ],
                "warning_signs": ["Blue lips", "Cannot speak", "Gasping", "Chest pain"]
            },
            "accident": {
                "immediate_steps": [
                    "Call 108 and 100 (police)",
                    "Do not move injured person unless in danger",
                    "Control bleeding with direct pressure",
                    "Keep person conscious and talking",
                    "Cover with blanket to prevent shock"
                ],
                "do_not": [
                    "Do not move person with spinal injury",
                    "Do not remove objects from wounds",
                    "Do not give food or water"
                ]
            }
        }

        guidance = emergency_guidance.get(emergency_type.lower(), {
            "immediate_steps": [
                "Call 108 for medical emergency",
                "Stay calm and assess the situation",
                "Provide first aid if trained",
                "Keep the person comfortable",
                "Wait for professional help"
            ]
        })

        guidance["emergency_numbers"] = self.emergency_services["national"]
        guidance["medical_helplines"] = self.emergency_services["medical_helplines"]

        return guidance

# Initialize service instance
hospital_finder = HospitalFinderService()
