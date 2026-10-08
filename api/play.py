import re
import cloudscraper
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    
    def extract_daddylive_stream(self, url):
        # Inizializziamo cloudscraper per bypassare i blocchi anti-bot
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        try:
            # 1. Scarichiamo la pagina principale
            response = scraper.get(url, timeout=15)
            
            # 2. Cerchiamo l'iframe
            iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', response.text, re.IGNORECASE)
            if not iframe_match:
                return None
                
            iframe_url = iframe_match.group(1)
            if iframe_url.startswith('/'):
                iframe_url = "https://daddylive.mov" + iframe_url
                
            # 3. Entriamo nell'iframe
            headers = {"Referer": "https://daddylive.mov/"}
            iframe_resp = scraper.get(iframe_url, headers=headers, timeout=15)
            
            # 4. Cerchiamo il file .m3u8
            m3u8_match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', iframe_resp.text)
            
            if m3u8_match:
                return m3u8_match.group(1).replace('\\/', '/')
                
        except Exception as e:
            print(f"Eccezione: {str(e)}")
            
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

        if canale == "italia1":
            target_url = "https://daddylive.mov/live/stream=Italia-1-IT&source=list8-7j"
            stream_url = self.extract_daddylive_stream(target_url)
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(f"Errore: Canale '{canale}' non trovato.".encode())
            return

        if stream_url:
            self.send_response(302)
            self.send_header('Location', stream_url)
            self.end_headers()
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Errore: Impossibile estrarre il flusso. Blocco Cloudflare attivo.")
