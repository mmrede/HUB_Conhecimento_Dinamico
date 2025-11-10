from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Parceria(Base):
    __tablename__ = "instrumentos_parceria"

    id = Column(Integer, primary_key=True, index=True)
    numero_do_termo = Column(String)
    ano_do_termo = Column(Integer)
    cpf_cnpj = Column(String)
    razao_social = Column(String)
    objeto = Column(String)
    data_da_assinatura = Column(Date)
    data_de_publicacao = Column(Date)
    vigencia = Column(Date)
    situacao = Column(String)

    class Config:
        orm_mode = True