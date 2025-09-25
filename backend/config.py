import os
from typing import Optional

class Settings:
    # Health Data APIs
    cdc_api_key: Optional[str] = os.getenv("CDC_API_KEY")
    fda_api_key: Optional[str] = os.getenv("FDA_API_KEY")
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")

    # Location Services
    google_maps_api_key: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    opencage_api_key: Optional[str] = os.getenv("OPENCAGE_API_KEY")

    # Weather Data
    openweather_api_key: Optional[str] = os.getenv("OPENWEATHER_API_KEY")

    # Medical APIs
    infermedica_app_id: Optional[str] = os.getenv("INFERMEDICA_APP_ID")
    infermedica_app_key: Optional[str] = os.getenv("INFERMEDICA_APP_KEY")

    # Indian Health APIs
    data_gov_in_api_key: Optional[str] = os.getenv("DATA_GOV_IN_API_KEY")
    covid19_india_api_key: Optional[str] = os.getenv("COVID19_INDIA_API_KEY")

    # User's existing API configurations (backward compatibility)
    cowin_api_key: Optional[str] = os.getenv("COWIN_API_KEY")
    idsp_api_key: Optional[str] = os.getenv("IDSP_API_KEY")

    # Database Configuration - Updated to match user's .env
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./health_chatbot.db")

    # SMS/WhatsApp Configuration - Updated to match user's .env structure
    # WhatsApp (user has different variable names)
    whatsapp_api_key: Optional[str] = os.getenv("WHATSAPP_API_KEY")
    whatsapp_api_secret: Optional[str] = os.getenv("WHATSAPP_API_SECRET")
    whatsapp_phone_number: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER")

    # Map to new variable names for backward compatibility
    whatsapp_token: Optional[str] = os.getenv("WHATSAPP_TOKEN") or os.getenv("WHATSAPP_API_KEY")
    whatsapp_phone_number_id: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("WHATSAPP_PHONE_NUMBER")

    # SMS Configuration (user's structure)
    sms_api_key: Optional[str] = os.getenv("SMS_API_KEY")
    sms_sender_id: Optional[str] = os.getenv("SMS_SENDER_ID", "HEALTH")

    # Twilio (fallback/alternative SMS service)
    twilio_account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")

    # Security Configuration - Updated to match user's .env
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    encryption_key: Optional[str] = os.getenv("ENCRYPTION_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Rasa Configuration - Added from user's .env
    rasa_model_path: str = os.getenv("RASA_MODEL_PATH", "models")
    rasa_api_url: str = os.getenv("RASA_API_URL", "http://localhost:5005")
    rasa_actions_url: str = os.getenv("RASA_ACTIONS_URL", "http://localhost:5055")
    rasa_url: str = os.getenv("RASA_URL", "http://localhost:5005")

    # Free APIs (no keys required)
    disease_sh_base_url: str = "https://disease.sh/v3/covid-19"
    cdc_data_base_url: str = "https://data.cdc.gov/api/odata/v4"
    fda_base_url: str = "https://api.fda.gov"

    # Other settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS Configuration
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()
