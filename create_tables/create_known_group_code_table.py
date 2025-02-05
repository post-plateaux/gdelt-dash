import os
import psycopg2
import traceback

# Retrieve database connection details
db_user = os.getenv('POSTGIS_USER')
db_password = os.getenv('POSTGIS_PASSWORD')
db_name = os.getenv('POSTGIS_DB')
db_host = os.getenv('POSTGIS_HOST')
db_port = os.getenv('POSTGIS_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print("Connection to the database was successful!")

    # Drop the cameo_known_group table if it exists
    cursor.execute("DROP TABLE IF EXISTS cameo_known_group CASCADE;")
    print("Table cameo_known_group dropped successfully.")

    # Create the cameo_known_group table
    create_table_query = """
    CREATE TABLE cameo_known_group (
        group_code VARCHAR(10) PRIMARY KEY,
        group_label VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table cameo_known_group created successfully.")
    conn.commit()

    # Insert data directly into cameo_known_group
    cameo_known_group_data = [
    ("AAM", "Al Aqsa Martyrs Brigade"),
    ("ABD", "Arab Bank for Economic Development in Africa"),
    ("ACC", "Arab Cooperation Council"),
    ("ADB", "Asian Development Bank"),
    ("AEU", "Arab Economic Unity Council"),
    ("AFB", "African Development Bank"),
    ("ALQ", "Al Qaeda"),
    ("AMF", "Arab Monetary Fund for Economic and Social Development"),
    ("AML", "Amal Militia"),
    ("AMN", "Amnesty International"),
    ("AMU", "Arab Maghreb Union"),
    ("ANO", "Abu Nidal Organization"),
    ("APE", "Org. of Arab Petroleum Exporting Countries (OAPEC)"),
    ("ARL", "Arab League"),
    ("ASL", "South Lebanon Army"),
    ("ASN", "Association of Southeast Asian Nations (ASEAN)"),
    ("ATD", "Eastern and Southern African Trade and Development Bank"),
    ("BCA", "Bank of Central African States (BEAC)"),
    ("BIS", "Bank for International Settlements"),
    ("BTH", "Baath Party"),
    ("CEM", "Common Market for Eastern and Southern Africa_OR_Monetary and Economic Community of Central Africa"),
    ("CFA", "Franc Zone Financial Community of Africa"),
    ("CIS", "Commonwealth of Independent States"),
    ("CMN", "Communist"),
    ("COE", "Council of Europe"),
    ("CPA", "Cocoa Producer's Alliance"),
    ("CPC", "Association of Coffee Producing Countries"),
    ("CRC", "International Fed. of Red Cross and Red Crescent (ICRC)"),
    ("CSS", "Community of Sahel-Saharan States (CENSAD)"),
    ("CWN", "Commonwealth of Nations"),
    ("DFL", "Democratic Front for the Lib. of Palestine (DFLP)"),
    ("EBR", "European Bank for Reconstruction and Development"),
    ("ECA", "Economic Community of Central African States"),
    ("EEC", "European Union"),
    ("EFT", "European Free Trade Association"),
    ("ENN", "Ennahda Movement"),
    ("FAO", "United Nations Food and Agriculture Organization"),
    ("FID", "International Federation of Human Rights (FIDH)"),
    ("FIS", "Islamic Salvation Army"),
    ("FLN", "National Liberation Front (FLN)"),
    ("FTA", "Fatah"),
    ("GCC", "Gulf Cooperation Council"),
    ("GIA", "Armed Islamic Group (GIA)"),
    ("GOE", "Group of Eight (G-8) (G-7 plus Russia)"),
    ("GOS", "Group of Seven (G-7)"),
    ("GSP", "Salafist Group"),
    ("GSS", "Group of Seventy-Seven (G-77)"),
    ("HCH", "UN High Commission for Human Rights"),
    ("HCR", "UN High Commission for Refugees"),
    ("HEZ", "Hezbullah"),
    ("HIP", "Highly Indebted Poor Countries (HIPC)"),
    ("HMS", "Hamas"),
    ("HRW", "Human Rights Watch"),
    ("IAC", "Inter-African Coffee Organization (IACO)"),
    ("IAD", "Intergovernmental Authority on Development (IGAD)"),
    ("IAE", "International Atomic Energy Agency (IAEA)"),
    ("IAF", "Islamic Action Front"),
    ("ICC", "International Criminal Court"),
    ("ICG", "International Crisis Group"),
    ("ICJ", "International Court of Justice (ICJ)"),
    ("ICO", "International Cocoa Organization (ICCO)"),
    ("IDB", "Islamic Development Bank"),
    ("IGC", "International Grains Council"),
    ("IHF", "International Helsinki Federation for Human Rights"),
    ("ILO", "International Labor Organization"),
    ("IMF", "International Monetary Fund (IMF)"),
    ("IOM", "International Organization for Migration"),
    ("IPU", "Inter-Parliamentary Union"),
    ("IRC", "Red Cross"),
    ("ISJ", "Palestinian Islamic Jihad"),
    ("ITP", "Interpol"),
    ("JUR", "International Commission of Jurists"),
    ("KDP", "Kurdish Democratic Party (KDP)"),
    ("KID", "United Nations Children?s Fund (UNICEF)"),
    ("LBA", "Israeli Labor Party"),
    ("LKD", "Likud Party"),
    ("MBR", "Muslim Brotherhood"),
    ("MRZ", "Meretz Party"),
    ("MSF", "Medecins Sans Frontieres (Doctors Without Borders)"),
    ("MSP", "Movement of the Society for Peace"),
    ("NAT", "North Atlantic Treaty Organization (NATO)"),
    ("NEP", "New Economic Partnership for Africa?s Development"),
    ("NON", "Organization of Non-Aligned Countries"),
    ("OAS", "Organization of American States"),
    ("OAU", "Organization of African Unity (OAU)"),
    ("OIC", "Organization of Islamic Conferences (OIC)"),
    ("OPC", "Organization of Petroleum Exporting Countries (OPEC)"),
    ("PAP", "Pan-African Parliament"),
    ("PFL", "People's Front for the Liberation of Palestine (PFLP)"),
    ("PLF", "Palestine Liberation Front"),
    ("PLO", "Palestine Liberation Organization"),
    ("PLS", "Polisario Guerillas"),
    ("PMD", "People's Mujahedeen"),
    ("PRC", "Paris Club"),
    ("PSE", "Occupied Palestinian Territories"),
    ("RCR", "Red Crescent"),
    ("RND", "Democratic National Rally"),
    ("SAA", "South Asian Association"),
    ("SAD", "Southern African Development Community"),
    ("SCE", "Council of Security and Cooperation in Europe (OSCE)"),
    ("SHA", "Shas Party"),
    ("SOT", "Southeast Asia Collective Defense Treaty (SEATO)"),
    ("TAL", "Taliban"),
    ("UEM", "Economic and Monetary Union of West Africa (UEMOA)"),
    ("UNO", "United Nations"),
    ("WAD", "West Africa Development Bank"),
    ("WAM", "West Africa Monetary and Economic Union"),
    ("WAS", "Economic Community of West African States (ECOWAS)"),
    ("WBK", "World Bank"),
    ("WCT", "International War Crimes Tribunals"),
    ("WEF", "World Economic Forum"),
    ("WFP", "World Food Program"),
    ("WHO", "World Health Organization"),
    ("WTO", "World Trade Organization"),
    ("XFM", "Oxfam")
]

    for group_code, group_label in cameo_known_group_data:
        insert_query = "INSERT INTO cameo_known_group (group_code, group_label) VALUES (%s, %s)"
        cursor.execute(insert_query, (group_code, group_label))
    print("Data loaded successfully into cameo_known_group.")
    conn.commit()

except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print(traceback.format_exc())
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
