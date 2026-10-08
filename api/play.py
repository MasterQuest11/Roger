from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Analizziamo l'URL che il player ha richiesto
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        
        # 2. Controlliamo se c'è il parametro 'ch' (es. ?ch=canale1)
        if 'ch' not in query:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Errore: parametro 'ch' mancante. Specifica un canale.".encode())
            return

        canale = query['ch'][0].lower()
        stream_url = ""

        # 3. Logica di smistamento (Routing) dei canali
        if canale == "canale1":
            # Qui in futuro metteremo la logica di estrazione vera e propria
            # Per ora usiamo un flusso di test (Big Buck Bunny)
            stream_url = "https://cdnlivetv.tv/secure/api/v1/6a288d2d81d8192bb76ce19f/playlist.m3u8?token=NmEyODhkMmQ4MWQ4MTkyYmI3NmNlMTlmOjE3OTE0Nzk5OTE0MTE6Y2RubGl2ZXR2LnR2OjVkODViYWUyNTBhZjRkOWMuNjIyZTU0OTQ1MmQ5ZDRiOWU3ODhiZGZhNTQxNGE0ZGVhYzdiYTdkOTdmYWUyYWUzOGYzOTc4NWNmOGIyZWE3YQ"
            
        elif canale == "canale2":
            # Altro flusso di test
            stream_url = "https://test-streams.mux.dev/test_001/stream.m3u8"
            
        else:
            # Se il canale non è nella lista, diamo errore
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Errore: Canale '{canale}' non trovato.".encode())
            return

        # 4. Il Reindirizzamento Magico (HTTP 302)
        # Diciamo al player: "Il video che cerchi si trova a questo nuovo indirizzo"
        self.send_response(302)
        self.send_header('Location', stream_url)
        self.end_headers()
