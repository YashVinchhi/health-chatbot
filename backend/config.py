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

    # Free APIs (no keys required)
    disease_sh_base_url: str = "https://disease.sh/v3/covid-19"
    cdc_data_base_url: str = "https://data.cdc.gov/api/odata/v4"
    fda_base_url: str = "https://api.fda.gov"

    # Other settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
