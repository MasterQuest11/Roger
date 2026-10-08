import re
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    
    def extract_daddylive_stream(self, url):
        # Simuliamo di essere un browser reale per non farci bloccare subito
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://daddylive.mov/"
        }
        
        try:
            # 1. Scarichiamo il codice sorgente della pagina principale
            response = requests.get(url, headers=headers, timeout=10)
            
            # 2. Cerchiamo il link dell'iframe del player (spesso ospitato su altri domini come dlhd o simili)
            iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', response.text, re.IGNORECASE)
            if not iframe_match:
                print("Nessun iframe trovato")
                return None
                
            iframe_url = iframe_match.group(1)
            if iframe_url.startswith('/'):
                iframe_url = "https://daddylive.mov" + iframe_url
                
            # 3. Entriamo nell'iframe e ne scarichiamo il codice
            iframe_resp = requests.get(iframe_url, headers=headers, timeout=10)
            
            # 4. Cerchiamo il fatidico link .m3u8 dentro il player
            m3u8_match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', iframe_resp.text)
            
            if m3u8_match:
                # Ripuliamo il link da eventuali caratteri di escape aggiunti dal javascript
                return m3u8_match.group(1).replace('\\/', '/')
                
        except Exception as e:
            print(f"Errore durante l'estrazione: {e}")
            
        return None

    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        
        if 'ch' not in query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Errore: parametro 'ch' mancante.")
            return

        canale = query['ch'][0].lower()
        stream_url = ""

        # LOGICA DEI CANALI
        if canale == "italia1":
            target_url = "https://daddylive.mov/live/stream=Italia-1-IT&source=list8-7j"
            stream_url = self.extract_daddylive_stream(target_url)
            
        elif canale == "canale2":
            # Per i test futuri
            stream_url = "https://test-streams.mux.dev/test_001/stream.m3u8"
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(f"Errore: Canale '{canale}' non trovato.".encode())
            return

        # ESECUZIONE DEL REINDIRIZZAMENTO
        if stream_url:
            self.send_response(302)
            self.send_header('Location', stream_url)
            self.end_headers()
        else:
            # Se l'estrazione fallisce (es. cambio layout del sito), restituiamo errore 500
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Errore: Impossibile estrarre il flusso m3u8 dal sito.")
