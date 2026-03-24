from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class TipAlgoritm(enum.Enum):
    SIMETRIC = "Simetric"
    ASIMETRIC = "Asimetric"

class TipOperatie(enum.Enum):
    CRIPTARE = "Criptare"
    DECRIPTARE = "Decriptare"

class Framework(Base):
    __tablename__ = 'frameworks'
    id = Column(Integer, primary_key=True)
    nume = Column(String, unique=True, nullable=False) 

class Algoritm(Base):
    __tablename__ = 'algoritmi'
    id = Column(Integer, primary_key=True)
    nume = Column(String, unique=True, nullable=False) 
    tip = Column(Enum(TipAlgoritm), nullable=False)

class Cheie(Base):
    __tablename__ = 'chei'
    id = Column(Integer, primary_key=True)
    valoare_sau_cale = Column(String, nullable=False)
    id_algoritm = Column(Integer, ForeignKey('algoritmi.id'))
    
    algoritm = relationship("Algoritm")

class Fisier(Base):
    __tablename__ = 'fisiere'
    id = Column(Integer, primary_key=True)
    nume_original = Column(String, nullable=False)
    cale_criptat = Column(String, nullable=False)
    id_cheie = Column(Integer, ForeignKey('chei.id'))
    
    cheie = relationship("Cheie")

class Performanta(Base):
    __tablename__ = 'performante'
    id = Column(Integer, primary_key=True)
    id_fisier = Column(Integer, ForeignKey('fisiere.id'))
    id_framework = Column(Integer, ForeignKey('frameworks.id'))
    tip_operatie = Column(Enum(TipOperatie), nullable=False)
    timp_executie_ms = Column(Float, nullable=False)
    memorie_kb = Column(Float, nullable=False)
    
    fisier = relationship("Fisier")
    framework = relationship("Framework")