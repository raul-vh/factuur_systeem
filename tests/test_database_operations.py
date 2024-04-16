import pytest
from backend.operations.database_operations import Product, Klant, Bedrijf, Factuur, BevatProduct
from backend.operations.database_operations import SingleEntityRepository, FactuurRepository

repo = SingleEntityRepository(':memory:')
repo.create()

def convert_pic(filename):
    with open(filename, "rb") as f:
        photo = f.read()
    return photo

# The tests for producten
Appel = Product(
    id=1,
    naam="Appel",
    omschrijving="Een apppel.",
    productcategorie="fruit",
    eenheidsprijs=0.50,
    btw_percentage=21.0
)

Banaan = Product(
    id=2,
    naam="Banaan",
    omschrijving="Een banaan.",
    productcategorie="fruit",
    eenheidsprijs=0.75,
    btw_percentage=21.0
)

def test_product_add_and_get() -> None:
    repo.add(Appel)
    assert repo.get(Appel.id, 'Product') == Appel

def test_product_add_and_get_all() -> None:
    repo.add(Banaan)
    assert repo.get_all('Product') == [Appel, Banaan]

Banaan = Product(
    id=2,
    naam="Banaan",
    omschrijving="Een banaan.",
    productcategorie="fruit",
    eenheidsprijs=0.75,
    btw_percentage=21.0
)

def test_product_update_and_get() -> None:
    repo.update(Banaan)
    assert repo.get(Banaan.id, 'Product') == Banaan

def test_product_delete() -> None:
    repo.delete(Banaan)
    with pytest.raises(ValueError):
        repo.get(Banaan.id, 'Product')

# The tests for klanten
John_Doe = Klant(
        id=1,
        handelsnaam="John Doe Inc.",
        ten_aanzien_van="John Doe",
        straatnaam="Pannekoeken Street",
        huisnummer="1",
        postcode="1234AB",
        plaats="New York")

Hans_Klaas = Klant(
        id=2,
        handelsnaam="Hans Klaas Inc.",
        ten_aanzien_van="Hans Klaas",
        straatnaam="Oliebollen Street",
        huisnummer="3",
        postcode="1234AC",
        plaats="Chicago")

def test_klant_add_and_get() -> None:
    repo.add(John_Doe)
    assert repo.get(John_Doe.id, 'Klant') == John_Doe

def test_klant_add_and_get_all() -> None:
    repo.add(Hans_Klaas)
    assert repo.get_all('Klant') == [John_Doe, Hans_Klaas]

Hans_Klaas = Klant(
        id=2,
        handelsnaam="Hans Klaas Inc.",
        ten_aanzien_van="Hans Klaas",
        straatnaam="Wentelteefjes Street",
        huisnummer="343",
        postcode="5678GH",
        plaats="Chicago")

def test_klant_update_and_get() -> None:
    repo.update(Hans_Klaas)
    assert repo.get(Hans_Klaas.id, 'Klant') == Hans_Klaas

def test_klant_delete() -> None:
    repo.delete(Hans_Klaas)
    with pytest.raises(ValueError):
        repo.get(Hans_Klaas.id, 'Klant')

# The tests for bedrijven
Google = Bedrijf(
    id=1,
    handelsnaam="Groenteboer BV",
    straatnaam="Main Street",
    huisnummer="2",
    postcode="1234AB",
    plaats="New York",
    kvk_nummer="12345678",
    btw_nummer="12345678",
    bank="ING",
    iban="NL12INGB1234567890",
    bic="INGBNL2A",
    telefoonnummer="123456789",
    email="info@groenteboer.com",
    logo=convert_pic("google_logo.png")
)

