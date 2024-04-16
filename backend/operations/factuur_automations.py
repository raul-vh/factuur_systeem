from fpdf import FPDF
from .database_operations import Product, Klant, Bedrijf, Factuur, BevatProduct
import os

def convert_pic(filename):
    with open(filename, "rb") as f:
        photo = f.read()
    return photo

def generate_pdf(factuur: Factuur) -> Factuur:
    '''
    Generates a pdf for the factuur
    Then reads the pdf as binary data and stores it in the factuur object
    Returns the factuur object'''
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header
    #convert binary image to png
    with open("temporary.png", "wb") as f:
        f.write(factuur.bedrijf.logo)
    pdf.image("temporary.png", x=10, y=10, h=30)
    os.remove("temporary.png")
    #print image
    pdf.ln(30)

    pdf.cell(100, 10, txt=f"{factuur.klant.handelsnaam}", ln=False)
    pdf.cell(0, 10, txt=f"{factuur.bedrijf.handelsnaam}", ln=True, align="R")
    pdf.cell(100, 10, txt=f"{factuur.klant.ten_aanzien_van}", ln=False)
    pdf.cell(0, 10, txt=f"{factuur.bedrijf.straatnaam}, {factuur.bedrijf.huisnummer}", ln=True, align="R")
    pdf.cell(100, 10, txt=f"{factuur.klant.straatnaam}, {factuur.klant.huisnummer}", ln=False)
    pdf.cell(0, 10, txt=f"{factuur.bedrijf.postcode}, {factuur.bedrijf.plaats}", ln=True, align="R")
    pdf.cell(100, 10, txt=f"{factuur.klant.postcode}, {factuur.klant.plaats}", ln=False)
    pdf.cell(0, 10, txt=f"KVK-nummer: {factuur.bedrijf.kvk_nummer}", ln=True, align="R")
    pdf.cell(0, 10, txt=f"BTW-nummer: {factuur.bedrijf.btw_nummer}", ln=True, align="R")
    pdf.cell(100, 10, txt=f"Factuurnummer: {factuur.factuurnummer}", ln=False)
    pdf.cell(0, 10, txt=f"Email: {factuur.bedrijf.email}", ln=True, align="R")
    pdf.cell(100, 10, txt=f"Factuurdatum: {factuur.factuurdatum}", ln=False)
    pdf.cell(0, 10, txt=f"Telefoonnummer: {factuur.bedrijf.telefoonnummer}", ln=True, align="R")
    pdf.ln(10)

    #Producten
    pdf.cell(25, 10, txt="Datum", border=1, ln=False, align="C")
    pdf.cell(40, 10, txt="Product", border=1, ln=False, align="L")
    pdf.cell(60, 10, txt="Omschrijving", border=1, ln=False, align="L")
    pdf.cell(15, 10, txt="Aantal", border=1, ln=False, align="C")
    pdf.cell(20, 10, txt="Prijs", border=1, ln=False, align="C")
    pdf.cell(30, 10, txt="Totaal", border=1, ln=True, align="C")

    # Producten
    pdf.cell(25, 10, txt="Datum", border=1, ln=False, align="C")
    pdf.cell(40, 10, txt="Product", border=1, ln=False, align="L")
    pdf.cell(60, 10, txt="Omschrijving", border=1, ln=False, align="L")
    pdf.cell(15, 10, txt="Aantal", border=1, ln=False, align="C")
    pdf.cell(20, 10, txt="Prijs", border=1, ln=False, align="C")
    pdf.cell(30, 10, txt="Totaal", border=1, ln=True, align="C")

    for bevat_product in factuur.producten:
        pdf.cell(25, 10, txt=str(bevat_product.datum), border=1, ln=False, align="C")
        pdf.cell(40, 10, txt=bevat_product.product.naam, border=1, ln=False, align="L")
        pdf.cell(60, 10, txt=str(bevat_product.product.omschrijving), border=1, ln=False, align="L")
        pdf.cell(15, 10, txt=str(bevat_product.hoeveelheid), border=1, ln=False, align="C")
        pdf.cell(20, 10, txt=f"{bevat_product.product.eenheidsprijs:.2f}", border=1, ln=False, align="R")
        pdf.cell(30, 10, txt=f"{bevat_product.product.eenheidsprijs * bevat_product.hoeveelheid:.2f}", border=1, ln=True, align="R")

    # Betaalinformatie, Uiterste betaaldatum, Totaal verschuldigd
    pdf.cell(100, 10, txt=f"Betaalinformatie:", ln=True)
    pdf.cell(100, 10, txt=f"Bank: {factuur.bedrijf.bank}", ln=False)
    pdf.cell(0, 10, txt=f"Totaal excl. BTW: {factuur.totaalbedrag_excl:.2f} EUR", ln=True, align="R")
    pdf.cell(100, 10, txt=f"IBAN: {factuur.bedrijf.iban}", ln=False)
    pdf.cell(0, 10, txt=f"BTW: {factuur.btw_bedrag:.2f} EUR", ln=True, align="R")
    pdf.cell(100, 10, txt=f"BIC: {factuur.bedrijf.bic}", ln=False)
    pdf.cell(0, 10, txt=f"Totaal incl. BTW: {factuur.totaalbedrag_incl:.2f} EUR", ln=True, align="R")

    pdf.ln(10)

    pdf.cell(0, 10, txt=f"Gelieve het bedrag van {factuur.totaalbedrag_incl} EUR te betalen voor {factuur.uiterste_betaaldatum}, onder vermelding van het factuurnummer {factuur.factuurnummer}.", ln=True)
    pdf.cell(0, 10, txt=f"Alvast bedankt!", ln=True)

    pdf.output(f"{factuur.factuurnummer}.pdf")
    with open(f"{factuur.factuurnummer}.pdf", "rb") as f:
        pdf = f.read()
    factuur.pdf = pdf
    os.remove(f"{factuur.factuurnummer}.pdf")
    return factuur