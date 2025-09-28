"""
Advanced Symptom Checker and Medical Triage System
Provides intelligent symptom analysis with severity assessment
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class SymptomAnalyzer:
    """
    Advanced symptom analysis system with medical triage capabilities
    """

    def __init__(self):
        self.symptom_database = self._load_symptom_database()
        self.red_flag_symptoms = self._load_red_flag_symptoms()
        self.severity_matrix = self._load_severity_matrix()
        self.home_remedies = self._load_home_remedies()
        self.specialist_mapping = self._load_specialist_mapping()

    def _load_symptom_database(self) -> Dict:
        """Load comprehensive symptom database with multilingual support"""
        return {
            "fever": {
                "aliases": ["बुखार", "జ్వరం", "காய்ச்சல்", "জ্বর", "high temperature", "pyrexia"],
                "severity_indicators": {
                    "mild": {"temp_range": "99-101°F", "duration": "<3 days", "associated": ["mild headache", "slight fatigue"]},
                    "moderate": {"temp_range": "101-103°F", "duration": "3-5 days", "associated": ["body ache", "chills", "sweating"]},
                    "severe": {"temp_range": ">103°F", "duration": ">5 days", "associated": ["severe headache", "confusion", "difficulty breathing"]}
                },
                "common_causes": ["viral infection", "bacterial infection", "COVID-19", "dengue", "malaria", "typhoid"],
                "when_to_see_doctor": [
                    "Fever above 103°F (39.4°C)",
                    "Fever lasting more than 3 days",
                    "Fever with severe headache",
                    "Fever with difficulty breathing",
                    "Fever with persistent vomiting"
                ]
            },
            "headache": {
                "aliases": ["सिर दर्द", "తల నొప్పి", "தலைவலி", "মাথাব্যথা", "head pain", "cephalgia"],
                "severity_indicators": {
                    "mild": {"intensity": "1-3/10", "duration": "<4 hours", "impact": "minimal daily activity disruption"},
                    "moderate": {"intensity": "4-6/10", "duration": "4-24 hours", "impact": "some daily activity disruption"},
                    "severe": {"intensity": "7-10/10", "duration": ">24 hours", "impact": "significant daily activity disruption"}
                },
                "types": ["tension headache", "migraine", "cluster headache", "sinus headache"],
                "red_flags": ["sudden severe headache", "headache with fever and neck stiffness", "headache with vision changes"],
                "when_to_see_doctor": [
                    "Sudden, severe headache unlike any before",
                    "Headache with fever, stiff neck, confusion",
                    "Headache with vision problems",
                    "Headache after head injury",
                    "Progressive worsening headache"
                ]
            },
            "cough": {
                "aliases": ["खांसी", "దగ్గు", "இருமல்", "কাশি", "tussis"],
                "types": {
                    "dry_cough": {"characteristics": ["no phlegm", "tickling sensation", "worse at night"]},
                    "productive_cough": {"characteristics": ["with phlegm", "morning cough", "chest congestion"]},
                    "chronic_cough": {"duration": ">8 weeks", "causes": ["asthma", "GERD", "post-nasal drip"]}
                },
                "severity_indicators": {
                    "mild": {"frequency": "occasional", "impact": "minimal sleep disruption"},
                    "moderate": {"frequency": "frequent", "impact": "some sleep disruption", "phlegm": "clear/white"},
                    "severe": {"frequency": "persistent", "impact": "significant sleep disruption", "phlegm": "blood-tinged/green"}
                },
                "when_to_see_doctor": [
                    "Cough lasting more than 3 weeks",
                    "Cough with blood",
                    "Cough with high fever",
                    "Cough with chest pain",
                    "Difficulty breathing with cough"
                ]
            },
            "chest_pain": {
                "aliases": ["छाती में दर्द", "ఛాతీ నొప్పి", "மார்புவலி", "বুকেব্যথা", "thoracic pain"],
                "severity_indicators": {
                    "mild": {"intensity": "1-3/10", "nature": "dull ache", "duration": "brief episodes"},
                    "moderate": {"intensity": "4-6/10", "nature": "pressure-like", "duration": "several minutes"},
                    "severe": {"intensity": "7-10/10", "nature": "crushing/squeezing", "duration": "prolonged"}
                },
                "red_flags": [
                    "crushing chest pain",
                    "pain radiating to arm/jaw",
                    "chest pain with sweating",
                    "chest pain with shortness of breath"
                ],
                "emergency_symptoms": [
                    "Severe chest pain lasting >10 minutes",
                    "Chest pain with difficulty breathing",
                    "Chest pain with nausea and sweating",
                    "Chest pain radiating to left arm or jaw"
                ]
            },
            "breathing_difficulty": {
                "aliases": ["सांस लेने में तकलीफ", "ఊపిరి ఆడకపోవడం", "மூச்சுவிடுவதில் சிரமம்", "শ্বাসকষ্ট", "dyspnea", "shortness of breath"],
                "severity_indicators": {
                    "mild": {"triggers": "heavy exertion", "rest_relief": "yes", "speech": "normal"},
                    "moderate": {"triggers": "moderate exertion", "rest_relief": "partial", "speech": "short sentences"},
                    "severe": {"triggers": "minimal exertion/rest", "rest_relief": "no", "speech": "few words only"}
                },
                "emergency_symptoms": [
                    "Severe difficulty breathing at rest",
                    "Blue lips or fingernails",
                    "Cannot speak in full sentences",
                    "Chest retractions",
                    "Gasping for air"
                ]
            },
            "stomach_pain": {
                "aliases": ["पेट दर्द", "కడుపు నొప్పి", "வயிற்றுவலி", "পেটব্যথা", "abdominal pain"],
                "locations": {
                    "upper_abdomen": ["gastritis", "peptic ulcer", "gallbladder issues"],
                    "lower_abdomen": ["appendicitis", "intestinal issues", "urinary problems"],
                    "generalized": ["gastroenteritis", "food poisoning", "viral infection"]
                },
                "severity_indicators": {
                    "mild": {"intensity": "1-3/10", "nature": "cramping", "duration": "intermittent"},
                    "moderate": {"intensity": "4-6/10", "nature": "constant ache", "duration": "several hours"},
                    "severe": {"intensity": "7-10/10", "nature": "sharp/stabbing", "duration": "persistent"}
                },
                "red_flags": [
                    "Severe abdominal pain with vomiting",
                    "Abdominal pain with fever",
                    "Rigid abdomen",
                    "Pain that worsens with movement"
                ]
            }
        }

    def _load_red_flag_symptoms(self) -> List[Dict]:
        """Load red flag symptoms requiring immediate medical attention"""
        return [
            {
                "symptom": "chest_pain_severe",
                "indicators": ["crushing chest pain", "pain radiating to arm", "sweating", "nausea"],
                "urgency": "EMERGENCY",
                "action": "Call 108 immediately - possible heart attack"
            },
            {
                "symptom": "breathing_severe",
                "indicators": ["severe shortness of breath", "blue lips", "gasping", "cannot speak"],
                "urgency": "EMERGENCY",
                "action": "Call 108 immediately - respiratory emergency"
            },
            {
                "symptom": "neurological",
                "indicators": ["sudden severe headache", "confusion", "loss of consciousness", "weakness on one side"],
                "urgency": "EMERGENCY",
                "action": "Call 108 immediately - possible stroke"
            },
            {
                "symptom": "severe_bleeding",
                "indicators": ["heavy bleeding", "bleeding that won't stop", "vomiting blood", "blood in stool"],
                "urgency": "EMERGENCY",
                "action": "Call 108 immediately and apply pressure to bleeding"
            },
            {
                "symptom": "high_fever_complications",
                "indicators": ["fever >104°F", "fever with stiff neck", "fever with confusion", "fever with severe headache"],
                "urgency": "URGENT",
                "action": "Go to emergency room immediately"
            },
            {
                "symptom": "severe_abdominal",
                "indicators": ["severe abdominal pain", "rigid abdomen", "abdominal pain with fever", "persistent vomiting"],
                "urgency": "URGENT",
                "action": "Seek immediate medical attention"
            }
        ]

    def _load_severity_matrix(self) -> Dict:
        """Load severity assessment matrix"""
        return {
            "critical": {
                "score_range": (8, 10),
                "action": "Call 108 emergency services immediately",
                "timeframe": "Immediate",
                "indicators": ["life-threatening symptoms", "severe pain >7/10", "emergency red flags"]
            },
            "urgent": {
                "score_range": (6, 7),
                "action": "Visit emergency room or urgent care within 2-4 hours",
                "timeframe": "2-4 hours",
                "indicators": ["significant symptoms", "moderate to severe pain", "concerning combinations"]
            },
            "moderate": {
                "score_range": (4, 5),
                "action": "Schedule appointment with doctor within 1-2 days",
                "timeframe": "1-2 days",
                "indicators": ["bothersome symptoms", "mild to moderate pain", "affecting daily activities"]
            },
            "mild": {
                "score_range": (1, 3),
                "action": "Monitor symptoms and try home remedies. See doctor if no improvement in 3-5 days",
                "timeframe": "3-5 days if no improvement",
                "indicators": ["minor symptoms", "minimal pain", "not affecting daily activities"]
            }
        }

    def _load_home_remedies(self) -> Dict:
        """Load safe home remedies for common symptoms"""
        return {
            "fever": [
                "Rest and drink plenty of fluids",
                "Take paracetamol as per package instructions",
                "Use cool compresses on forehead",
                "Wear light clothing",
                "Take lukewarm bath",
                "Drink herbal teas (ginger, tulsi)",
                "Eat light, easily digestible foods"
            ],
            "headache": [
                "Rest in a quiet, dark room",
                "Apply cold or warm compress to head/neck",
                "Stay hydrated - drink water",
                "Practice relaxation techniques",
                "Gentle head and neck massage",
                "Take paracetamol if needed",
                "Avoid loud noises and bright lights"
            ],
            "cough": [
                "Drink warm water with honey and lemon",
                "Use steam inhalation (hot water with eucalyptus)",
                "Gargle with warm salt water",
                "Stay hydrated",
                "Use humidifier or breathe moist air",
                "Take ginger tea",
                "Avoid cold drinks and ice cream"
            ],
            "sore_throat": [
                "Gargle with warm salt water (1/2 tsp salt in 1 cup water)",
                "Drink warm liquids (tea, soup, warm water)",
                "Suck on throat lozenges or hard candies",
                "Use humidifier",
                "Rest your voice",
                "Take honey (not for children under 1 year)",
                "Avoid smoking and secondhand smoke"
            ],
            "stomach_pain": [
                "Rest and avoid solid foods initially",
                "Drink clear fluids (water, clear broths)",
                "Try BRAT diet (bananas, rice, applesauce, toast)",
                "Apply warm compress to abdomen",
                "Avoid dairy, caffeine, alcohol",
                "Take small, frequent sips of water",
                "Try ginger tea for nausea"
            ],
            "nausea": [
                "Eat small, frequent meals",
                "Try ginger (tea, capsules, or fresh)",
                "Drink clear fluids in small sips",
                "Avoid strong odors",
                "Get fresh air",
                "Rest with head elevated",
                "Try dry crackers or toast"
            ]
        }

    def _load_specialist_mapping(self) -> Dict:
        """Load specialist recommendations based on symptoms"""
        return {
            "cardiac": ["chest pain", "heart palpitations", "shortness of breath with chest pain"],
            "pulmonary": ["persistent cough", "breathing difficulty", "chest congestion"],
            "gastroenterology": ["abdominal pain", "persistent nausea", "digestive issues"],
            "neurology": ["severe headaches", "dizziness", "neurological symptoms"],
            "ent": ["sore throat", "ear pain", "sinus problems"],
            "dermatology": ["skin rash", "skin changes", "allergic reactions"],
            "orthopedic": ["joint pain", "back pain", "muscle injuries"],
            "general_medicine": ["fever", "general weakness", "multiple symptoms"]
        }

    async def analyze_symptoms(self, symptoms: List[str], duration: Optional[str] = None,
                             severity: Optional[str] = None, additional_info: Optional[Dict] = None) -> Dict:
        """
        Comprehensive symptom analysis with severity assessment
        """
        try:
            # Normalize and process symptoms
            processed_symptoms = self._process_symptoms(symptoms)

            # Check for red flag symptoms
            red_flags = self._check_red_flags(processed_symptoms)

            # Calculate severity score
            severity_assessment = self._assess_severity(processed_symptoms, duration, severity, additional_info)

            # Get recommendations
            recommendations = self._get_recommendations(processed_symptoms, severity_assessment)

            # Get home remedies
            home_remedies = self._get_applicable_home_remedies(processed_symptoms)

            # Get specialist recommendation
            specialist = self._recommend_specialist(processed_symptoms)

            response = {
                "symptoms_analyzed": processed_symptoms,
                "severity_assessment": severity_assessment,
                "red_flags": red_flags,
                "recommendations": recommendations,
                "home_remedies": home_remedies,
                "specialist_recommendation": specialist,
                "general_advice": self._get_general_advice(),
                "emergency_numbers": {
                    "ambulance": "108",
                    "police": "100",
                    "fire": "101",
                    "health_helpline": "1075"
                }
            }

            return response

        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
            return {
                "error": "Unable to analyze symptoms",
                "advice": "Please consult with a healthcare professional for proper evaluation"
            }

    def _process_symptoms(self, symptoms: List[str]) -> List[Dict]:
        """Process and normalize symptom inputs"""
        processed = []

        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()

            # Find matching symptom in database
            matched_symptom = None
            for key, data in self.symptom_database.items():
                if (symptom_lower == key or
                    symptom_lower in [alias.lower() for alias in data.get("aliases", [])] or
                    any(alias.lower() in symptom_lower for alias in data.get("aliases", []))):
                    matched_symptom = {
                        "name": key,
                        "input": symptom,
                        "data": data
                    }
                    break

            if not matched_symptom:
                # Generic symptom processing
                matched_symptom = {
                    "name": symptom_lower,
                    "input": symptom,
                    "data": {"severity_indicators": {}, "when_to_see_doctor": []}
                }

            processed.append(matched_symptom)

        return processed

    def _check_red_flags(self, symptoms: List[Dict]) -> List[Dict]:
        """Check for red flag symptoms requiring immediate attention"""
        red_flags_found = []

        for red_flag in self.red_flag_symptoms:
            for indicator in red_flag["indicators"]:
                for symptom in symptoms:
                    if (indicator.lower() in symptom["input"].lower() or
                        indicator.lower() in symptom["name"].lower()):
                        red_flags_found.append(red_flag)
                        break

        return red_flags_found

    def _assess_severity(self, symptoms: List[Dict], duration: Optional[str],
                        severity: Optional[str], additional_info: Optional[Dict]) -> Dict:
        """Calculate severity score and assessment"""
        base_score = 0
        factors = []

        # Base score from symptoms
        for symptom in symptoms:
            if symptom["name"] in ["chest_pain", "breathing_difficulty"]:
                base_score += 3
                factors.append("High priority symptom detected")
            elif symptom["name"] in ["fever", "headache"]:
                base_score += 2
                factors.append("Common symptom requiring attention")
            else:
                base_score += 1

        # Duration factor
        if duration:
            if "week" in duration.lower() or "month" in duration.lower():
                base_score += 2
                factors.append("Prolonged duration increases concern")
            elif "day" in duration.lower():
                days = self._extract_number(duration)
                if days and days > 3:
                    base_score += 1
                    factors.append("Extended duration")

        # Severity factor
        if severity:
            if severity.lower() in ["severe", "extreme", "unbearable"]:
                base_score += 3
                factors.append("High severity reported")
            elif severity.lower() in ["moderate", "significant"]:
                base_score += 2
                factors.append("Moderate severity")
            elif severity.lower() in ["mild", "slight"]:
                base_score += 1
                factors.append("Mild severity")

        # Additional info factors
        if additional_info:
            if additional_info.get("fever_temp") and float(additional_info["fever_temp"]) > 103:
                base_score += 2
                factors.append("High fever detected")
            if additional_info.get("affecting_sleep") == "yes":
                base_score += 1
                factors.append("Affecting sleep quality")
            if additional_info.get("affecting_work") == "yes":
                base_score += 1
                factors.append("Affecting daily activities")

        # Determine severity level
        severity_level = "mild"
        for level, data in self.severity_matrix.items():
            if data["score_range"][0] <= base_score <= data["score_range"][1]:
                severity_level = level
                break

        # Handle scores above maximum
        if base_score > 7:
            severity_level = "critical"

        return {
            "score": base_score,
            "level": severity_level,
            "factors": factors,
            "assessment": self.severity_matrix[severity_level]
        }

    def _get_recommendations(self, symptoms: List[Dict], severity_assessment: Dict) -> List[str]:
        """Get specific recommendations based on symptoms and severity"""
        recommendations = []

        # Add severity-based recommendation
        recommendations.append(severity_assessment["assessment"]["action"])

        # Add symptom-specific recommendations
        for symptom in symptoms:
            when_to_see_doctor = symptom["data"].get("when_to_see_doctor", [])
            if when_to_see_doctor:
                recommendations.extend([f"See doctor if: {item}" for item in when_to_see_doctor[:2]])

        # Add general monitoring advice
        recommendations.extend([
            "Monitor symptoms and note any changes",
            "Keep a symptom diary with times and severity",
            "Stay hydrated and get adequate rest"
        ])

        return list(set(recommendations))  # Remove duplicates

    def _get_applicable_home_remedies(self, symptoms: List[Dict]) -> List[str]:
        """Get applicable home remedies for symptoms"""
        remedies = []

        for symptom in symptoms:
            symptom_name = symptom["name"]
            if symptom_name in self.home_remedies:
                remedies.extend(self.home_remedies[symptom_name][:3])  # Top 3 remedies

        if not remedies:
            remedies = [
                "Rest and stay hydrated",
                "Eat nutritious, easily digestible foods",
                "Avoid stress and get adequate sleep"
            ]

        # Add disclaimer
        remedies.append("⚠️ These are general suggestions. Consult healthcare provider for proper diagnosis.")

        return list(set(remedies))  # Remove duplicates

    def _recommend_specialist(self, symptoms: List[Dict]) -> Dict:
        """Recommend appropriate medical specialist"""
        specialist_scores = {}

        for symptom in symptoms:
            symptom_name = symptom["name"]
            for specialist, symptom_list in self.specialist_mapping.items():
                if any(s in symptom_name for s in symptom_list):
                    specialist_scores[specialist] = specialist_scores.get(specialist, 0) + 1

        if specialist_scores:
            recommended_specialist = max(specialist_scores, key=specialist_scores.get)
        else:
            recommended_specialist = "general_medicine"

        specialist_names = {
            "cardiac": "Cardiologist (Heart Specialist)",
            "pulmonary": "Pulmonologist (Lung Specialist)",
            "gastroenterology": "Gastroenterologist (Digestive System Specialist)",
            "neurology": "Neurologist (Brain & Nervous System Specialist)",
            "ent": "ENT Specialist (Ear, Nose, Throat)",
            "dermatology": "Dermatologist (Skin Specialist)",
            "orthopedic": "Orthopedic Doctor (Bone & Joint Specialist)",
            "general_medicine": "General Physician"
        }

        return {
            "specialist": specialist_names.get(recommended_specialist, "General Physician"),
            "reason": f"Based on your symptoms, this specialist would be most appropriate",
            "alternatives": "You can also start with a General Physician who can refer you if needed"
        }

    def _get_general_advice(self) -> List[str]:
        """Get general health advice"""
        return [
            "🏥 When in doubt, always consult a healthcare professional",
            "📱 Save emergency numbers: 108 for ambulance, 1075 for health helpline",
            "📝 Keep track of your symptoms, their timing, and severity",
            "💊 Don't self-medicate with prescription drugs",
            "🚨 Seek immediate help for severe or worsening symptoms",
            "🧘‍♀️ Practice stress management and maintain good sleep hygiene"
        ]

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None

# Initialize service instance
symptom_analyzer = SymptomAnalyzer()
