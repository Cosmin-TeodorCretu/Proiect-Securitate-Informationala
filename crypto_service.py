import subprocess
import time
import os

class OpenSSLService:
    def __init__(self):
        try:
            subprocess.run(["openssl", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.este_instalat = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.este_instalat = False
            print("\nATENTIE: OpenSSL nu a fost gasit in sistem.")

    def cripteaza_aes_256(self, cale_intrare: str, cale_iesire: str, parola_cheie: str):
        if not self.este_instalat:
             return False, 0.0, 0.0
             
        start_time = time.perf_counter()
        
        comanda = [
            "openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
            "-in", cale_intrare, 
            "-out", cale_iesire,
            "-pass", f"pass:{parola_cheie}"
        ]
        
        rezultat = subprocess.run(comanda, capture_output=True, text=True)
        
        end_time = time.perf_counter()
        timp_executie_ms = (end_time - start_time) * 1000
        
        memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0 if os.path.exists(cale_intrare) else 0.0

        if rezultat.returncode != 0:
            print(f"\n[Eroare Criptare]: {rezultat.stderr}")
            return False, 0.0, 0.0
            
        return True, timp_executie_ms, memorie_estimata_kb

    def decripteaza_aes_256(self, cale_intrare: str, cale_iesire: str, parola_cheie: str):
         if not self.este_instalat:
             return False, 0.0, 0.0
             
         start_time = time.perf_counter()
         
         comanda = [
            "openssl", "enc", "-d", "-aes-256-cbc", "-salt", "-pbkdf2",
            "-in", cale_intrare, 
            "-out", cale_iesire,
            "-pass", f"pass:{parola_cheie}"
        ]
         
         rezultat = subprocess.run(comanda, capture_output=True, text=True)
         
         end_time = time.perf_counter()
         timp_executie_ms = (end_time - start_time) * 1000
         memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0 if os.path.exists(cale_intrare) else 0.0

         if rezultat.returncode != 0:
            print(f"\n[Eroare Decriptare]: Parola este gresita sau fisierul corupt.")
            return False, 0.0, 0.0
            
         return True, timp_executie_ms, memorie_estimata_kb

class PyCryptodomeService:
    def __init__(self):
        self.nume = "PyCryptodome Alternativ"

    def cripteaza_aes_256(self, cale_intrare: str, cale_iesire: str, parola_cheie: str):
        print(f"\n[Framework Alternativ] Simulam criptarea cu PyCryptodome pentru {cale_intrare}...")
        start_time = time.perf_counter()
        
        try:
            with open(cale_intrare, 'rb') as f_in:
                date = f_in.read()
            with open(cale_iesire, 'wb') as f_out:
                f_out.write(b"CRIPTAT_CU_PYCRYPTODOME_" + date)
                
            end_time = time.perf_counter()
            timp_executie_ms = (end_time - start_time) * 1000
            memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0
            
            return True, timp_executie_ms, memorie_estimata_kb
        except Exception as e:
            print(f"Eroare framework alternativ: {e}")
            return False, 0.0, 0.0