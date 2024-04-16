from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
from abc import ABC, abstractmethod
from typing import Union, Optional
import contextlib
from datetime import datetime, timedelta

class Product(BaseModel):
    id: int
    naam: str
    omschrijving: str
    productcategorie: str
    eenheidsprijs: float
    btw_percentage: float

class Bedrijf(BaseModel):
    id: int
    handelsnaam: str
    straatnaam: str
    huisnummer: str
    postcode: str
    plaats: str
    kvk_nummer: str
    btw_nummer: str
    bank: str
    iban: str
    bic: str
    telefoonnummer: str
    email: str
    logo: Optional[bytes] = None

class Klant(BaseModel):
    id: int
    handelsnaam: str
    ten_aanzien_van: str
    straatnaam: str
    huisnummer: str
    postcode: str
    plaats: str

class BevatProduct(BaseModel):
    product: Product
    hoeveelheid: int
    datum: str
    
class Factuur(BaseModel):
    factuurnummer: str
    klant: Klant
    bedrijf: Bedrijf
    factuurdatum: str
    uiterste_betaaldatum: Optional[str] = None
    producten: list[BevatProduct]
    totaalbedrag_excl: Optional[float] = None
    btw_bedrag: Optional[float] = None
    totaalbedrag_incl: Optional[float] = None
    betaalstatus: bool = False
    pdf: Optional[bytes] = None

    def __init__(self, factuurnummer: str, klant: Klant, bedrijf: Bedrijf, factuurdatum: str, producten: list[BevatProduct], betaalstatus: bool = False, uiterste_betaaldatum: Optional[str] = None, totaalbedrag_excl: Optional[float] = None, btw_bedrag: Optional[float] = None, totaalbedrag_incl: Optional[float] = None, pdf: Optional[bytes] = None):
        super().__init__(
            factuurnummer=factuurnummer,
            klant=klant,
            bedrijf=bedrijf,
            factuurdatum=factuurdatum,
            producten=producten,
            betaalstatus=betaalstatus,
            uiterste_betaaldatum=uiterste_betaaldatum,  # Add this line
            totaalbedrag_excl=totaalbedrag_excl,  # Add this line
            btw_bedrag=btw_bedrag,  # Add this line
            totaalbedrag_incl=totaalbedrag_incl,  # Add this line
            pdf=pdf
        )

        # If uiterste_betaaldatum is not provided, calculate it
        if self.uiterste_betaaldatum is None:
            uiterste_betaaldatum_obj = datetime.strptime(factuurdatum, "%Y-%m-%d") + timedelta(days=30)
            self.uiterste_betaaldatum = uiterste_betaaldatum_obj.strftime("%Y-%m-%d")

        # If totaalbedrag_excl is not provided, calculate it
        if self.totaalbedrag_excl is None:
            totaalbedrag_excl = sum(bevatproduct.product.eenheidsprijs * bevatproduct.hoeveelheid for bevatproduct in producten)
            self.totaalbedrag_excl = totaalbedrag_excl

        # If btw_bedrag is not provided, calculate it
        if self.btw_bedrag is None:
            btw_bedrag = sum(bevatproduct.product.eenheidsprijs * bevatproduct.hoeveelheid * bevatproduct.product.btw_percentage / 100 for bevatproduct in producten)
            self.btw_bedrag = round(btw_bedrag, 2)

        # If totaalbedrag_incl is not provided, calculate it
        if self.totaalbedrag_incl is None:
            self.totaalbedrag_incl = self.totaalbedrag_excl + self.btw_bedrag

class Repository[T](ABC):
    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get(self, item: int) -> T:
        raise NotImplementedError
    
    @abstractmethod
    def get_all(self, item: T) -> list[T]:
        raise NotImplementedError
    
    @abstractmethod
    def add(self, item: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, item: T) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, item: T) -> None:
        raise NotImplementedError

