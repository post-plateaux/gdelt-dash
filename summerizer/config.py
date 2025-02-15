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
SQL_QUERY = """WITH ref_actor_events AS (
              SELECT globaleventid
              FROM events
              WHERE actor1type1code = '{actor_code}'
                    OR actor1type2code = '{actor_code}'
                    OR actor1type3code = '{actor_code}'
                    OR actor2type1code = '{actor_code}'
                    OR actor2type2code = '{actor_code}'
                    OR actor2type3code = '{actor_code}'
              UNION
              SELECT globaleventid
              FROM events_translated
              WHERE actor1type1code = '{actor_code}'
                    OR actor1type2code = '{actor_code}'
                    OR actor1type3code = '{actor_code}'
                    OR actor2type1code = '{actor_code}'
                    OR actor2type2code = '{actor_code}'
                    OR actor2type3code = '{actor_code}'
            ),
            combined_mentions AS (
              SELECT *
              FROM mentions
              WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
                AND confidence >= 70
              UNION ALL
              SELECT *
              FROM mentions_translated
              WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
                AND confidence >= 70
            ),
            unique_mentions AS (
              SELECT DISTINCT ON (mentionidentifier) *
              FROM combined_mentions
              ORDER BY mentionidentifier, globaleventid
            )
            SELECT DISTINCT ON (globaleventid) *
            FROM unique_mentions
            ORDER BY globaleventid, mentionidentifier;"""
