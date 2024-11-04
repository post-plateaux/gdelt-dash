import os
import psycopg2
import traceback

# Retrieve database connection details
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print("Connection to the database was successful!")

    # Drop the fips_country table if it exists
    cursor.execute("DROP TABLE IF EXISTS fips_country CASCADE;")
    print("Table fips_country dropped successfully.")

    # Create the fips_country table
    create_table_query = """
    CREATE TABLE fips_country (
        country_code VARCHAR(10) PRIMARY KEY,
        country_name VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table fips_country created successfully.")
    conn.commit()

    # Insert data directly into fips_country
    fips_country_data = [
    ("AF", "Afghanistan"),
    ("AX", "Akrotiri Sovereign Base Area"),
    ("AL", "Albania"),
    ("AG", "Algeria"),
    ("AQ", "American Samoa"),
    ("AN", "Andorra"),
    ("AO", "Angola"),
    ("AV", "Anguilla"),
    ("AY", "Antarctica"),
    ("AC", "Antigua and Barbuda"),
    ("AR", "Argentina"),
    ("AM", "Armenia"),
    ("AA", "Aruba"),
    ("AT", "Ashmore and Cartier Islands"),
    ("AS", "Australia"),
    ("AU", "Austria"),
    ("AJ", "Azerbaijan"),
    ("BF", "Bahamas, The"),
    ("BA", "Bahrain"),
    ("FQ", "Baker Island"),
    ("BG", "Bangladesh"),
    ("BB", "Barbados"),
    ("BS", "Bassas da India"),
    ("BO", "Belarus"),
    ("BE", "Belgium"),
    ("BH", "Belize"),
    ("BN", "Benin"),
    ("BD", "Bermuda"),
    ("BT", "Bhutan"),
    ("BL", "Bolivia"),
    ("BK", "Bosnia-Herzegovina"),
    ("BC", "Botswana"),
    ("BV", "Bouvet Island"),
    ("BR", "Brazil"),
    ("IO", "British Indian Ocean Territory"),
    ("VI", "British Virgin Islands"),
    ("BX", "Brunei"),
    ("BU", "Bulgaria"),
    ("UV", "Burkina Faso"),
    ("BY", "Burundi"),
    ("CB", "Cambodia"),
    ("CM", "Cameroon"),
    ("CA", "Canada"),
    ("CV", "Cape Verde"),
    ("CJ", "Cayman Islands"),
    ("CT", "Central African Republic"),
    ("CD", "Chad"),
    ("CI", "Chile"),
    ("CH", "China"),
    ("KT", "Christmas Island"),
    ("IP", "Clipperton Island"),
    ("CK", "Cocos Keeling Islands"),
    ("CO", "Colombia"),
    ("CN", "Comoros"),
    ("CF", "Congo"),
    ("CW", "Cook Islands"),
    ("CR", "Coral Sea Islands"),
    ("CS", "Costa Rica"),
    ("IV", "Cote dIvoire"),
    ("HR", "Croatia"),
    ("CU", "Cuba"),
    ("CY", "Cyprus"),
    ("EZ", "Czech Republic"),
    ("LO", "Czechoslovakia"),
    ("CG", "Democratic Republic of the Congo"),
    ("DA", "Denmark"),
    ("DX", "Dhekelia Sovereign Base Area"),
    ("DJ", "Djibouti"),
    ("DO", "Dominica"),
    ("DR", "Dominican Republic"),
    ("TT", "East Timor"),
    ("EC", "Ecuador"),
    ("EG", "Egypt"),
    ("ES", "El Salvador"),
    ("GV", "Equatorial Guinea"),
    ("EK", "Equatorial Guinea"),
    ("ER", "Eritrea"),
    ("EN", "Estonia"),
    ("ET", "Ethiopia"),
    ("PJ", "Etorofu, Habomai, Kunashiri and Shikotan Islands"),
    ("EU", "Europa Island"),
    ("FK", "Falkland Islands Islas Malvinas"),
    ("FO", "Faroe Islands"),
    ("FJ", "Fiji"),
    ("FI", "Finland"),
    ("FR", "France"),
    ("FG", "French Guiana"),
    ("FP", "French Polynesia"),
    ("FS", "French Southern and Antarctic Lands"),
    ("GB", "Gabon"),
    ("GA", "Gambia"),
    ("GZ", "Gaza Strip"),
    ("GG", "Georgia"),
    ("GM", "Germany"),
    ("GH", "Ghana"),
    ("GI", "Gibraltar"),
    ("GO", "Glorioso Islands"),
    ("GR", "Greece"),
    ("GL", "Greenland"),
    ("GJ", "Grenada"),
    ("GP", "Guadeloupe"),
    ("GQ", "Guam"),
    ("GT", "Guatemala"),
    ("GK", "Guernsey"),
    ("PU", "Guinea-Bissau"),
    ("GY", "Guyana"),
    ("HA", "Haiti"),
    ("HM", "Heard Island and McDonald Islands"),
    ("HO", "Honduras"),
    ("HK", "Hong Kong"),
    ("HQ", "Howland Island"),
    ("HU", "Hungary"),
    ("IC", "Iceland"),
    ("IN", "India"),
    ("ID", "Indonesia"),
    ("IR", "Iran"),
    ("IZ", "Iraq"),
    ("EI", "Ireland"),
    ("IM", "Isle of Man"),
    ("IS", "Israel"),
    ("IT", "Italy"),
    ("JM", "Jamaica"),
    ("JN", "Jan Mayen"),
    ("JA", "Japan"),
    ("DQ", "Jarvis Island"),
    ("JE", "Jersey"),
    ("JQ", "Johnston Atoll"),
    ("JO", "Jordan"),
    ("JU", "Juan de Nova Island"),
    ("KZ", "Kazakhstan"),
    ("KE", "Kenya"),
    ("KQ", "Kingman Reef"),
    ("KR", "Kiribati"),
    ("KV", "Kosovo"),
    ("KU", "Kuwait"),
    ("KG", "Kyrgyzstan"),
    ("LA", "Laos"),
    ("LG", "Latvia"),
    ("LE", "Lebanon"),
    ("LT", "Lesotho"),
    ("LI", "Liberia"),
    ("LY", "Libya"),
    ("LS", "Liechtenstein"),
    ("LH", "Lithuania"),
    ("LU", "Luxembourg"),
    ("MC", "Macau"),
    ("MK", "Macedonia"),
    ("MA", "Madagascar"),
    ("MI", "Malawi"),
    ("MY", "Malaysia"),
    ("MV", "Maldives"),
    ("ML", "Mali"),
    ("MT", "Malta"),
    ("RM", "Marshall Islands"),
    ("MB", "Martinique"),
    ("MR", "Mauritania"),
    ("MP", "Mauritius"),
    ("MF", "Mayotte"),
    ("MX", "Mexico"),
    ("FM", "Micronesia"),
    ("MQ", "Midway Islands"),
    ("MD", "Moldova"),
    ("MN", "Monaco"),
    ("MG", "Mongolia"),
    ("MJ", "Montenegro"),
    ("MH", "Montserrat"),
    ("MO", "Morocco"),
    ("MZ", "Mozambique"),
    ("BM", "Myanmar"),
    ("WA", "Namibia"),
    ("NR", "Nauru"),
    ("BQ", "Navassa Island"),
    ("NP", "Nepal"),
    ("NL", "Netherlands"),
    ("NT", "Netherlands Antilles"),
    ("NC", "New Caledonia"),
    ("NZ", "New Zealand"),
    ("NU", "Nicaragua"),
    ("NG", "Niger"),
    ("NI", "Nigeria"),
    ("NE", "Niue"),
    ("NM", "No Mans Land"),
    ("NF", "Norfolk Island"),
    ("KN", "North Korea"),
    ("CQ", "Northern Mariana Islands"),
    ("NO", "Norway"),
    ("OS", "Oceans"),
    ("MU", "Oman"),
    ("PK", "Pakistan"),
    ("PS", "Palau"),
    ("LQ", "Palmyra Atoll"),
    ("PM", "Panama"),
    ("PP", "Papua New Guinea"),
    ("PF", "Paracel Islands"),
    ("PA", "Paraguay"),
    ("PE", "Peru"),
    ("RP", "Philippines"),
    ("PC", "Pitcairn Islands"),
    ("PL", "Poland"),
    ("PO", "Portugal"),
    ("RQ", "Puerto Rico"),
    ("QA", "Qatar"),
    ("RE", "Reunion"),
    ("RO", "Romania"),
    ("RS", "Russia"),
    ("RW", "Rwanda"),
    ("SH", "Saint Helena"),
    ("SC", "Saint Kitts and Nevis"),
    ("ST", "Saint Lucia"),
    ("RN", "Saint Martin"),
    ("SB", "Saint Pierre and Miquelon"),
    ("VC", "Saint Vincent and the Grenadines"),
    ("TB", "Saint-Barthelemy Island"),
    ("WS", "Samoa"),
    ("SM", "San Marino"),
    ("TP", "Sao Tome and Principe"),
    ("SA", "Saudi Arabia"),
    ("SG", "Senegal"),
    ("RI", "Serbia"),
    ("SE", "Seychelles"),
    ("SL", "Sierra Leone"),
    ("SN", "Singapore"),
    ("SI", "Slovenia"),
    ("BP", "Solomon Islands"),
    ("SO", "Somalia"),
    ("SF", "South Africa"),
    ("SX", "South Georgia and the South Sandwich Islands"),
    ("KS", "South Korea"),
    ("OD", "South Sudan"),
    ("SP", "Spain"),
    ("PG", "Spratly Islands"),
    ("CE", "Sri Lanka"),
    ("SU", "Sudan"),
    ("NS", "Suriname"),
    ("SV", "Svalbard"),
    ("WZ", "Swaziland"),
    ("SW", "Sweden"),
    ("SZ", "Switzerland"),
    ("SY", "Syria"),
    ("TW", "Taiwan"),
    ("TI", "Tajikistan"),
    ("TZ", "Tanzania"),
    ("TH", "Thailand"),
    ("TO", "Togo"),
    ("TL", "Tokelau"),
    ("TN", "Tonga"),
    ("TD", "Trinidad and Tobago"),
    ("TE", "Tromelin Island"),
    ("TS", "Tunisia"),
    ("TU", "Turkey"),
    ("TX", "Turkmenistan"),
    ("TK", "Turks and Caicos Islands"),
    ("TV", "Tuvalu"),
    ("UG", "Uganda"),
    ("UP", "Ukraine"),
    ("UF", "Undersea Features"),
    ("UU", "Undesignated Sovereignty"),
    ("AE", "United Arab Emirates"),
    ("UK", "United Kingdom"),
    ("US", "United States"),
    ("UY", "Uruguay"),
    ("UZ", "Uzbekistan"),
    ("NH", "Vanuatu"),
    ("VT", "Vatican City"),
    ("VE", "Venezuela"),
    ("VM", "Vietnam, Democratic Republic of"),
    ("VQ", "Virgin Islands"),
    ("WQ", "Wake Island"),
    ("WF", "Wallis and Futuna"),
    ("WE", "West Bank"),
    ("WI", "Western Sahara"),
    ("YM", "Yemen"),
    ("ZA", "Zambia"),
    ("ZI", "Zimbabwe")
]

    for country_code, country_name in fips_country_data:
        insert_query = "INSERT INTO fips_country (country_code, country_name) VALUES (%s, %s)"
        cursor.execute(insert_query, (country_code, country_name))
    print("Data loaded successfully into fips_country.")
    conn.commit()

except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print(traceback.format_exc())
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()