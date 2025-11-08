"""
Test the fixed parsing logic directly
"""

import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Sample markdown from actual Indonetwork page
SAMPLE_MARKDOWN = """
[Download Aplikasi](https://play.google.com/store/apps/details?id=id.co.indonetwork.adiperkasa.mampang)

### Selamat Datang

##### Penjual

[Cara Daftar Penjual](https://www.indonetwork.co.id/page/cara-daftar-penjual) [Mulai Jual Produk](https://www.indonetwork.co.id/page/cara-jual-produk) [Seller Center (Informasi Penjual)](https://www.indonetwork.co.id/page/seller-center)

# Botol Spray Pet 100ml | Botol PET Kosmetik Skincare 100 ml

Kategori

[Botol PET](https://www.indonetwork.co.id/k/botol-pet)

Update Terakhir

14 / 10 / 2025

Minimum Pembelian

1 Botol

Dilihat Sebanyak

33 Kali

* * *

Harga

CALL

* * *

CONTACT PERSON

WHATSAPP : 0822-2424-9969

### CV. Emba Plast

**EMBA PLAST** merupakan Perusahaan yang bergerak di Bidang **Packaging Cosmetic & Pharmasi**.

**Alamat kami di:**

Perumahan Golden Berry Regency Blok DG 07
Menganti Gresik, Jawa Timur, Indonesia

### [CV. Emba Plast](https://www.indonetwork.co.id/company/embaplast)

Premium Gold

7 Tahun

Perumahan Golden Berry Blok DG 07 Menganti Gresik, 61174 - Kabupaten Gresik, Jawa Timur, Indonesia -61174

**Login Terakhir 06 / 08 / 2025**
"""

def test_parsing():
    """Test the parsing logic"""
    
    print("=" * 70)
    print("TESTING FIXED PARSING LOGIC")
    print("=" * 70)
    print()
    
    markdown = SAMPLE_MARKDOWN
    
    # 1. Test company name extraction
    print("1. COMPANY NAME EXTRACTION:")
    print("-" * 70)
    company_match = re.search(r'###\s+((?:CV\.|PT\.|UD\.|Toko\s)\s*[^\n]+)', markdown, re.IGNORECASE)
    if not company_match:
        company_match = re.search(r'### \[([^\]]+)\]\(https://www\.indonetwork\.co\.id/company/', markdown)
    
    company_name = company_match.group(1).strip() if company_match else "Unknown Supplier"
    print(f"✅ Company Name: {company_name}")
    print()
    
    # 2. Test product name extraction
    print("2. PRODUCT NAME EXTRACTION:")
    print("-" * 70)
    product_match = re.search(r'^# (.+)$', markdown, re.MULTILINE)
    product_name = product_match.group(1).strip() if product_match else "Product"
    print(f"✅ Product Name: {product_name}")
    print()
    
    # 3. Test WhatsApp extraction
    print("3. WHATSAPP EXTRACTION:")
    print("-" * 70)
    whatsapp_match = re.search(r'(?:WHATSAPP|WhatsApp|WA)\s*[:：]\s*([\d\-\+\(\)\s]+)', markdown, re.IGNORECASE)
    whatsapp = ""
    if whatsapp_match:
        whatsapp = whatsapp_match.group(1).strip()
    else:
        whatsapp_match = re.search(r'(0\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})', markdown)
        if whatsapp_match:
            whatsapp = whatsapp_match.group(1).strip()
    
    print(f"✅ WhatsApp: {whatsapp}")
    print()
    
    # 4. Test location extraction
    print("4. LOCATION EXTRACTION:")
    print("-" * 70)
    address_match = re.search(r'(?:Perumahan|Jalan|Jl\.|Gedung|Kompleks)\s+([^\n]+)\n([^\n]+?(?:Jakarta|Surabaya|Bandung|Semarang|Yogyakarta|Bali|Gresik|Tangerang|Bekasi|Bogor|Depok|Malang|Medan)[^\n]*)', markdown, re.IGNORECASE | re.DOTALL)
    if address_match:
        location = f"{address_match.group(1).strip()}, {address_match.group(2).strip()}"
    else:
        location_match = re.search(r'([^\n]*(?:Jakarta|Surabaya|Bandung|Semarang|Yogyakarta|Bali|Gresik|Tangerang|Bekasi|Bogor|Depok|Malang|Medan)[^\n]*)', markdown, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else "Indonesia"
    
    print(f"✅ Location: {location}")
    print()
    
    # 5. Test MOQ extraction
    print("5. MINIMUM ORDER QUANTITY:")
    print("-" * 70)
    moq_match = re.search(r'Minimum Pembelian\s*\n\s*(\d+)', markdown, re.IGNORECASE)
    if not moq_match:
        moq_match = re.search(r'(?:MOQ|Minimum Order|Min\. Order)[:\s]*([0-9]+)', markdown, re.IGNORECASE)
    moq = int(moq_match.group(1)) if moq_match else 1
    print(f"✅ MOQ: {moq}")
    print()
    
    # 6. Test city extraction
    print("6. CITY EXTRACTION:")
    print("-" * 70)
    major_cities = ['Jakarta', 'Surabaya', 'Bandung', 'Semarang', 'Yogyakarta', 'Bali', 'Gresik', 'Tangerang', 'Bekasi', 'Bogor', 'Depok', 'Malang', 'Medan']
    city = "Indonesia"
    for c in major_cities:
        if c.lower() in location.lower():
            city = c
            break
    print(f"✅ City: {city}")
    print()
    
    print("=" * 70)
    print("SUMMARY OF EXTRACTED DATA:")
    print("=" * 70)
    print(f"""
Company Name:  {company_name}
Product:       {product_name}
WhatsApp:      {whatsapp}
Location:      {location}
City:          {city}
MOQ:           {moq}
    """)
    
    # Check if all critical fields are extracted correctly
    all_good = True
    if company_name == "Unknown Supplier" or "Cara Daftar" in company_name:
        print("❌ FAIL: Company name extraction failed")
        all_good = False
    else:
        print("✅ PASS: Company name extracted correctly")
    
    if not whatsapp or whatsapp == "-":
        print("❌ FAIL: WhatsApp extraction failed")
        all_good = False
    else:
        print("✅ PASS: WhatsApp extracted correctly")
    
    if city == "Indonesia":
        print("❌ FAIL: City extraction failed")
        all_good = False
    else:
        print("✅ PASS: City extracted correctly")
    
    print()
    if all_good:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Review the extraction logic")

if __name__ == "__main__":
    test_parsing()
