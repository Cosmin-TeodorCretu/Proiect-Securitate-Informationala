from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Framework, Algoritm, Cheie, TipAlgoritm

engine = create_engine('sqlite:///crypto.db', echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def ruleaza_teste_crud():

    print("\n1. Adaugam Framework-uri si Algoritmi...")
    fw_openssl = Framework(nume="OpenSSL")
    fw_pycrypto = Framework(nume="PyCryptodome")
    
    alg_aes = Algoritm(nume="AES-256", tip=TipAlgoritm.SIMETRIC)
    alg_rsa = Algoritm(nume="RSA-2048", tip=TipAlgoritm.ASIMETRIC)

    session.add_all([fw_openssl, fw_pycrypto, alg_aes, alg_rsa])
    session.commit()
    print("Date inserate cu succes!")

    # Adăugăm o cheie de test legată de AES
    cheie_test = Cheie(valoare_sau_cale="parola_secreta_123", id_algoritm=alg_aes.id)
    session.add(cheie_test)
    session.commit()

    # --- READ (Citire date) ---
    print("\n2. Citim din baza de date...")
    algoritmi_db = session.query(Algoritm).all()
    for alg in algoritmi_db:
        print(f"Găsit algoritm: {alg.nume} (Tip: {alg.tip.value})")

    chei_db = session.query(Cheie).all()
    for c in chei_db:
        print(f"Găsit cheie: {c.valoare_sau_cale} folosită pentru {c.algoritm.nume}")

    # --- UPDATE (Actualizare date) ---
    print("\n3. Actualizam parola cheii...")
    cheie_de_modificat = session.query(Cheie).first()
    cheie_de_modificat.valoare_sau_cale = "parola_NOUA_456"
    session.commit()
    print(f"Parola a fost schimbată în: {cheie_de_modificat.valoare_sau_cale}")

    # --- DELETE (Ștergere date - curățăm pentru următoarea rulare) ---
    print("\n4. Ștergem datele de test (pentru a rula scriptul iar data viitoare)...")
    session.query(Cheie).delete()
    session.query(Algoritm).delete()
    session.query(Framework).delete()
    session.commit()
    print("Datele au fost șterse. Test CRUD finalizat cu succes!")

if __name__ == "__main__":
    ruleaza_teste_crud()