Fruitwinkel = Bedrijf(
    id=2,
    handelsnaam="Fruitwinkel BV",
    straatnaam="Main Street",
    huisnummer="3",
    postcode="1234AB",
    plaats="New York",
    kvk_nummer="23456789",
    btw_nummer="23456789",
    bank="ING",
    iban="NL12INGB1234567890",
    bic="INGBNL2A",
    telefoonnummer="123456789",
    email="info@fruitwinkel.com"
)
def test_bedrijf_add_and_get() -> None:
    repo.add(Google)
    assert repo.get(Google.id, 'Bedrijf') == Google

def test_bedrijf_add_and_get_all() -> None:
    repo.add(Fruitwinkel)
    assert repo.get_all('Bedrijf') == [Google, Fruitwinkel]

Fruitwinkel = Bedrijf(
    id=2,
    handelsnaam="Fruitwinkel BV",
    straatnaam="Main Street",
    huisnummer="3",
    postcode="1234AB",
    plaats="New York",
    kvk_nummer="65820472",
    btw_nummer="23456789",
    bank="RABO",
    iban="NL43RABO1234567890",
    bic="RABONL2A",
    telefoonnummer="123456789",
    email="info@fruitwinkel.com"
)

def test_bedrijf_update_and_get() -> None:
    repo.update(Fruitwinkel)
    assert repo.get(Fruitwinkel.id, 'Bedrijf') == Fruitwinkel

def test_bedrijf_delete() -> None:
    repo.delete(Fruitwinkel)
    with pytest.raises(ValueError):
        repo.get(Fruitwinkel.id, 'Bedrijf')

# The tests for facturen
f2024001 = Factuur(
    factuurnummer="f2024001",
    klant=John_Doe,
    bedrijf=Google,
    factuurdatum="2021-01-01",
    producten=[
        BevatProduct(
            product=Appel,
            hoeveelheid=3,
            datum="2021-01-01"
        ),
        BevatProduct(
            product=Banaan,
            hoeveelheid=2,
            datum="2021-01-02"
        )
    ],
    betaalstatus=False)

factuur_repo = FactuurRepository(':memory:')
factuur_repo.conn = repo.conn
factuur_repo.create()

def test_factuur_add_and_get() -> None:
    repo.add(Banaan)
    factuur_repo.add(f2024001)
    print(f2024001)
    print("\n")
    print(factuur_repo.get(f2024001.factuurnummer))
    assert factuur_repo.get(f2024001.factuurnummer) == f2024001

f2024002 = Factuur(
    factuurnummer="f2024002",
    klant=John_Doe,
    bedrijf=Google,
    factuurdatum="2022-04-01",
    producten=[
        BevatProduct(
            product=Appel,
            hoeveelheid=1,
            datum="2022-04-01"
        ),
        BevatProduct(
            product=Banaan,
            hoeveelheid=2,
            datum="2021-04-01"
        )
    ],
    betaalstatus=False)

def test_factuur_add_and_get_all() -> None:
    factuur_repo.add(f2024002)
    print(factuur_repo.get_all())
    print("\n")
    print([f2024001, f2024002])
    assert factuur_repo.get_all() == [f2024001, f2024002]

Mango = Product(
    id=3,
    naam="Mango",
    omschrijving="Een mango.",
    productcategorie="fruit",
    eenheidsprijs=1.99,
    btw_percentage=21.0
)

f2024001_update = Factuur(
    factuurnummer="f2024001",
    klant=John_Doe,
    bedrijf=Google,
    factuurdatum="2021-01-01",
    producten=[
        BevatProduct(
            product=Appel,
            hoeveelheid=3,
            datum="2021-01-01"
        ),
        BevatProduct(
            product=Mango,
            hoeveelheid=2,
            datum="2021-01-02"
        )
    ],
    betaalstatus=False)

def test_factuur_update_and_get() -> None:
    repo.add(Mango)
    factuur_repo.update(f2024001_update)
    assert factuur_repo.get(f2024001_update.factuurnummer) == f2024001_update

def test_factuur_delete() -> None:
    factuur_repo.delete(f2024002)
    with pytest.raises(ValueError):
        factuur_repo.get(f2024002.factuurnummer)