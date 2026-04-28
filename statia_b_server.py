import socket
from crypto_service import OpenSSLService

def start_server(host='127.0.0.1', port=65432):
    print("\n   Statia B (Receptor)   \n")
    
    parola_cheie = input("Introduceti cheia secreta asteptata: ")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"\n[Server] Ascult pe portul {port} si astept fisiere...")
        
        conn, addr = s.accept()
        with conn:
            print(f"[Server] Conexiune stabilita cu Statia A ({addr[0]})")
            
            cale_iesire_criptat = "fisier_receptionat.enc"
            blocuri_primite = 0
            
            print("[Server] Receptionez datele...")
            with open(cale_iesire_criptat, "wb") as f:
                while True:
                    # Citim cate un bloc de 4096 bytes (4KB)
                    bloc = conn.recv(4096)
                    if not bloc:
                        break # Daca nu mai sunt date, oprim citirea
                    f.write(bloc)
                    blocuri_primite += 1
            
            print(f"[Server] Succes! Am receptionat si recompus {blocuri_primite} blocuri.")
            
            print("[Server] Incepem decriptarea fisierului...")
            crypto = OpenSSLService()
            cale_iesire_decriptat = "mesaj_final_decriptat.txt"
            
            succes, timp, mem = crypto.decripteaza_aes_256(cale_iesire_criptat, cale_iesire_decriptat, parola_cheie)
            
            if succes:
                print(f"\nDecriptare reusita! Fisierul a fost salvat ca: {cale_iesire_decriptat}")
            else:
                print("\nEroare la decriptare: Cheie gresita sau date corupte.")

if __name__ == "__main__":
    start_server()