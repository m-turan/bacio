import requests
import xml.etree.ElementTree as ET
import os
from pathlib import Path
from ftplib import FTP
import tempfile

def download_xml(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def upload_to_ftp(xml_content, ftp_config):
    """
    XML içeriğini FTP ile sunucuya yükler
    
    Args:
        xml_content: XML içeriği (bytes)
        ftp_config: FTP bağlantı bilgileri (dict)
    """
    try:
        # FTP bağlantısı kur
        ftp = FTP()
        ftp.connect(ftp_config['host'], ftp_config['port'])
        ftp.login(ftp_config['username'], ftp_config['password'])
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as temp_file:
            temp_file.write(xml_content)
            temp_file_path = temp_file.name
        
        # Dosyayı FTP ile yükle
        with open(temp_file_path, 'rb') as file:
            ftp.storbinary(f'STOR {ftp_config["remote_filename"]}', file)
        
        # Geçici dosyayı sil
        os.unlink(temp_file_path)
        
        # FTP bağlantısını kapat
        ftp.quit()
        
        print(f"XML başarıyla FTP ile yüklendi: {ftp_config['host']}/{ftp_config['remote_filename']}")
        return True
        
    except Exception as e:
        print(f"FTP yükleme hatası: {str(e)}")
        return False

def convert_and_save_xml(source_xml_content, output_filename="baciodeneme.xml", ftp_config=None):
    # Kaynak XML'i parse et
    root = ET.fromstring(source_xml_content)
    # Yeni kök oluştur
    new_root = ET.Element("products")

    # Her ürün için dönüştür
    for i, product in enumerate(root.findall(".//product"), 1):
        new_product = ET.SubElement(new_root, "product")
        # <id>
        ET.SubElement(new_product, "id").text = str(i)
        # <productCode>
        ET.SubElement(new_product, "productCode").text = (product.findtext("code") or "").strip()
        # <barcode>
        ET.SubElement(new_product, "barcode").text = (product.findtext("barcode") or "").strip()
        # <main_category>
        ET.SubElement(new_product, "main_category").text = "İÇ GİYİM"
        # <top_category>
        ET.SubElement(new_product, "top_category").text = (product.findtext("cat1name") or "").strip()
        # <sub_category>
        ET.SubElement(new_product, "sub_category").text = (product.findtext("cat2name") or "").strip()
        # <sub_category_>
        ET.SubElement(new_product, "sub_category_").text = ""
        # <categoryID>
        ET.SubElement(new_product, "categoryID").text = "44"
        # <category>
        main_cat = "İÇ GİYİM"
        top_cat = product.findtext("cat1name") or ""
        sub_cat = product.findtext("cat2name") or ""
        ET.SubElement(new_product, "category").text = f"{main_cat} >>> {top_cat or sub_cat}"
        # <active>
        ET.SubElement(new_product, "active").text = "1"
        # <brandID>
        ET.SubElement(new_product, "brandID").text = "2"
        # <brand>
        ET.SubElement(new_product, "brand").text = (product.findtext("brand") or "").strip()
        # <name>
        ET.SubElement(new_product, "name").text = (product.findtext("name") or "").strip()
        # <description>
        ET.SubElement(new_product, "description").text = (product.findtext("detail") or "").strip()
        # <variants>
        variants_elem = ET.SubElement(new_product, "variants")
        subproducts = product.find("subproducts")
        if subproducts is not None:
            for subproduct in subproducts.findall("subproduct"):
                variant_elem = ET.SubElement(variants_elem, "variant")
                ET.SubElement(variant_elem, "name1").text = "Renk"
                ET.SubElement(variant_elem, "value1").text = (subproduct.findtext("type1") or "").strip()
                ET.SubElement(variant_elem, "name2").text = "Beden"
                ET.SubElement(variant_elem, "value2").text = (subproduct.findtext("type2") or "").strip()
                ET.SubElement(variant_elem, "quantity").text = subproduct.findtext("stock") or "0"
                ET.SubElement(variant_elem, "barcode").text = (subproduct.findtext("barcode") or "").strip()
        # <image1>, <image2>, <image3>
        images = product.find("images")
        if images is not None:
            img_items = images.findall("img_item")
            for idx in range(3):
                img_elem = ET.SubElement(new_product, f"image{idx+1}")
                if idx < len(img_items):
                    img_elem.text = (img_items[idx].text or "").strip()
                else:
                    img_elem.text = ""
        else:
            for idx in range(3):
                ET.SubElement(new_product, f"image{idx+1}").text = ""
        # <listPrice>
        ET.SubElement(new_product, "listPrice").text = product.findtext("price_list") or "0.00"
        # <price>
        ET.SubElement(new_product, "price").text = product.findtext("price_special") or "0.00"
        # <tax>
        tax = product.findtext("vat") or "0.1"
        try:
            tax_val = float(tax)
            tax_val = tax_val / 100 if tax_val > 1 else tax_val
        except Exception:
            tax_val = 0.1
        ET.SubElement(new_product, "tax").text = str(tax_val)
        # <currency>
        currency = product.findtext("currency") or "TRY"
        ET.SubElement(new_product, "currency").text = currency.replace("TL", "TRY")
        # <desi>
        ET.SubElement(new_product, "desi").text = product.findtext("desi") or "1"
        # <quantity>
        ET.SubElement(new_product, "quantity").text = product.findtext("stock") or "0"

    # XML'i string olarak oluştur
    tree = ET.ElementTree(new_root)
    
    # XML içeriğini bytes olarak al
    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    
    if ftp_config:
        # FTP ile yükle
        success = upload_to_ftp(xml_bytes, ftp_config)
        if not success:
            # FTP başarısız olursa locale kaydet
            desktop = Path.home() / "Desktop"
            output_path = desktop / output_filename
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            print(f"FTP başarısız oldu, locale kaydedildi: {output_path}")
    else:
        # Sadece locale kaydet
        desktop = Path.home() / "Desktop"
        output_path = desktop / output_filename
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"XML başarıyla kaydedildi: {output_path}")

def main():
    # FTP bağlantı bilgileri - Bu bilgileri kendi hosting bilgilerinizle değiştirin
    ftp_config = {
        'host': 'ftp.eterella.com',  # FTP sunucu adresi
        'port': 21,                     # FTP port (genellikle 21)
        'username': 'windamdx',    # FTP kullanıcı adı
        'password': 'c_bJ!-PGMwG57#Hx',    # FTP şifre
        'remote_filename': '/public_html/yasinxml/baciodeneme.xml'  # Sunucuda kaydedilecek dosya adı
    }
    
    url = "https://bacioicgiyim.com.tr/priodcutsxml/products.xml"
    xml_content = download_xml(url)
    
    # FTP ile yükle (ftp_config None ise sadece locale kaydeder)
    convert_and_save_xml(xml_content, ftp_config=ftp_config)

if __name__ == "__main__":
    main() 