class SingleEntityRepository(Repository[Union[Product, Klant, Bedrijf]]):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
    
    def create(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Product (
                        id INTEGER NOT NULL,
                        naam VARCHAR(255) NOT NULL,
                        omschrijving VARCHAR(255) NOT NULL,
                        productcategorie VARCHAR(255) NOT NULL,
                        eenheidsprijs DECIMAL(10,2) NOT NULL,
                        btw_percentage DECIMAL(10,2) NOT NULL,
                        PRIMARY KEY (id)
                        );
                        """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Klant (
                        id INTEGER NOT NULL,
                        handelsnaam VARCHAR(255) NOT NULL, 
                        ten_aanzien_van VARCHAR(255) NOT NULL,
                        straatnaam VARCHAR(255) NOT NULL,
                        huisnummer VARCHAR(255) NOT NULL,
                        postcode VARCHAR(255) NOT NULL,
                        plaats VARCHAR(255) NOT NULL,
                        PRIMARY KEY (id)
                        );
                        """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Bedrijf (
                        id INTEGER NOT NULL,
                        handelsnaam VARCHAR(255) NOT NULL, 
                        straatnaam VARCHAR(255) NOT NULL,
                        huisnummer VARCHAR(255) NOT NULL,
                        postcode VARCHAR(255) NOT NULL,
                        plaats VARCHAR(255) NOT NULL,
                        kvk_nummer VARCHAR(255) NOT NULL,
                        btw_nummer VARCHAR(255) NOT NULL,
                        bank VARCHAR(255) NOT NULL,
                        iban VARCHAR(255) NOT NULL,
                        bic VARCHAR(255) NOT NULL,
                        telefoonnummer VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        logo BLOB,
                        PRIMARY KEY (id)
                        );
                        """)

    def get(self, id: int, table_name: str) -> Product | Klant | Bedrijf:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = {id};")
        query_result = cursor.fetchone()
        if query_result is None:
            raise ValueError(f"{table_name} with id {id} does not exist.")
        mappings = {
            "Product": Product,
            "Klant": Klant,
            "Bedrijf": Bedrijf
        }
        query_dict = dict(zip(list(mappings[table_name].model_fields.keys()), query_result))
        return mappings[table_name](**query_dict)

    def get_all(self, table_name: str) -> list[Product | Klant | Bedrijf]:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        query_result = cursor.fetchall()
        if query_result is None:
            raise ValueError(f"No entries in {table_name} exist.")
        mappings = {
            "Product": Product,
            "Klant": Klant,
            "Bedrijf": Bedrijf
        }
        items = []
        for item in query_result:
            item_dict = dict(zip(list(mappings[table_name].model_fields.keys()), item))
            items.append(mappings[table_name](**item_dict))               
        return items
    
    def add(self, item: Product | Klant | Bedrijf) -> None:
        table_name = item.__class__.__name__
        columns = list(item.model_dump().keys())
        placeholders = ", ".join(["?"] * len(columns))
        cursor = self.conn.cursor()
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        values = [getattr(item, column) for column in columns]
        cursor.execute(query, values)
        self.conn.commit()

    def update(self, item: Product | Klant | Bedrijf) -> None:
        table_name = item.__class__.__name__
        columns = list(item.model_dump().keys())
        placeholders = ", ".join([f"{column} = ?" for column in columns])
        cursor = self.conn.cursor()
        query = f"UPDATE {table_name} SET {placeholders} WHERE id = {item.id};"
        values = [getattr(item, column) for column in columns]
        cursor.execute(query, values)
        self.conn.commit()
    
    def delete(self, item: Product | Klant | Bedrijf) -> None:
        table_name = item.__class__.__name__
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = {item.id};")

class FactuurRepository(Repository[Factuur]):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

    def create(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Factuur (
                        factuurnummer VARCHAR(255) NOT NULL,
                        klant VARCHAR(255) NOT NULL,
                        bedrijf VARCHAR(255) NOT NULL,
                        factuurdatum DATE NOT NULL,
                        uiterste_betaaldatum DATE NOT NULL,
                        totaalbedrag_excl DECIMAL(10,2) NOT NULL,
                        btw_bedrag DECIMAL(10,2) NOT NULL,
                        totaalbedrag_incl DECIMAL(10,2) NOT NULL,
                        betaalstatus BOOLEAN NOT NULL DEFAULT FALSE,
                        pdf BLOB,
                        PRIMARY KEY (factuurnummer),
                        FOREIGN KEY (klant) REFERENCES Klant(id),
                        FOREIGN KEY (bedrijf) REFERENCES Bedrijf(id)
                        );
                        """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS BevatProduct (
                        factuur VARCHAR(255) NOT NULL,
                        product VARCHAR(255) NOT NULL,
                        hoeveelheid INT NOT NULL,
                        datum DATE NOT NULL,
                        PRIMARY KEY (factuur, product, datum),
                        FOREIGN KEY (factuur) REFERENCES Factuur(factuurnummer),
                        FOREIGN KEY (product) REFERENCES Product(id)
                        );
                    """)
    
    def get(self, factuurnummer: str) -> Factuur:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM Factuur WHERE Factuur.factuurnummer = ?;""", (factuurnummer,))
        facturen = cursor.fetchone()
        if facturen is None:
            raise ValueError(f"Factuur with factuurnummer {factuurnummer} does not exist.")
        factuur_dict = dict(zip(["factuurnummer", "klant", "bedrijf", "factuurdatum", "uiterste_betaaldatum", "totaalbedrag_excl", "btw_bedrag", "totaalbedrag_incl", "betaalstatus", "pdf"], facturen))
        cursor.execute("""SELECT * FROM BevatProduct WHERE BevatProduct.factuur = ?;""", (factuurnummer,))
        bevatproducten = cursor.fetchall()
        repo = SingleEntityRepository(self.db_path)
        repo.conn = self.conn
        factuur = Factuur(
            factuurnummer=factuur_dict["factuurnummer"],
            klant=repo.get(factuur_dict["klant"], "Klant"),
            bedrijf=repo.get(factuur_dict["bedrijf"], "Bedrijf"),
            factuurdatum=factuur_dict["factuurdatum"],
            uiterste_betaaldatum=factuur_dict["uiterste_betaaldatum"],
            totaalbedrag_excl=factuur_dict["totaalbedrag_excl"],
            btw_bedrag=factuur_dict["btw_bedrag"],
            totaalbedrag_incl=factuur_dict["totaalbedrag_incl"],
            betaalstatus=factuur_dict["betaalstatus"],
            pdf=factuur_dict["pdf"],
            producten=[BevatProduct(
                factuur=bevatproduct[0],
                product=repo.get(bevatproduct[1], "Product"),
                hoeveelheid=bevatproduct[2],
                datum=bevatproduct[3]
            ) for bevatproduct in bevatproducten]
        )
        return factuur
 
    def get_all(self) -> list[Factuur]:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT Factuur.factuurnummer FROM Factuur;""")
        factuurnummers = cursor.fetchall()
        return [
            self.get(factuurnummer[0])
            for factuurnummer in factuurnummers
        ]
    
    def add(self, item: Factuur) -> None:
        cursor = self.conn.cursor()
        repo = SingleEntityRepository(self.db_path)
        repo.conn = self.conn
        # Check if all entities exist
        if not item.klant == repo.get(item.klant.id, 'Klant'):
            raise ValueError(f"Klant with id {item.klant.id} does not exist.")
        if not item.bedrijf == repo.get(item.bedrijf.id, 'Bedrijf'):
            raise ValueError(f"Bedrijf with id {item.bedrijf.id} does not exist.")
        for product in item.producten:
            if not product.product == repo.get(product.product.id, 'Product'):
                raise ValueError(f"Product with id {product.id} does not exist.")
        # Insert new factuur in database
        cursor.execute("""
                        INSERT INTO Factuur
                        (factuurnummer, klant, bedrijf, factuurdatum, uiterste_betaaldatum, totaalbedrag_excl, btw_bedrag, totaalbedrag_incl, betaalstatus, pdf)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            item.factuurnummer,
                            item.klant.id,
                            item.bedrijf.id,
                            item.factuurdatum,
                            item.uiterste_betaaldatum,
                            item.totaalbedrag_excl,
                            item.btw_bedrag,
                            item.totaalbedrag_incl,
                            item.betaalstatus,
                            item.pdf
                        ))
        # Insert Bevat products using a for loop
        for product in item.producten:
            cursor.execute("""
                            INSERT INTO BevatProduct
                            (factuur, product, hoeveelheid, datum)
                            VALUES
                            (?, ?, ?, ?);
                            """, (
                                item.factuurnummer,
                                product.product.id,
                                product.hoeveelheid,
                                product.datum
                            ))
        self.conn.commit()
        
    def update(self, item: Factuur) -> None:
        cursor = self.conn.cursor()
        repo = SingleEntityRepository(self.db_path)
        repo.conn = self.conn
        # Check if all entities exist
        if not item.klant == repo.get(item.klant.id, 'Klant'):
            raise ValueError(f"Klant with id {item.klant.id} does not exist.")
        if not item.bedrijf == repo.get(item.bedrijf.id, 'Bedrijf'):
            raise ValueError(f"Bedrijf with id {item.bedrijf.id} does not exist.")
        for product in item.producten:
            if not product.product == repo.get(product.product.id, 'Product'):
                raise ValueError(f"Product with id {product.id} does not exist.")
        # Update factuur in database
        cursor.execute("""
                        UPDATE Factuur SET
                        factuurnummer = ?,
                        klant = ?,
                        bedrijf = ?,
                        factuurdatum = ?,
                        uiterste_betaaldatum = ?,
                        totaalbedrag_excl = ?,
                        btw_bedrag = ?,
                        totaalbedrag_incl = ?,
                        betaalstatus = ?,
                        pdf = ?
                        WHERE factuurnummer = ?;
                       """, (
                            item.factuurnummer,
                            item.klant.id,
                            item.bedrijf.id,
                            item.factuurdatum,
                            item.uiterste_betaaldatum,
                            item.totaalbedrag_excl,
                            item.btw_bedrag,
                            item.totaalbedrag_incl,
                            item.betaalstatus,
                            item.pdf,
                            item.factuurnummer
                        ))
        # Delete all BevatProducts with corresponding to that factuurnummer
        cursor.execute("""DELETE FROM BevatProduct WHERE BevatProduct.factuur = ?;""", (item.factuurnummer,))
        # Insert Bevat products using a for loop
        for product in item.producten:
            cursor.execute("""
                            INSERT INTO BevatProduct
                            (factuur, product, hoeveelheid, datum)
                            VALUES
                            (?, ?, ?, ?);
                            """, (
                                item.factuurnummer,
                                product.product.id,
                                product.hoeveelheid,
                                product.datum
                            ))
        self.conn.commit()
    
    def delete(self, item: Factuur) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM BevatProduct WHERE BevatProduct.factuur = ?;""", (item.factuurnummer,))
        cursor.execute("""DELETE FROM Factuur WHERE Factuur.factuurnummer = ?;""", (item.factuurnummer,))
        self.conn.commit()