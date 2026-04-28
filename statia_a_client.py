import socket
import os
import time
from crypto_service import OpenSSLService

def send_file(host='127.0.0.1', port=65432):
    print("\n   Statia A (Expeditor)   \n")
    
    cale_fisier = input("Ce fisier doriti sa trimiteti? (ex: test.txt): ")
    if not os.path.exists(cale_fisier):
        print("[Eroare] Fisierul nu exista!")
        return

    parola_cheie = input("Introduceti cheia secreta de criptare: ")
    cale_criptat = cale_fisier + ".send.enc"

    print("\n[Pasul 1] Criptam fisierul...")
    crypto = OpenSSLService()
    succes, timp, mem = crypto.cripteaza_aes_256(cale_fisier, cale_criptat, parola_cheie)

    if not succes:
        print("[Eroare] Criptarea a esuat. Oprim transmisia.")
        return
    print("[Succes] Fisier criptat pregatit pentru trimitere.")

    print(f"\n[Pasul 2] Ne conectam la Statia B ({host}:{port})...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print("[Conectat] Incepem trimiterea fisierului pe bucati (blocuri)...")

            dimensiune_bloc = 4096 # Impartim in blocuri de 4 KB
            blocuri_trimise = 0

            with open(cale_criptat, "rb") as f:
                while True:
                    bloc = f.read(dimensiune_bloc)
                    if not bloc:
                        break # Am ajuns la finalul fisierului
                    
                    s.sendall(bloc)
                    blocuri_trimise += 1
                    time.sleep(0.05) # O mica pauza artificiala ca sa simulam reteaua
            
            print(f"\nTransmisie finalizata! Au fost trimise {blocuri_trimise} blocuri.")
            
    except ConnectionRefusedError:
        print("\n[Eroare] Statia B nu raspunde. Asigurati-va ca ati pornit statia_b_server.py inainte!")

if __name__ == "__main__":
    send_file()