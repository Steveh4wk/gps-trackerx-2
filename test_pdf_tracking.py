#!/usr/bin/env python3
"""
Test script per verificare che il PDF tracking funzioni
"""

import requests
import os
from pathlib import Path

def test_pdf_endpoint():
    """Test che il PDF sia servito correttamente dal web server"""
    print("🧪 TESTING PDF ENDPOINT")
    print("=" * 30)
    
    try:
        # Test localhost
        response = requests.get('http://localhost:5000/pdf/psicologia', timeout=5)
        if response.status_code == 200:
            print("✅ PDF endpoint locale funziona!")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ PDF endpoint locale fallito: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore connessione locale: {e}")
    
    return False

def check_pdf_files():
    """Verifica che i PDF siano stati creati correttamente"""
    print("\n🗂️ CHECKING PDF FILES")
    print("=" * 30)
    
    files_to_check = [
        "PSICOLOGIA GIURIDICA AIPG.pdf",
        "PSICOLOGIA GIURIDICA AIPG_ORIGINAL.pdf"
    ]
    
    all_good = True
    for filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename}: {size:,} bytes")
        else:
            print(f"❌ {filename}: NON TROVATO")
            all_good = False
    
    return all_good

def simulate_pdf_tracking():
    """Simula quello che succede quando qualcuno apre il PDF"""
    print("\n🎯 SIMULATING PDF TRACKING")
    print("=" * 30)
    
    # Simula dati che il PDF invierebbe
    mock_pdf_data = {
        "sessionId": "pdf_psicologia_test123",
        "eventType": "pdf_psicologia_opened",
        "timestamp": "2025-09-18T12:20:00.000Z",
        "userAgent": "Mozilla/5.0 (PDF Reader Test)",
        "source": "PDF_PSICOLOGIA_GIURIDICA",
        "document_name": "PSICOLOGIA GIURIDICA AIPG.pdf",
        "data": {
            "document_title": "PSICOLOGIA GIURIDICA AIPG",
            "reader": "Adobe_Acrobat",
            "page_count": 50
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/track',
            json=mock_pdf_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ PDF tracking simulation successful!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ PDF tracking simulation failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error simulating PDF tracking: {e}")
    
    return False

def check_tracking_data():
    """Controlla se i dati di tracking PDF sono nei backup"""
    print("\n📊 CHECKING TRACKING DATA")
    print("=" * 30)
    
    backup_files = [
        "tracking_backup.txt",
        "Nuovo Documento di testo.txt"
    ]
    
    found_pdf_data = False
    for backup_file in backup_files:
        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'pdf_psicologia' in content.lower():
                print(f"✅ Trovati dati PDF in: {backup_file}")
                # Mostra le righe con pdf_psicologia
                lines = content.split('\n')
                pdf_lines = [line for line in lines if 'pdf_psicologia' in line.lower()]
                for line in pdf_lines[:3]:  # Mostra prime 3
                    print(f"   {line[:80]}...")
                found_pdf_data = True
                break
    
    if not found_pdf_data:
        print("📭 Nessun dato PDF tracking trovato nei backup")
        print("   (Normale se il PDF non è ancora stato aperto)")
    
    return found_pdf_data

def main():
    print("🎯 PDF TRACKING - TEST COMPLETO")
    print("=" * 40)
    
    # Check dei file
    files_ok = check_pdf_files()
    
    # Test endpoint (solo se web server è attivo)
    endpoint_ok = test_pdf_endpoint()
    
    # Simula tracking
    tracking_ok = simulate_pdf_tracking()
    
    # Controlla dati
    data_found = check_tracking_data()
    
    print("\n📋 SUMMARY")
    print("=" * 20)
    print(f"PDF Files: {'✅' if files_ok else '❌'}")
    print(f"Web Endpoint: {'✅' if endpoint_ok else '❌'}")
    print(f"Tracking API: {'✅' if tracking_ok else '❌'}")
    print(f"Data in Backup: {'✅' if data_found else '📭'}")
    
    if files_ok and endpoint_ok and tracking_ok:
        print("\n🎉 TUTTO FUNZIONA!")
        print("\n💡 NEXT STEPS:")
        print("1. Condividi: PSICOLOGIA GIURIDICA AIPG.pdf")
        print("2. URL web: http://localhost:5000/pdf/psicologia")
        print("3. Monitora i backup per i dati PDF")
        print("4. Session ID PDF iniziano con 'pdf_psicologia_'")
    else:
        print("\n⚠️ Alcuni test falliti. Check i dettagli sopra.")
        if not endpoint_ok:
            print("   Assicurati che il web server sia in running:")
            print("   python web_server.py")

if __name__ == "__main__":
    main()