from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base, Framework, Algoritm, Cheie, TipAlgoritm

class CryptoDBManager:
    def __init__(self, db_url='sqlite:///crypto.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def adauga_framework(self, nume: str):
        if not nume or not nume.strip():
            print("Eroare: Numele framework-ului nu poate fi gol.")
            return None
            
        try:
            existent = self.session.query(Framework).filter_by(nume=nume).first()
            if existent:
                print(f"Info: Framework-ul '{nume}' exista deja.")
                return existent
                
            nou_fw = Framework(nume=nume)
            self.session.add(nou_fw)
            self.session.commit()
            print(f"Succes: Framework '{nume}' adaugat.")
            return nou_fw
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare DB la adaugarea framework-ului: {e}")
            return None

    def adauga_algoritm(self, nume: str, tip: TipAlgoritm):
        if not nume.strip():
            print("Eroare: Numele algoritmului nu poate fi gol.")
            return None
            
        try:
            existent = self.session.query(Algoritm).filter_by(nume=nume).first()
            if existent:
                print(f"Info: Algoritmul '{nume}' exista deja.")
                return existent
                
            nou_alg = Algoritm(nume=nume, tip=tip)
            self.session.add(nou_alg)
            self.session.commit()
            print(f"Succes: Algoritm '{nume}' ({tip.value}) adaugat.")
            return nou_alg
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare DB la adaugarea algoritmului: {e}")
            return None

    def adauga_cheie(self, valoare_sau_cale: str, id_algoritm: int):
        if not valoare_sau_cale.strip():
            print("Eroare: Valoarea cheii nu poate fi goala.")
            return None
            
        try:
            algoritm = self.session.query(Algoritm).filter_by(id=id_algoritm).first()
            if not algoritm:
                print(f"Eroare: Algoritmul cu ID-ul {id_algoritm} nu a fost gasit.")
                return None

            noua_cheie = Cheie(valoare_sau_cale=valoare_sau_cale, id_algoritm=id_algoritm)
            self.session.add(noua_cheie)
            self.session.commit()
            print("Succes: Cheie adaugata cu succes.")
            return noua_cheie
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare DB la adaugarea cheii: {e}")
            return None

    def obtine_toate_cheile(self):
        try:
            return self.session.query(Cheie).all()
        except SQLAlchemyError as e:
            print(f"Eroare la citirea cheilor: {e}")
            return []

    def actualizeaza_cheie(self, cheie_id: int, noua_valoare: str):
        if not noua_valoare.strip():
            print("Eroare: Noua valoare nu poate fi goala.")
            return False
            
        try:
            cheie = self.session.query(Cheie).filter_by(id=cheie_id).first()
            if not cheie:
                print(f"Eroare: Cheia cu ID-ul {cheie_id} nu exista.")
                return False
                
            cheie.valoare_sau_cale = noua_valoare
            self.session.commit()
            print(f"Succes: Cheia {cheie_id} a fost actualizata.")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare la actualizarea cheii: {e}")
            return False
        
    def sterge_cheie(self, cheie_id: int):
        try:
            cheie = self.session.query(Cheie).filter_by(id=cheie_id).first()
            if not cheie:
                print(f"\nEroare: Cheia cu ID-ul {cheie_id} nu exista.")
                return False
                
            self.session.delete(cheie)
            self.session.commit()
            print(f"\nSucces: Cheia cu ID-ul {cheie_id} a fost stearsa definitiv din baza de date.")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"\nEroare DB la stergerea cheii: {e}")
            return False
    
    def adauga_fisier(self, nume_original: str, cale_criptat: str, id_cheie: int, hash_fisier: str = ""):
        from models import Fisier # import local pentru siguranta
        try:
            nou_fisier = Fisier(nume_original=nume_original, cale_criptat=cale_criptat, id_cheie=id_cheie, hash_fisier=hash_fisier)
            self.session.add(nou_fisier)
            self.session.commit()
            return nou_fisier
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare DB la adaugarea fisierului: {e}")
            return None

    def adauga_performanta(self, id_fisier: int, id_framework: int, tip_operatie, timp_ms: float, memorie_kb: float):
        from models import Performanta
        try:
            noua_perf = Performanta(
                id_fisier=id_fisier, 
                id_framework=id_framework, 
                tip_operatie=tip_operatie, 
                timp_executie_ms=timp_ms, 
                memorie_kb=memorie_kb
            )
            self.session.add(noua_perf)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Eroare DB la salvarea performantei: {e}")
            return False

if __name__ == "__main__":
    db = CryptoDBManager()

    print("\n1. Testare Creare (cu validari)")
    db.adauga_framework("OpenSSL")
    db.adauga_framework("PyCryptodome")
    
    alg_aes = db.adauga_algoritm("AES-256", TipAlgoritm.SIMETRIC)
    alg_rsa = db.adauga_algoritm("RSA-2048", TipAlgoritm.ASIMETRIC)
    
    db.adauga_algoritm("", TipAlgoritm.SIMETRIC) 
    
    if alg_aes:
        db.adauga_cheie("super_secret_key_123", alg_aes.id)

    print("\n2. Testare Citire")
    chei = db.obtine_toate_cheile()
    for c in chei:
        print(f"Cheie ID {c.id}: {c.valoare_sau_cale} (Algoritm ID: {c.id_algoritm})")

    print("\n3. Testare Actualizare")
    if chei:
        db.actualizeaza_cheie(chei[0].id, "parola_noua_modificata")
        
    db.actualizeaza_cheie(999, "nu_va_merge")