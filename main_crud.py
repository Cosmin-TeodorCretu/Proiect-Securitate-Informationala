import os
import time
import hashlib
from database import CryptoDBManager
from models import TipAlgoritm, TipOperatie
from crypto_service import OpenSSLService, PyCryptodomeService


def curata_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')


def afiseaza_meniu_principal():
    print("   Sistem Management Criptare & Performanta")
    print("\n1. Administrare (Framework-uri si Algoritmi)")
    print("2. Management Chei (Adaugare, Vizualizare, Modificare)")
    print("3. Operatiuni Fisiere (Criptare/Decriptare)")
    print("4. Rapoarte Performanta")
    print("0. Iesire")
    return input("\nSelectati o optiune: ")


def submeniu_administrare(db):
    curata_ecran()
    print("   Administrare Sistem")
    print("\n1. Adauga Framework (ex: OpenSSL, PyCryptodome)")
    print("2. Adauga Algoritm (ex: AES-256, RSA-2048)")
    print("3. Vizualizeaza Framework-uri si Algoritmi existenti")
    print("4. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        nume = input("\nIntroduceti numele framework-ului: ")
        db.adauga_framework(nume)
        input("\nApasa Enter pentru a continua...")

    elif opt == "2":
        nume = input("\nIntroduceti numele algoritmului: ")
        print("\nTip algoritm: 1. Simetric | 2. Asimetric")
        t = input("Alegere: ")
        tip = TipAlgoritm.SIMETRIC if t == "1" else TipAlgoritm.ASIMETRIC
        db.adauga_algoritm(nume, tip)
        input("\nApasa Enter pentru a continua...")

    elif opt == "3":
        frameworks = db.obtine_toate_frameworkurile()
        print("\n--- Framework-uri ---")
        if not frameworks:
            print("Nu exista framework-uri in baza de date.")
        for fw in frameworks:
            print(f"  ID: {fw.id} | Nume: {fw.nume}")

        from models import Algoritm
        algoritmi = db.session.query(Algoritm).all()
        print("\n--- Algoritmi ---")
        if not algoritmi:
            print("Nu exista algoritmi in baza de date.")
        for alg in algoritmi:
            print(f"  ID: {alg.id} | Nume: {alg.nume} | Tip: {alg.tip.value}")
        input("\nApasa Enter pentru a continua...")


def submeniu_chei(db):
    curata_ecran()
    print("   Management Chei")
    print("\n1. Adauga Cheie Noua")
    print("2. Vizualizeaza Toate Cheile")
    print("3. Actualizeaza Valoare Cheie")
    print("4. Sterge o Cheie (Delete)")
    print("5. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        valoare = input("\nIntroduceti valoarea cheii sau calea catre fisierul cheie: ")
        id_alg = input("ID Algoritm asociat: ")
        try:
            db.adauga_cheie(valoare, int(id_alg))
        except ValueError:
            print("Eroare: ID-ul trebuie sa fie un numar.")
        input("\nApasa Enter pentru a continua...")

    elif opt == "2":
        chei = db.obtine_toate_cheile()
        print("\n--- Lista Chei ---")
        if not chei:
            print("Nu exista chei in baza de date.")
        for c in chei:
            print(f"  ID: {c.id} | Cheie: {c.valoare_sau_cale} | Algoritm: {c.algoritm.nume}")
        input("\nApasa Enter pentru a continua...")

    elif opt == "3":
        id_cheie = input("\nIntroduceti ID-ul cheii pe care vreti sa o modificati: ")
        valoare_noua = input("Introduceti noua valoare: ")
        try:
            db.actualizeaza_cheie(int(id_cheie), valoare_noua)
        except ValueError:
            print("Eroare: ID-ul trebuie sa fie un numar.")
        input("\nApasa Enter pentru a continua...")

    elif opt == "4":
        id_cheie = input("\nIntroduceti ID-ul cheii pe care vreti sa o stergeti: ")
        try:
            db.sterge_cheie(int(id_cheie))
        except ValueError:
            print("Eroare: ID-ul trebuie sa fie un numar.")
        input("\nApasa Enter pentru a continua...")


def _calculeaza_hash_md5(cale_fisier: str) -> str:
    """Calculeaza hash-ul MD5 al unui fisier."""
    hash_md5 = hashlib.md5()
    with open(cale_fisier, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _alege_cheie(db):
    """Afiseaza cheile disponibile si returneaza cheia aleasa de utilizator."""
    chei = db.obtine_toate_cheile()
    if not chei:
        print("\nEroare: Nu aveti nicio cheie in baza de date. Adaugati una intai!")
        return None

    print("\nChei disponibile:")
    for c in chei:
        print(f"  [{c.id}] Cheie: {c.valoare_sau_cale} (Algoritm: {c.algoritm.nume})")

    id_ales = input("\nIntroduceti ID-ul cheii dorite: ")
    cheie_aleasa = next((c for c in chei if str(c.id) == id_ales), None)
    if not cheie_aleasa:
        print("Eroare: ID invalid.")
    return cheie_aleasa


def _alege_framework(db):
    """Afiseaza framework-urile disponibile si returneaza cel ales."""
    frameworks = db.obtine_toate_frameworkurile()
    if not frameworks:
        print("\nEroare: Nu aveti niciun framework in baza de date.")
        return None, None

    print("\nFramework-uri disponibile:")
    for fw in frameworks:
        print(f"  [{fw.id}] {fw.nume}")

    id_ales = input("\nAlegeti framework-ul (ID): ")
    fw_ales = next((fw for fw in frameworks if str(fw.id) == id_ales), None)
    if not fw_ales:
        print("Eroare: ID invalid.")
        return None, None

    if "openssl" in fw_ales.nume.lower():
        return fw_ales, OpenSSLService()
    elif "pycryptodome" in fw_ales.nume.lower() or "pyc" in fw_ales.nume.lower():
        return fw_ales, PyCryptodomeService()
    else:
        print(f"\nAtentie: Nu exista implementare pentru '{fw_ales.nume}'. Se foloseste OpenSSL implicit.")
        return fw_ales, OpenSSLService()


def submeniu_criptare(db):
    curata_ecran()

    print("   Criptare Fisier")

    cale_fisier = input("\nIntroduceti calea fisierului de criptat (ex: test.txt): ")
    if not os.path.exists(cale_fisier):
        print("\nEroare: Fisierul nu exista pe disc!")
        input("\nApasa Enter pentru a continua...")
        return

    cheie_aleasa = _alege_cheie(db)
    if not cheie_aleasa:
        input("\nApasa Enter pentru a continua...")
        return

    fw_ales, crypto = _alege_framework(db)
    if not fw_ales:
        input("\nApasa Enter pentru a continua...")
        return

    if "AES" not in cheie_aleasa.algoritm.nume:
        print(f"\nAlgoritmul {cheie_aleasa.algoritm.nume} nu este suportat inca.")
        input("\nApasa Enter pentru a continua...")
        return

    cale_iesire = cale_fisier + ".enc"
    print(f"\nSe cripteaza cu {fw_ales.nume}...")

    #w14
    if cheie_aleasa.algoritm.tip == TipAlgoritm.SIMETRIC:
        succes, timp_ms, mem_kb = crypto.cripteaza_aes_256(
            cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
        )
    elif cheie_aleasa.algoritm.tip == TipAlgoritm.ASIMETRIC:
        succes, timp_ms, mem_kb = crypto.cripteaza_rsa(
            cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
        )
    # succes, timp_ms, mem_kb = crypto.cripteaza_aes_256(
    #     cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
    # )

    if succes:
        print(f"\nSucces! Fisier criptat creat: {cale_iesire}")
        print(f"Timp executie: {timp_ms:.2f} ms | Marime fisier original: {mem_kb:.2f} KB")

        valoare_hash = _calculeaza_hash_md5(cale_fisier)
        print(f"Hash MD5 fisier original: {valoare_hash}")

        fisier_db = db.adauga_fisier(cale_fisier, cale_iesire, cheie_aleasa.id, valoare_hash)
        if fisier_db:
            db.adauga_performanta(fisier_db.id, fw_ales.id, TipOperatie.CRIPTARE, timp_ms, mem_kb)
            print("Datele despre performanta au fost salvate in baza de date!")
    else:
        print("\nCriptarea a esuat.")

    input("\nApasa Enter pentru a continua...")


def submeniu_decriptare(db):
    curata_ecran()
    print("   Decriptare Fisier")

    cale_fisier = input("\nIntroduceti calea fisierului criptat (ex: test.txt.enc): ")
    if not os.path.exists(cale_fisier):
        print("\nEroare: Fisierul nu exista pe disc!")
        input("\nApasa Enter pentru a continua...")
        return

    cheie_aleasa = _alege_cheie(db)
    if not cheie_aleasa:
        input("\nApasa Enter pentru a continua...")
        return

    fw_ales, crypto = _alege_framework(db)
    if not fw_ales:
        input("\nApasa Enter pentru a continua...")
        return

    if "AES" not in cheie_aleasa.algoritm.nume:
        print(f"\nAlgoritmul {cheie_aleasa.algoritm.nume} nu este suportat inca.")
        input("\nApasa Enter pentru a continua...")
        return

    if cale_fisier.endswith(".enc"):
        cale_iesire = cale_fisier[:-4] + ".dec"
    else:
        cale_iesire = cale_fisier + ".dec"

    print(f"\nSe decripteaza cu {fw_ales.nume}...")

    if cheie_aleasa.algoritm.tip == TipAlgoritm.SIMETRIC:
        succes, timp_ms, mem_kb = crypto.decripteaza_aes_256(
            cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
        )
    elif cheie_aleasa.algoritm.tip == TipAlgoritm.ASIMETRIC:
        succes, timp_ms, mem_kb = crypto.decripteaza_rsa(
            cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
        )
    # succes, timp_ms, mem_kb = crypto.decripteaza_aes_256(
    #     cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
    # )

    if succes:
        print(f"\nSucces! Fisier decriptat salvat in: {cale_iesire}")
        print(f"Timp executie: {timp_ms:.2f} ms")

        # Verificam integritatea daca avem hash-ul original in BD
        fisiere = db.obtine_toate_fisierele()
        fisier_original = next(
            (f for f in fisiere if f.cale_criptat == cale_fisier), None
        )
        if fisier_original and fisier_original.hash_fisier:
            hash_decriptat = _calculeaza_hash_md5(cale_iesire)
            if hash_decriptat == fisier_original.hash_fisier:
                print("Verificare integritate: OK (hash-ul corespunde fisierului original)")
            else:
                print("Atentie: Hash-ul nu corespunde! Fisierul poate fi corupt sau parola e gresita.")

        # Salvam performanta decriptarii
        if fisier_original:
            db.adauga_performanta(fisier_original.id, fw_ales.id, TipOperatie.DECRIPTARE, timp_ms, mem_kb)
            print("Datele despre performanta au fost salvate in baza de date!")
    else:
        print("\nDecriptarea a esuat. Verificati parola sau fisierul.")

    input("\nApasa Enter pentru a continua...")


def submeniu_comparare_frameworkuri(db):
    """Cripteaza acelasi fisier cu ambele framework-uri si compara performanta."""
    curata_ecran()
    print("   Comparare Framework-uri (Benchmark)")

    cale_fisier = input("\nIntroduceti calea fisierului pentru benchmark: ")
    if not os.path.exists(cale_fisier):
        print("\nEroare: Fisierul nu exista pe disc!")
        input("\nApasa Enter pentru a continua...")
        return

    cheie_aleasa = _alege_cheie(db)
    if not cheie_aleasa:
        input("\nApasa Enter pentru a continua...")
        return

    if "AES" not in cheie_aleasa.algoritm.nume:
        print(f"\nAlgoritmul {cheie_aleasa.algoritm.nume} nu este suportat pentru benchmark.")
        input("\nApasa Enter pentru a continua...")
        return

    frameworks = db.obtine_toate_frameworkurile()
    if len(frameworks) < 2:
        print("\nAtentie: Aveti nevoie de cel putin 2 framework-uri in BD pentru comparare.")
        print("Adaugati 'OpenSSL' si 'PyCryptodome' din meniul Administrare.")
        input("\nApasa Enter pentru a continua...")
        return

    rezultate = []

    for fw in frameworks:
        if "openssl" in fw.nume.lower():
            crypto = OpenSSLService()
        elif "pycryptodome" in fw.nume.lower() or "pyc" in fw.nume.lower():
            crypto = PyCryptodomeService()
        else:
            continue

        cale_iesire = f"{cale_fisier}.{fw.nume.lower().replace(' ', '_')}.enc"
        print(f"\nTestare {fw.nume}...")

        if cheie_aleasa.algoritm.tip == TipAlgoritm.SIMETRIC:
            succes, timp_ms, mem_kb = crypto.cripteaza_aes_256(
                cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
            )
        elif cheie_aleasa.algoritm.tip == TipAlgoritm.ASIMETRIC:
            succes, timp_ms, mem_kb = crypto.cripteaza_rsa(
                cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
            )
        
        # succes, timp_ms, mem_kb = crypto.cripteaza_aes_256(
        #     cale_fisier, cale_iesire, cheie_aleasa.valoare_sau_cale
        # )

        if succes:
            rezultate.append((fw, timp_ms, mem_kb, cale_iesire))
            print(f"  -> Timp criptare: {timp_ms:.2f} ms")

            fisier_db = db.adauga_fisier(cale_fisier, cale_iesire, cheie_aleasa.id, "")
            if fisier_db:
                db.adauga_performanta(fisier_db.id, fw.id, TipOperatie.CRIPTARE, timp_ms, mem_kb)
        else:
            print(f"  -> Esuat pentru {fw.nume}")

    if len(rezultate) >= 2:
        print("\n")
        print("   REZULTATE COMPARATIVE")
        print(f"{'Framework':<20} {'Timp (ms)':<15} {'Marime (KB)':<15}")
        for fw, timp, mem, _ in rezultate:
            print(f"{fw.nume:<20} {timp:<15.2f} {mem:<15.2f}")

        cel_mai_rapid = min(rezultate, key=lambda x: x[1])
        print(f"\nConcluzii: {cel_mai_rapid[0].nume} este mai rapid cu {cel_mai_rapid[1]:.2f} ms.")

    input("\nApasa Enter pentru a continua...")


def submeniu_fisiere(db):
    curata_ecran()
    print("   Operatiuni Fisiere")
    print("\n1. Cripteaza un fisier")
    print("2. Decripteaza un fisier")
    print("3. Comparare framework-uri (Benchmark)")
    print("4. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        submeniu_criptare(db)
    elif opt == "2":
        submeniu_decriptare(db)
    elif opt == "3":
        submeniu_comparare_frameworkuri(db)


def submeniu_rapoarte(db):
    curata_ecran()
    print("   Rapoarte Performanta")
    print("\n1. Toate inregistrarile de performanta")
    print("2. Fisiere criptate/decriptate")
    print("3. Inapoi")
    opt = input("\nOptiune: ")

    if opt == "1":
        performante = db.obtine_toate_performantele()
        print("\n--- Raport Performanta ---")
        if not performante:
            print("Nu exista date de performanta in baza de date.")
        else:
            print(f"\n{'ID':<5} {'Fisier':<25} {'Framework':<15} {'Operatie':<12} {'Timp(ms)':<12} {'Mem(KB)':<10}")
            print("-" * 80)
            for p in performante:
                nume_fisier = p.fisier.nume_original if p.fisier else "N/A"
                nume_fw = p.framework.nume if p.framework else "N/A"
                print(f"{p.id:<5} {nume_fisier:<25} {nume_fw:<15} {p.tip_operatie.value:<12} {p.timp_executie_ms:<12.2f} {p.memorie_kb:<10.2f}")

            # Statistici simple
            print("\n--- Statistici ---")
            timpi = [p.timp_executie_ms for p in performante]
            print(f"Timp mediu executie: {sum(timpi)/len(timpi):.2f} ms")
            print(f"Timp minim: {min(timpi):.2f} ms")
            print(f"Timp maxim: {max(timpi):.2f} ms")
            print(f"Total operatiuni: {len(performante)}")

        input("\nApasa Enter pentru a continua...")

    elif opt == "2":
        fisiere = db.obtine_toate_fisierele()
        print("\nFisiere in Baza de Date")
        if not fisiere:
            print("Nu exista fisiere inregistrate.")
        else:
            print(f"\n{'ID':<5} {'Fisier Original':<25} {'Fisier Criptat':<30} {'Hash MD5':<35}")
            print("-" * 95)
            for f in fisiere:
                hash_scurt = f.hash_fisier[:32] if f.hash_fisier else "N/A"
                print(f"{f.id:<5} {f.nume_original:<25} {f.cale_criptat:<30} {hash_scurt:<35}")
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
            submeniu_rapoarte(db)
        elif opt == "0":
            print("\nInchidere aplicatie. La revedere!")
            break
        else:
            print("\nOptiune invalida! Incearca din nou.")
            time.sleep(1)
            curata_ecran()


if __name__ == "__main__":
    main()