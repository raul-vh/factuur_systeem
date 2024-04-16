import pytest
from backend.operations.database_operations import Product, Klant, Bedrijf, Factuur, BevatProduct
from backend.operations.database_operations import SingleEntityRepository, FactuurRepository
from backend.operations.factuur_automations import generate_pdf
import os

repo = SingleEntityRepository(':memory:')
repo.create()

def convert_pic(filename):
    with open(filename, "rb") as f:
        photo = f.read()
    return photo

Google = Bedrijf(
    id=1,
    handelsnaam="Google",
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
    email="info@google.com",
    logo=convert_pic("google_logo.png")
)

John_Doe = Klant(
    id=1,
    handelsnaam="John Doe Inc.",
    ten_aanzien_van="John Doe",
    straatnaam="Pannekoeken Street",
    huisnummer="1",
    postcode="1234AB",
    plaats="New York"
)

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

f2024002 = Factuur(
    factuurnummer="F2024002",
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
        ),
        BevatProduct(
            product=Banaan,
            hoeveelheid=5,
            datum="2021-04-02"
        ),
        BevatProduct(
            product=Banaan,
            hoeveelheid=5,
            datum="2021-04-03"
        ),
        BevatProduct(
            product=Banaan,
            hoeveelheid=5,
            datum="2021-04-04"
        )
    ],
    betaalstatus=False
)

def test_generate_pdf() -> None:
    """Test if Factuur object with generated pdf is not equal to Factuur object without."""
    with pytest.raises(AssertionError):
        assert f2024002 == generate_pdf(f2024002).pdf

def test_generate_pdf_repo_functionality() -> None:
    """Test if Factuur object with generated pdf can be added and retrieved from repo,
    and that the retrieved object is equal to the Factuur object with generated pdf."""
    repo.add(Google)
    repo.add(Banaan)
    repo.add(Appel)
    repo.add(John_Doe)
    factuur_repo = FactuurRepository(':memory:')
    factuur_repo.conn = repo.conn
    factuur_repo.create()
    factuur_repo.add(f2024002)
    f2024002_with_pdf = generate_pdf(f2024002)
    factuur_repo.update(f2024002_with_pdf)
    retrieved_object_after_update = factuur_repo.get(f2024002_with_pdf.factuurnummer)
    assert retrieved_object_after_update == f2024002_with_pdf

def test_generate_pdf_writing_pdf() -> None:
    """Test if Factuur object with generated pdf can be written to pdf file."""
    f2024002_with_pdf = generate_pdf(f2024002)
    print(f2024002_with_pdf)
    with open("factuur.pdf", "wb") as f:
        f.write(f2024002_with_pdf.pdf)
    assert os.path.exists("factuur.pdf") == True
    os.remove("factuur.pdf")