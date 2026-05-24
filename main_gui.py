import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import hashlib

# Importuri din modulele tale deja existente
from database import CryptoDBManager
from models import TipAlgoritm, TipOperatie, Algoritm, Cheie, Framework, Fisier, Performanta
from crypto_service import OpenSSLService, PyCryptodomeService

# Configurare aspect aplicatie
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CryptoGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Setari fereastra
        self.title("Sistem Management Criptare & Performanta")
        self.geometry("1000x700")

        # Initializare servicii
        self.db = CryptoDBManager()
        self.openssl = OpenSSLService()
        self.pycrypto = PyCryptodomeService()

        # Configurare Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ================= MENIU LATERAL (SIDEBAR) =================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Crypto Manager", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, padx=20, pady=(30, 40))

        ctk.CTkButton(self.sidebar_frame, text="Administrare", command=self.show_admin).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Management Chei", command=self.show_keys).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Criptare / Decriptare", command=self.show_crypto).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Rapoarte Performanta", command=self.show_reports).grid(row=4, column=0, padx=20, pady=10)

        # ================= ZONA PRINCIPALA DE CONTINUT =================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Incarcam prima pagina by default
        self.show_admin()

    def clear_frame(self):
        """Sterge tot ce este in zona principala pentru a afisa alta pagina."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ================= 1. PAGINA ADMINISTRARE =================
    def show_admin(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Administrare Framework-uri & Algoritmi", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 30))

        # --- Adaugare Framework ---
        fw_frame = ctk.CTkFrame(self.main_frame)
        fw_frame.pack(pady=10, padx=20, fill="x")
        
        self.fw_entry = ctk.CTkEntry(fw_frame, placeholder_text="Nume Framework (ex: OpenSSL, PyCryptodome)", width=300)
        self.fw_entry.pack(side="left", padx=20, pady=15, expand=True, fill="x")
        ctk.CTkButton(fw_frame, text="Adauga Framework", command=self.add_fw).pack(side="right", padx=20, pady=15)

        # --- Adaugare Algoritm ---
        alg_frame = ctk.CTkFrame(self.main_frame)
        alg_frame.pack(pady=10, padx=20, fill="x")
        
        self.alg_entry = ctk.CTkEntry(alg_frame, placeholder_text="Nume Algoritm (ex: AES-256, RSA)", width=200)
        self.alg_entry.pack(side="left", padx=20, pady=15, expand=True, fill="x")
        
        self.alg_type = ctk.CTkComboBox(alg_frame, values=["Simetric", "Asimetric"])
        self.alg_type.pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(alg_frame, text="Adauga Algoritm", command=self.add_alg).pack(side="right", padx=20, pady=15)

    def add_fw(self):
        nume = self.fw_entry.get().strip()
        if nume:
            try:
                nou_fw = Framework(nume=nume)
                self.db.session.add(nou_fw)
                self.db.session.commit()
                messagebox.showinfo("Succes", f"Framework-ul '{nume}' a fost salvat!")
                self.fw_entry.delete(0, 'end')
            except Exception as e:
                self.db.session.rollback()
                messagebox.showerror("Eroare", f"Acest framework exista deja!")

    def add_alg(self):
        nume = self.alg_entry.get().strip()
        tip_enum = TipAlgoritm.SIMETRIC if self.alg_type.get() == "Simetric" else TipAlgoritm.ASIMETRIC
        if nume:
            try:
                nou_alg = Algoritm(nume=nume, tip=tip_enum)
                self.db.session.add(nou_alg)
                self.db.session.commit()
                messagebox.showinfo("Succes", f"Algoritmul '{nume}' a fost salvat!")
                self.alg_entry.delete(0, 'end')
            except Exception as e:
                self.db.session.rollback()
                messagebox.showerror("Eroare", f"Acest algoritm exista deja!")

    # ================= 2. PAGINA CHEI =================
    def show_keys(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Management Chei de Criptare", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 30))

        # --- Adaugare Cheie Noua ---
        add_frame = ctk.CTkFrame(self.main_frame)
        add_frame.pack(pady=10, padx=20, fill="x")

        algoritmi = self.db.session.query(Algoritm).all()
        alg_names = [a.nume for a in algoritmi] if algoritmi else ["Adaugati intai un algoritm"]

        self.key_alg_combo = ctk.CTkComboBox(add_frame, values=alg_names, width=150)
        self.key_alg_combo.pack(side="left", padx=20, pady=15)

        self.key_val_entry = ctk.CTkEntry(add_frame, placeholder_text="Parola/Cheie secreta SAU Calea catre fisier (.pem)")
        self.key_val_entry.pack(side="left", padx=10, pady=15, expand=True, fill="x")

        ctk.CTkButton(add_frame, text="Salveaza Cheia", command=self.add_key).pack(side="right", padx=20, pady=15)

        # --- Lista Chei Existente ---
        list_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Baza de Date: Chei Salvate")
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)

        chei = self.db.session.query(Cheie).all()
        for c in chei:
            nume_alg = c.algoritm.nume if c.algoritm else "N/A"
            tip_alg = c.algoritm.tip.value if c.algoritm else "N/A"
            ctk.CTkLabel(list_frame, text=f"🔑 ID: {c.id}   |   Algoritm: {nume_alg} ({tip_alg})   |   Valoare: {c.valoare_sau_cale}").pack(anchor="w", padx=10, pady=5)

    def add_key(self):
        alg_name = self.key_alg_combo.get()
        val = self.key_val_entry.get().strip()
        alg = self.db.session.query(Algoritm).filter_by(nume=alg_name).first()

        if alg and val:
            noua_cheie = Cheie(valoare_sau_cale=val, id_algoritm=alg.id)
            self.db.session.add(noua_cheie)
            self.db.session.commit()
            messagebox.showinfo("Succes", "Cheia a fost salvata in baza de date!")
            self.show_keys() # Refresh lista

    # ================= 3. PAGINA CRIPTARE/DECRIPTARE =================
    def show_crypto(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Operatiuni: Criptare si Decriptare", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 30))

        self.selected_file = None

        # --- Selectie Fisier ---
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.pack(pady=10, padx=20, fill="x")
        self.file_label = ctk.CTkLabel(file_frame, text="Niciun fisier selectat...", font=ctk.CTkFont(slant="italic"))
        self.file_label.pack(side="left", padx=20, pady=15)
        ctk.CTkButton(file_frame, text="Alege Fisier", command=self.select_file, width=120).pack(side="right", padx=20, pady=15)

        # --- Selectie Optiuni ---
        opt_frame = ctk.CTkFrame(self.main_frame)
        opt_frame.pack(pady=10, padx=20, fill="x")

        # Incarcam cheile pentru dropdown
        chei = self.db.session.query(Cheie).all()
        chei_str = [f"{c.id}: [{c.algoritm.nume if c.algoritm else ''}] - {c.valoare_sau_cale}" for c in chei] if chei else ["Nu exista chei"]
        
        ctk.CTkLabel(opt_frame, text="Cheie:").pack(side="left", padx=(20, 5), pady=15)
        self.crypto_key_combo = ctk.CTkComboBox(opt_frame, values=chei_str, width=350)
        self.crypto_key_combo.pack(side="left", padx=5, pady=15)

        self.crypto_op_var = ctk.StringVar(value="Criptare")
        ctk.CTkRadioButton(opt_frame, text="Criptare", variable=self.crypto_op_var, value="Criptare").pack(side="left", padx=20)
        ctk.CTkRadioButton(opt_frame, text="Decriptare", variable=self.crypto_op_var, value="Decriptare").pack(side="left", padx=10)

        # --- Buton Executie ---
        ctk.CTkButton(self.main_frame, text="Executa Operatiunea", font=ctk.CTkFont(weight="bold"), 
                      command=self.execute_crypto, fg_color="#2E8B57", hover_color="#226B43", height=40).pack(pady=30)

    def select_file(self):
        cale = filedialog.askopenfilename()
        if cale:
            self.selected_file = cale
            self.file_label.configure(text=cale)

    def execute_crypto(self):
        if not self.selected_file:
            messagebox.showwarning("Atentie", "Va rugam sa selectati un fisier!")
            return

        key_sel = self.crypto_key_combo.get()
        if key_sel == "Nu exista chei" or ":" not in key_sel:
            messagebox.showwarning("Atentie", "Selectati o cheie valida!")
            return

        id_cheie = int(key_sel.split(":")[0])
        cheie = self.db.session.query(Cheie).filter_by(id=id_cheie).first()
        if not cheie: return

        operatie = self.crypto_op_var.get()
        cale_in = self.selected_file
        
        # Generam extensia in functie de operatiune
        if operatie == "Criptare":
            cale_out = cale_in + ".enc"
        else:
            cale_out = cale_in.replace(".enc", "") + "_dec" if ".enc" in cale_in else cale_in + ".dec"

        is_simetric = cheie.algoritm.tip == TipAlgoritm.SIMETRIC
        hash_in = self.calculeaza_md5(cale_in) if operatie == "Criptare" else "N/A"

        # Cautam ID-ul OpenSSL pentru rapoarte (sau generam unul)
        fw = self.db.session.query(Framework).first()
        fw_id = fw.id if fw else 1

        succes, timp, mem = False, 0.0, 0.0

        try:
            if operatie == "Criptare":
                if is_simetric:
                    succes, timp, mem = self.openssl.cripteaza_aes_256(cale_in, cale_out, cheie.valoare_sau_cale)
                else:
                    succes, timp, mem = self.pycrypto.cripteaza_rsa(cale_in, cale_out, cheie.valoare_sau_cale)
                
                # Salvam fisierul nou criptat in DB
                if succes:
                    self.db.adauga_fisier(os.path.basename(cale_in), cale_out, id_cheie, hash_in)

            else: # DECRIPTARE
                if is_simetric:
                    succes, timp, mem = self.openssl.decripteaza_aes_256(cale_in, cale_out, cheie.valoare_sau_cale)
                else:
                    succes, timp, mem = self.pycrypto.decripteaza_rsa(cale_in, cale_out, cheie.valoare_sau_cale)

            if succes:
                op_enum = TipOperatie.CRIPTARE if operatie == "Criptare" else TipOperatie.DECRIPTARE
                
                # Cautam id-ul fisierului creat in DB pt rapoarte
                fisier_db = self.db.session.query(Fisier).order_by(Fisier.id.desc()).first()
                fid = fisier_db.id if fisier_db else 1
                
                self.db.adauga_performanta(fid, fw_id, op_enum, timp, mem)
                messagebox.showinfo("Succes", f"{operatie} finalizata cu succes!\nTimp de executie: {timp:.2f} ms")
            else:
                messagebox.showerror("Eroare", "Operatiunea a esuat! Verificati consola pentru erori.")

        except Exception as e:
            messagebox.showerror("Eroare Fatala", f"A aparut o problema: {str(e)}")

    def calculeaza_md5(self, cale):
        md5 = hashlib.md5()
        with open(cale, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    # ================= 4. PAGINA RAPOARTE =================
    def show_reports(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Rapoarte de Performanta (Timp & Memorie)", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 30))

        list_frame = ctk.CTkScrollableFrame(self.main_frame)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        perfs = self.db.session.query(Performanta).all()
        if not perfs:
            ctk.CTkLabel(list_frame, text="Nu exista date de performanta inregistrate.").pack(pady=20)
            return

        # Header tabel imaginar
        ctk.CTkLabel(list_frame, text="ID | Operatiune | Timp Executie | Memorie Procesata", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        for p in perfs:
            op_nume = p.tip_operatie.name if hasattr(p.tip_operatie, 'name') else p.tip_operatie
            text_raport = f"📊 ID: {p.id}  |  {op_nume}  |  ⏱️ {p.timp_executie_ms:.2f} ms  |  💾 {p.memorie_kb:.2f} KB"
            ctk.CTkLabel(list_frame, text=text_raport).pack(anchor="w", padx=10, pady=2)


if __name__ == "__main__":
    app = CryptoGUI()
    app.mainloop()