from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Framework, Algoritm, Cheie, TipAlgoritm

engine = create_engine('sqlite:///crypto.db', echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def ruleaza_teste_crud():

    print("\n1. Verificam si adaugam Framework-uri si Algoritmi...")
    
    fw_openssl = session.query(Framework).filter_by(nume="OpenSSL").first()
    if not fw_openssl:
        fw_openssl = Framework(nume="OpenSSL")
        session.add(fw_openssl)

    fw_pycrypto = session.query(Framework).filter_by(nume="PyCryptodome").first()
    if not fw_pycrypto:
        fw_pycrypto = Framework(nume="PyCryptodome")
        session.add(fw_pycrypto)
        
    alg_aes = session.query(Algoritm).filter_by(nume="AES-256").first()
    if not alg_aes:
        alg_aes = Algoritm(nume="AES-256", tip=TipAlgoritm.SIMETRIC)
        session.add(alg_aes)

    alg_rsa = session.query(Algoritm).filter_by(nume="RSA-2048").first()
    if not alg_rsa:
        alg_rsa = Algoritm(nume="RSA-2048", tip=TipAlgoritm.ASIMETRIC)
        session.add(alg_rsa)

    session.commit()
    print("Framework-uri si Algoritmi pregatiti!")

    cheie_test = session.query(Cheie).filter_by(valoare_sau_cale="123456789").first()
    cheie_modificata_anterior = session.query(Cheie).filter_by(valoare_sau_cale="987654321").first()
    
    if not cheie_test and not cheie_modificata_anterior:
        cheie_noua = Cheie(valoare_sau_cale="123456789", id_algoritm=alg_aes.id)
        session.add(cheie_noua)
        session.commit()

    print("\n2. Citim din baza de date...")
    algoritmi_db = session.query(Algoritm).all()
    for alg in algoritmi_db:
        print(f"Gasit algoritm: {alg.nume} (Tip: {alg.tip.value})")

    chei_db = session.query(Cheie).all()
    for c in chei_db:
        print(f"Gasit cheie: {c.valoare_sau_cale} folosita pentru {c.algoritm.nume}")

    print("\n3. Actualizam parola cheii...")
    cheie_de_modificat = session.query(Cheie).first()
    if cheie_de_modificat:
        cheie_de_modificat.valoare_sau_cale = "987654321"
        session.commit()
        print(f"Parola a fost schimbata in: {cheie_de_modificat.valoare_sau_cale}")

    print("\n4. stergem datele de test...")
    session.query(Cheie).delete()
    session.query(Algoritm).delete()
    session.query(Framework).delete()
    session.commit()
    print("Datele au fost sterse.")

if __name__ == "__main__":
    ruleaza_teste_crud()