"""
Comprehensive Vaccination Information Service
Alternative to Co-WIN API using publicly available data
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VaccinationService:
    """
    Vaccination information service with comprehensive data
    for Indian vaccination programs
    """

    def __init__(self):
        self.vaccination_data = self._load_vaccination_data()
        self.state_centers = self._load_state_centers()
        self.helpline_numbers = self._load_helpline_numbers()

    def _load_vaccination_data(self) -> Dict:
        """Load comprehensive vaccination schedule and information"""
        return {
            "covid_vaccines": {
                "available_vaccines": [
                    {
                        "name": "Covishield",
                        "manufacturer": "Serum Institute of India",
                        "doses": 2,
                        "gap": "84 days",
                        "age_group": "18+",
                        "efficacy": "70-90%",
                        "type": "Viral Vector"
                    },
                    {
                        "name": "Covaxin",
                        "manufacturer": "Bharat Biotech",
                        "doses": 2,
                        "gap": "28 days",
                        "age_group": "18+",
                        "efficacy": "78%",
                        "type": "Inactivated Virus"
                    },
                    {
                        "name": "Sputnik V",
                        "manufacturer": "Dr. Reddy's",
                        "doses": 2,
                        "gap": "21 days",
                        "age_group": "18+",
                        "efficacy": "91.6%",
                        "type": "Viral Vector"
                    }
                ],
                "booster_info": {
                    "eligible": "60+ years, healthcare workers, frontline workers",
                    "gap_from_second_dose": "9 months",
                    "vaccines": ["Covishield", "Covaxin", "Sputnik V"]
                },
                "child_vaccination": {
                    "age_group": "15-18 years",
                    "vaccines": ["Covaxin"],
                    "doses": 2,
                    "gap": "28 days"
                }
            },
            "routine_immunization": {
                "infants": [
                    {"vaccine": "BCG", "age": "At birth", "disease": "Tuberculosis"},
                    {"vaccine": "Hepatitis B", "age": "At birth", "disease": "Hepatitis B"},
                    {"vaccine": "OPV-0", "age": "At birth", "disease": "Polio"},
                    {"vaccine": "DPT-1", "age": "6 weeks", "disease": "Diphtheria, Pertussis, Tetanus"},
                    {"vaccine": "OPV-1", "age": "6 weeks", "disease": "Polio"},
                    {"vaccine": "Rotavirus-1", "age": "6 weeks", "disease": "Rotavirus"},
                    {"vaccine": "IPV-1", "age": "6 weeks", "disease": "Polio"},
                    {"vaccine": "DPT-2", "age": "10 weeks", "disease": "Diphtheria, Pertussis, Tetanus"},
                    {"vaccine": "OPV-2", "age": "10 weeks", "disease": "Polio"},
                    {"vaccine": "Rotavirus-2", "age": "10 weeks", "disease": "Rotavirus"},
                    {"vaccine": "DPT-3", "age": "14 weeks", "disease": "Diphtheria, Pertussis, Tetanus"},
                    {"vaccine": "OPV-3", "age": "14 weeks", "disease": "Polio"},
                    {"vaccine": "IPV-2", "age": "14 weeks", "disease": "Polio"},
                    {"vaccine": "Rotavirus-3", "age": "14 weeks", "disease": "Rotavirus"},
                    {"vaccine": "Measles-1", "age": "9 months", "disease": "Measles"},
                    {"vaccine": "JE-1", "age": "9 months", "disease": "Japanese Encephalitis"},
                    {"vaccine": "DPT Booster-1", "age": "16-24 months", "disease": "Diphtheria, Pertussis, Tetanus"},
                    {"vaccine": "OPV Booster", "age": "16-24 months", "disease": "Polio"},
                    {"vaccine": "Measles-2", "age": "16-24 months", "disease": "Measles"},
                    {"vaccine": "JE-2", "age": "16-24 months", "disease": "Japanese Encephalitis"},
                    {"vaccine": "DPT Booster-2", "age": "5-6 years", "disease": "Diphtheria, Pertussis, Tetanus"},
                    {"vaccine": "TT", "age": "10 years", "disease": "Tetanus"},
                    {"vaccine": "TT", "age": "16 years", "disease": "Tetanus"}
                ],
                "adults": [
                    {"vaccine": "Tetanus-Diphtheria", "frequency": "Every 10 years", "age": "18+"},
                    {"vaccine": "Influenza", "frequency": "Annual", "age": "50+"},
                    {"vaccine": "Pneumococcal", "frequency": "Once", "age": "65+"},
                    {"vaccine": "Hepatitis B", "frequency": "3 doses", "age": "High risk"},
                    {"vaccine": "HPV", "frequency": "3 doses", "age": "9-26 years (females)"}
                ],
                "pregnant_women": [
                    {"vaccine": "TT-1", "timing": "Early pregnancy", "disease": "Tetanus"},
                    {"vaccine": "TT-2", "timing": "4 weeks after TT-1", "disease": "Tetanus"},
                    {"vaccine": "TT Booster", "timing": "If received 2 TT doses within 3 years", "disease": "Tetanus"}
                ]
            },
            "travel_vaccines": [
                {"vaccine": "Yellow Fever", "required_for": "Africa, South America"},
                {"vaccine": "Meningococcal", "required_for": "Hajj pilgrimage, Africa"},
                {"vaccine": "Japanese Encephalitis", "required_for": "Southeast Asia"},
                {"vaccine": "Typhoid", "recommended_for": "Most international travel"},
                {"vaccine": "Hepatitis A", "recommended_for": "International travel"},
                {"vaccine": "Cholera", "required_for": "Some African countries"}
            ]
        }

    def _load_state_centers(self) -> Dict:
        """Load vaccination centers by state"""
        return {
            "Delhi": {
                "government_hospitals": [
                    "AIIMS Delhi", "Safdarjung Hospital", "Ram Manohar Lohia Hospital",
                    "Lady Hardinge Medical College", "Maulana Azad Medical College"
                ],
                "centers": [
                    "Delhi Cantonment Board Dispensary", "East Delhi Medical College",
                    "Hindu Rao Hospital", "LNJP Hospital", "Rajiv Gandhi Super Speciality Hospital"
                ]
            },
            "Mumbai": {
                "government_hospitals": [
                    "King Edward Memorial Hospital", "Lokmanya Tilak Municipal General Hospital",
                    "Rajawadi Hospital", "Sion Hospital", "Nair Hospital"
                ],
                "centers": [
                    "BMC Health Centers", "Primary Health Centers", "Urban Health Centers"
                ]
            },
            "Bangalore": {
                "government_hospitals": [
                    "Victoria Hospital", "Bowring and Lady Curzon Hospital",
                    "KC General Hospital", "Indira Gandhi Institute of Child Health"
                ],
                "centers": [
                    "BBMP Health Centers", "Primary Health Centers", "Urban Primary Health Centers"
                ]
            },
            "Chennai": {
                "government_hospitals": [
                    "Rajiv Gandhi Government General Hospital", "Kilpauk Medical College Hospital",
                    "Stanley Medical College Hospital", "Institute of Child Health and Hospital for Children"
                ],
                "centers": [
                    "Corporation Health Centers", "Primary Health Centers", "Urban Health Centers"
                ]
            },
            "Hyderabad": {
                "government_hospitals": [
                    "Gandhi Hospital", "Osmania General Hospital", "Niloufer Hospital",
                    "Institute of Preventive Medicine"
                ],
                "centers": [
                    "GHMC Health Centers", "Primary Health Centers", "Urban Health Centers"
                ]
            }
        }

    def _load_helpline_numbers(self) -> Dict:
        """Load vaccination helpline numbers"""
        return {
            "national": {
                "cowin_helpline": "1075",
                "covid_helpline": "011-23978046",
                "health_ministry": "1800-11-4477"
            },
            "states": {
                "Delhi": "011-22307145",
                "Mumbai": "022-22927787",
                "Bangalore": "080-22963819",
                "Chennai": "044-25619048",
                "Hyderabad": "040-24651119"
            }
        }

    async def get_vaccination_schedule(self, age: Optional[str] = None,
                                     vaccine_type: Optional[str] = None) -> Dict:
        """Get vaccination schedule based on age and vaccine type"""
        try:
            if vaccine_type and vaccine_type.lower() in ['covid', 'covid-19']:
                return await self._get_covid_vaccine_info(age)
            elif age:
                return await self._get_age_based_schedule(age)
            else:
                return await self._get_general_vaccination_info()
        except Exception as e:
            logger.error(f"Error getting vaccination schedule: {e}")
            return {"error": "Unable to fetch vaccination information"}

    async def _get_covid_vaccine_info(self, age: Optional[str] = None) -> Dict:
        """Get COVID-19 vaccination information"""
        covid_data = self.vaccination_data["covid_vaccines"]

        response = {
            "title": "COVID-19 Vaccination Information",
            "available_vaccines": covid_data["available_vaccines"],
            "registration": {
                "platform": "CoWIN Portal",
                "website": "https://www.cowin.gov.in/",
                "app": "Aarogya Setu App",
                "documents_required": [
                    "Aadhaar Card", "Voter ID", "Passport", "Driving License",
                    "PAN Card", "NPR Smart Card", "Pension Document"
                ]
            },
            "booster_info": covid_data["booster_info"],
            "child_vaccination": covid_data["child_vaccination"],
            "helplines": self.helpline_numbers["national"],
            "precautions": [
                "Stay hydrated before vaccination",
                "Inform about allergies or medical conditions",
                "Wait for 30 minutes post-vaccination for observation",
                "Continue COVID-appropriate behavior after vaccination"
            ]
        }

        return response

    async def _get_age_based_schedule(self, age: str) -> Dict:
        """Get vaccination schedule based on age"""
        try:
            age_num = int(age)
            routine_data = self.vaccination_data["routine_immunization"]

            if age_num < 2:
                vaccines = [v for v in routine_data["infants"] if self._is_age_appropriate(v["age"], age_num)]
                category = "Infant Vaccination Schedule"
            elif age_num < 18:
                vaccines = [v for v in routine_data["infants"] if "years" in v["age"]]
                category = "Child/Adolescent Vaccination Schedule"
            else:
                vaccines = routine_data["adults"]
                category = "Adult Vaccination Schedule"

            return {
                "category": category,
                "age": age,
                "vaccines": vaccines,
                "next_due": self._get_next_due_vaccines(age_num),
                "general_advice": [
                    "Maintain vaccination records",
                    "Consult healthcare provider for personalized schedule",
                    "Report any adverse reactions",
                    "Follow up for booster doses"
                ]
            }
        except ValueError:
            return {"error": "Please provide age in years (e.g., 25)"}

    async def _get_general_vaccination_info(self) -> Dict:
        """Get general vaccination information"""
        return {
            "title": "Vaccination Information for India",
            "government_programs": [
                {
                    "name": "Universal Immunization Programme (UIP)",
                    "description": "Free vaccination for children under 2 years and pregnant women",
                    "vaccines": "12 vaccine-preventable diseases"
                },
                {
                    "name": "Mission Indradhanush",
                    "description": "Intensified immunization drive",
                    "target": "90% immunization coverage"
                },
                {
                    "name": "COVID-19 Vaccination Drive",
                    "description": "World's largest vaccination campaign",
                    "status": "Ongoing for all eligible population"
                }
            ],
            "vaccination_centers": {
                "government": "PHCs, CHCs, District Hospitals, Medical Colleges",
                "private": "Registered private hospitals and clinics"
            },
            "cost": {
                "government_centers": "Free for routine immunization",
                "private_centers": "Charges applicable"
            },
            "helplines": self.helpline_numbers["national"]
        }

    def _is_age_appropriate(self, vaccine_age: str, current_age: int) -> bool:
        """Check if vaccine is appropriate for current age"""
        if "birth" in vaccine_age.lower():
            return current_age == 0
        elif "weeks" in vaccine_age:
            weeks = int(vaccine_age.split()[0])
            return current_age <= (weeks / 4.33)  # Convert weeks to months
        elif "months" in vaccine_age:
            months = int(vaccine_age.split()[0])
            return current_age >= (months / 12)  # Convert months to years
        return False

    def _get_next_due_vaccines(self, age: int) -> List[Dict]:
        """Get next due vaccines based on age"""
        # This would be more sophisticated in a real implementation
        if age < 1:
            return [{"vaccine": "Check with pediatrician for next due vaccines", "timing": "As per schedule"}]
        elif age < 18:
            return [{"vaccine": "Consult healthcare provider", "timing": "For catch-up vaccines if missed"}]
        else:
            return [{"vaccine": "Tetanus-Diphtheria booster", "timing": "Every 10 years"}]

    async def find_vaccination_centers(self, location: str) -> Dict:
        """Find vaccination centers near location"""
        location_key = self._normalize_location(location)

        if location_key in self.state_centers:
            centers = self.state_centers[location_key]
            return {
                "location": location,
                "government_hospitals": centers["government_hospitals"],
                "health_centers": centers["centers"],
                "helpline": self.helpline_numbers["states"].get(location_key, self.helpline_numbers["national"]["cowin_helpline"]),
                "instructions": [
                    "Call the center before visiting",
                    "Carry required documents",
                    "Check vaccination availability",
                    "Follow COVID protocols"
                ]
            }
        else:
            return {
                "message": f"For vaccination centers in {location}, please:",
                "steps": [
                    "Visit CoWIN portal: https://www.cowin.gov.in/",
                    "Use 'Find Vaccination Centers' feature",
                    "Enter your PIN code",
                    "Call local health department",
                    f"Contact helpline: {self.helpline_numbers['national']['cowin_helpline']}"
                ]
            }

    def _normalize_location(self, location: str) -> str:
        """Normalize location name for lookup"""
        location_mapping = {
            "delhi": "Delhi",
            "mumbai": "Mumbai",
            "bangalore": "Bangalore",
            "bengaluru": "Bangalore",
            "chennai": "Chennai",
            "hyderabad": "Hyderabad"
        }
        return location_mapping.get(location.lower(), location)

    async def get_vaccine_side_effects_info(self, vaccine_name: str) -> Dict:
        """Get information about vaccine side effects"""
        common_side_effects = {
            "covid": [
                "Pain, redness, swelling at injection site",
                "Fatigue", "Headache", "Muscle pain", "Chills",
                "Fever", "Nausea"
            ],
            "general": [
                "Mild fever", "Soreness at injection site",
                "Mild fussiness", "Temporary loss of appetite"
            ]
        }

        serious_symptoms = [
            "Difficulty breathing", "Swelling of face and throat",
            "Fast heartbeat", "Weakness", "Dizziness",
            "Severe allergic reactions"
        ]

        return {
            "vaccine": vaccine_name,
            "common_side_effects": common_side_effects.get(vaccine_name.lower(), common_side_effects["general"]),
            "serious_symptoms": serious_symptoms,
            "advice": [
                "Most side effects are mild and resolve in 1-2 days",
                "Use cold compress for injection site pain",
                "Take rest and drink plenty of fluids",
                "Consult doctor if symptoms persist or worsen",
                "Seek immediate medical help for serious symptoms"
            ],
            "reporting": {
                "platform": "AEFI (Adverse Event Following Immunization)",
                "helpline": self.helpline_numbers["national"]["cowin_helpline"]
            }
        }

# Initialize service instance
vaccination_service = VaccinationService()
