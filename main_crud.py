import os
import time
from database import CryptoDBManager
from models import TipAlgoritm, TipOperatie
import hashlib

def curata_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')

def afiseaza_meniu_principal():
    print("\n   Sistem Management Criptare & Performanta")
    print("\n1. Administrare (Framework-uri si Algoritmi)")
    print("2. Management Chei (Adaugare, Vizualizare, Modificare)")
    print("3. Operatiuni Fisiere (Criptare/Decriptare)")
    print("4. Rapoarte Performanta")
    print("0. Iesire")
    return input("\nSelectati o optiune: ")

def submeniu_administrare(db):
    curata_ecran()
    print("   Administrare Sistem\n")
    print("1. Adauga Framework (ex: OpenSSL, PyCryptodome)")
    print("2. Adauga Algoritm (ex: AES-256, RSA-2048)")
    print("3. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        nume = input("\nIntroduceti numele framework-ului: ")
        db.adauga_framework(nume)
    elif opt == "2":
        nume = input("\nIntroduceti numele algoritmului: ")
        print("\nTip algoritm: 1. Simetric | 2. Asimetric")
        t = input("Alegere: ")
        tip = TipAlgoritm.SIMETRIC if t == "1" else TipAlgoritm.ASIMETRIC
        db.adauga_algoritm(nume, tip)

def submeniu_chei(db):
    curata_ecran()
    print("   Management Chei\n")
    print("1. Adauga Cheie Noua")
    print("2. Vizualizeaza Toate Cheile")
    print("3. Actualizeaza Valoare Cheie")
    print("4. Sterge o Cheie (Delete)")
    print("5. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        valoare = input("\nIntroduceti valoarea cheii sau calea catre fisierul cheie: ")
        id_alg = input("ID Algoritm asociat: ")
        db.adauga_cheie(valoare, int(id_alg))
    elif opt == "2":
        chei = db.obtine_toate_cheile()
        print("\n Lista Chei ")
        if not chei:
            print("Nu exista chei in baza de date.")
        for c in chei:
            print(f"ID: {c.id} | Cheie: {c.valoare_sau_cale} | Algoritm: {c.algoritm.nume}")
        input("\nApasa Enter pentru a continua...")
    elif opt == "3":
        id_cheie = input("\nIntroduceti ID-ul cheii pe care vreti sa o modificati: ")
        valoare_noua = input("Introduceti noua valoare: ")
        db.actualizeaza_cheie(int(id_cheie), valoare_noua)
    elif opt == "4":
        id_cheie = input("\nIntroduceti ID-ul cheii pe care vreti sa o stergeti: ")
        db.sterge_cheie(int(id_cheie))

from crypto_service import OpenSSLService # adauga asta sus langa celelalte importuri

def submeniu_fisiere(db):
    curata_ecran()
    print("   Operatiuni Fisiere\n")
    
    cale_fisier = input("1. Introduceti calea fisierului de criptat (ex: secret.txt): ")
    if not os.path.exists(cale_fisier):
        print("\nEroare: Fisierul nu exista pe disc!")
        input("\nApasa Enter pentru a continua...")
        return

    chei = db.obtine_toate_cheile()
    if not chei:
        print("\nEroare: Nu aveti nicio cheie in baza de date. Adaugati una intai!")
        input("\nApasa Enter pentru a continua...")
        return

    print("\nAlegeti o cheie pentru criptare")
    for c in chei:
        print(f"[{c.id}] Cheie: {c.valoare_sau_cale} (Algoritm: {c.algoritm.nume})")
        
    id_ales = input("\nIntroduceti ID-ul cheii dorite: ")
    
    cheie_aleasa = next((c for c in chei if str(c.id) == id_ales), None)
    if not cheie_aleasa:
        print("ID invalid.")
        return

    cale_iesire = cale_fisier + ".enc"
    
    print("\nIncepem criptarea cu OpenSSL...")
    crypto = OpenSSLService()
    
    if "AES" in cheie_aleasa.algoritm.nume:
        succes, timp_ms, mem_kb = crypto.cripteaza_aes_256(cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale)
        
        if succes:
            print(f"\nSucces! Fisier criptat creat: {cale_iesire}")
            print(f"Timp executie: {timp_ms:.2f} ms | Memorie est: {mem_kb:.2f} KB")
            
            hash_md5 = hashlib.md5()
            with open(cale_fisier, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            valoare_hash = hash_md5.hexdigest()

            fisier_db = db.adauga_fisier(cale_fisier, cale_iesire, cheie_aleasa.id, valoare_hash)
            if fisier_db:
                db.adauga_performanta(fisier_db.id, 1, TipOperatie.CRIPTARE, timp_ms, mem_kb)
                print("Datele despre performanta au fost salvate in BD!")
    else:
        print(f"\nAlgoritmul {cheie_aleasa.algoritm.nume} nu este implementat inca.")
        
    input("\nApasa Enter pentru a continua...")

def main():
    db = CryptoDBManager()
    
    while True:
        opt = afiseaza_meniu_principal()
        
        if opt == "1":
            submeniu_administrare(db)
        elif opt == "2":
            submeniu_chei(db)
        elif opt == "3":
            submeniu_fisiere(db)
        elif opt == "4":
            print("\n[IN LUCRU]: Aici vor fi afisate performantele salvate.")
            input("\nApasa Enter pentru a continua...")
        elif opt == "0":
            print("\nInchidere aplicatie...")
            break
        else:
            print("\nOptiune invalida! Incearca din nou.")
            time.sleep(1)
            curata_ecran()

if __name__ == "__main__":
    main()