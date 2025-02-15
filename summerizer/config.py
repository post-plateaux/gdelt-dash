"""
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
ACTOR_CODE = "GOV"
SQL_QUERY = """SELECT COUNT(*) AS trump_mentions_count
FROM (
  SELECT mentionidentifier
  FROM mentions
  WHERE mentionidentifier ILIKE '%Trump%'
  UNION
  SELECT mentionidentifier
  FROM mentions_translated
  WHERE mentionidentifier ILIKE '%Trump%'
) AS combined_mentions;"""
