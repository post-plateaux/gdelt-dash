import requests

def get_translation(text):
    try:
        detect_response = requests.post("http://libretranslate:5000/detect", data={"q": text}, timeout=30)
        detect_data = detect_response.json()
        if isinstance(detect_data, list) and len(detect_data) > 0:
            detected_language = detect_data[0].get("language", "en")
        else:
            detected_language = "en"
    except Exception:
        detected_language = "en"
    if detected_language == "en":
        return text

    retries = 2  # Two additional attempts
    for attempt in range(retries + 1):
        try:
            translate_response = requests.post(
                "http://libretranslate:5000/translate",
                data={
                    "q": text,
                    "source": detected_language,
                    "target": "en",
                    "format": "text"
                },
                timeout=90
            )
            translate_response.raise_for_status()
            translate_data = translate_response.json()
            translated_text = translate_data.get("translatedText", text)
            return translated_text
        except Exception:
            if attempt < retries:
                continue
            else:
                return text

if __name__ == '__main__':                                                                              
 import sys                                                                                          
 if len(sys.argv) > 1:                                                                               
     input_text = " ".join(sys.argv[1:])                                                             
     translated = get_translation(input_text)                                                        
     print(translated)                                                                               
 else:                                                                                               
     print("Usage: python get_translation.py <text>")  
