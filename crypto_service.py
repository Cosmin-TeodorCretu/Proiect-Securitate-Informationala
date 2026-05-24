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
            print(f"\n[Eroare Criptare OpenSSL]: {rezultat.stderr}")
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
    
    #w14
    def cripteaza_rsa(self, cale_intrare: str, cale_iesire: str, cale_cheie_publica: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()
        comanda = [
            "openssl", "pkeyutl", "-encrypt", "-pubin",
            "-inkey", cale_cheie_publica,
            "-pkeyopt", "rsa_padding_mode:oaep",
            "-in", cale_intrare,
            "-out", cale_iesire
        ]
        rezultat = subprocess.run(comanda, capture_output=True, text=True)
        end_time = time.perf_counter()
        
        timp_executie_ms = (end_time - start_time) * 1000
        memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0 if os.path.exists(cale_intrare) else 0.0

        if rezultat.returncode != 0:
            print(f"\n[Eroare Criptare RSA OpenSSL]: {rezultat.stderr}")
            return False, 0.0, 0.0
        return True, timp_executie_ms, memorie_estimata_kb

    def decripteaza_rsa(self, cale_intrare: str, cale_iesire: str, cale_cheie_privata: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()
        comanda = [
            "openssl", "pkeyutl", "-decrypt",
            "-inkey", cale_cheie_privata,
            "-pkeyopt", "rsa_padding_mode:oaep",
            "-in", cale_intrare,
            "-out", cale_iesire
        ]
        rezultat = subprocess.run(comanda, capture_output=True, text=True)
        end_time = time.perf_counter()
        
        timp_executie_ms = (end_time - start_time) * 1000
        memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0 if os.path.exists(cale_intrare) else 0.0

        if rezultat.returncode != 0:
            print(f"\n[Eroare Decriptare RSA OpenSSL]: {rezultat.stderr}")
            return False, 0.0, 0.0
        return True, timp_executie_ms, memorie_estimata_kb


class PyCryptodomeService:
    #w14
    def __init__(self):
        self.nume = "PyCryptodome"
        try:
            from Crypto.Cipher import AES
            self.este_instalat = True
        except ImportError:
            self.este_instalat = False
            print("\nATENTIE: PyCryptodome nu este instalat. Rulati: pip install pycryptodome")

    def _deriveaza_cheie_si_iv(self, parola_cheie: str):
        import hashlib
        cheie = hashlib.sha256(parola_cheie.encode()).digest()
        iv = hashlib.md5(parola_cheie.encode()).digest()
        return cheie, iv

    def cripteaza_aes_256(self, cale_intrare: str, cale_iesire: str, parola_cheie: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()

        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad

            cheie, iv = self._deriveaza_cheie_si_iv(parola_cheie)

            with open(cale_intrare, 'rb') as f:
                date_originale = f.read()

            cipher = AES.new(cheie, AES.MODE_CBC, iv)
            date_criptate = cipher.encrypt(pad(date_originale, AES.block_size))

            with open(cale_iesire, 'wb') as f:
                f.write(iv + date_criptate)

            end_time = time.perf_counter()
            timp_executie_ms = (end_time - start_time) * 1000
            memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0

            return True, timp_executie_ms, memorie_estimata_kb

        except Exception as e:
            print(f"\n[Eroare Criptare PyCryptodome]: {e}")
            return False, 0.0, 0.0

    def decripteaza_aes_256(self, cale_intrare: str, cale_iesire: str, parola_cheie: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()

        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad

            cheie, iv = self._deriveaza_cheie_si_iv(parola_cheie)

            with open(cale_intrare, 'rb') as f:
                continut = f.read()

            iv_din_fisier = continut[:16]
            date_criptate = continut[16:]

            cipher = AES.new(cheie, AES.MODE_CBC, iv_din_fisier)
            date_decriptate = unpad(cipher.decrypt(date_criptate), AES.block_size)

            with open(cale_iesire, 'wb') as f:
                f.write(date_decriptate)

            end_time = time.perf_counter()
            timp_executie_ms = (end_time - start_time) * 1000
            memorie_estimata_kb = os.path.getsize(cale_intrare) / 1024.0

            return True, timp_executie_ms, memorie_estimata_kb

        except Exception as e:
            print(f"\n[Eroare Decriptare PyCryptodome]: Parola gresita sau fisier corupt.")
            return False, 0.0, 0.0
        
    #w14
    def cripteaza_rsa(self, cale_intrare: str, cale_iesire: str, cale_cheie_publica: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()
        try:
            from Crypto.PublicKey import RSA
            from Crypto.Cipher import PKCS1_OAEP

            with open(cale_cheie_publica, 'r') as f:
                cheie_pub = RSA.import_key(f.read())

            cipher = PKCS1_OAEP.new(cheie_pub)
            with open(cale_intrare, 'rb') as f:
                date_originale = f.read()

            date_criptate = cipher.encrypt(date_originale)
            with open(cale_iesire, 'wb') as f:
                f.write(date_criptate)

            end_time = time.perf_counter()
            return True, (end_time - start_time) * 1000, os.path.getsize(cale_intrare) / 1024.0
        except Exception as e:
            print(f"\n[Eroare Criptare RSA PyCryptodome]: {e}")
            return False, 0.0, 0.0

    def decripteaza_rsa(self, cale_intrare: str, cale_iesire: str, cale_cheie_privata: str):
        if not self.este_instalat:
            return False, 0.0, 0.0

        start_time = time.perf_counter()
        try:
            from Crypto.PublicKey import RSA
            from Crypto.Cipher import PKCS1_OAEP

            with open(cale_cheie_privata, 'r') as f:
                cheie_priv = RSA.import_key(f.read())

            cipher = PKCS1_OAEP.new(cheie_priv)
            with open(cale_intrare, 'rb') as f:
                date_criptate = f.read()

            date_decriptate = cipher.decrypt(date_criptate)
            with open(cale_iesire, 'wb') as f:
                f.write(date_decriptate)

            end_time = time.perf_counter()
            return True, (end_time - start_time) * 1000, os.path.getsize(cale_intrare) / 1024.0
        except Exception as e:
            print(f"\n[Eroare Decriptare RSA PyCryptodome]: {e}")
            return False, 0.0, 0.0