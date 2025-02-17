import os
from typing import Any, Optional
from prompts import SUMMARY_PROMPT, ARTICLE_PROMPT, CRAWLER_SELECTION_PROMPT

class Config:
    """Configuration manager for the summerizer application"""
    
    # CAMEO Actor Types documentation
    ACTOR_TYPES_DOC = """
    CAMEO Actor Types:
    CODE    LABEL
    COP     Police forces
    GOV     Government
    INS     Insurgents
    JUD     Judiciary
    MIL     Military
    OPP     Political Opposition
    REB     Rebels
    SEP     Separatist Rebels
    SPY     State Intelligence
    UAF     Unaligned Armed Forces
    AGR     Agriculture
    BUS     Business
    CRM     Criminal
    CVL     Civilian
    DEV     Development
    EDU     Education
    ELI     Elites
    ENV     Environmental
    HLH     Health
    HRI     Human Rights
    LAB     Labor
    LEG     Legislature
    MED     Media
    REF     Refugees
    MOD     Moderate
    RAD     Radical
    AMN     Amnesty International
    IRC     Red Cross
    GRP     Greenpeace
    UNO     United Nations
    PKO     Peacekeepers
    UIS     Unidentified State Actor
    IGO     Inter-Governmental Organization
    IMG     International Militarized Group
    INT     International/Transnational Generic
    MNC     Multinational Corporation
    NGM     Non-Governmental Movement
    NGO     Non-Governmental Organization
    UIS     Unidentified State Actor
    SET     Settler
    """

    def __init__(self):
        # Constants
        self.ACTOR_CODE = "GOV"
        self.SQL_QUERY = """SELECT DISTINCT mentionidentifier
FROM (
  SELECT mentionidentifier
  FROM mentions_translated
  WHERE mentionidentifier ILIKE '%DOGE%'
  UNION
  SELECT mentionidentifier
  FROM mentions_translated
  WHERE mentionidentifier ILIKE '%Trump%'
) AS combined_mentions;"""

        # Database settings
        self.POSTGRES_HOST = self.get_env("POSTGRES_HOST", "postgres")
        self.POSTGRES_DB = self.get_env("POSTGRES_DB")
        self.POSTGRES_USER = self.get_env("POSTGRES_USER")
        self.POSTGRES_PASSWORD = self.get_env("POSTGRES_PASSWORD")
        self.POSTGRES_PORT = int(self.get_env("POSTGRES_PORT", "5432"))

        # OpenRouter settings
        self.OPENROUTER_API_KEY = self.get_env("OPENROUTER_API_KEY")
        self.OPENROUTER_MODEL = self.get_env("OPENROUTER_MODEL")
        self.OPENROUTER_ARTICLE_MODEL = self.get_env("OPENROUTER_ARTICLE_MODEL")
        
        # Site settings
        self.SITE_URL = self.get_env("SITE_URL", "http://example.com")
        self.SITE_NAME = self.get_env("SITE_NAME", "My Site")
        
        # Prompt settings loaded from prompts.py
        self.SUMMARY_PROMPT = SUMMARY_PROMPT
        self.ARTICLE_PROMPT = ARTICLE_PROMPT
        self.CRAWLER_SELECTION_PROMPT = CRAWLER_SELECTION_PROMPT
        
        # Article generation settings
        self.ARTICLE_MAX_TOKENS = self.get_env("ARTICLE_MAX_TOKENS")
        self.ARTICLE_TEMPERATURE = self.get_env("ARTICLE_TEMPERATURE")
        
        # Domain blocking
        self.BLOCKED_DOMAINS = [
            d.strip() 
            for d in self.get_env("BLOCKED_DOMAINS", "").split(",") 
            if d.strip()
        ]

    def get_env(self, key: str, default: Any = None) -> Optional[str]:
        """Get environment variable with optional default"""
        value = os.environ.get(key, default)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

# Create a global instance
config = Config()

# Original SQL command (from before refactoring):
# SELECT mentionidentifier
#             FROM (
#               SELECT mentionidentifier
#               FROM mentions
#               WHERE mentionidentifier ILIKE '%Trump%'
#               UNION
#               SELECT mentionidentifier
#               FROM mentions_translated
#               WHERE mentionidentifier ILIKE '%Trump%'
#             ) AS combined_mentions;
