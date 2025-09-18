#!/usr/bin/env python3
"""
Script per leggere e formattare i dati di tracking salvati nel backup locale
"""

import json
from datetime import datetime
from pathlib import Path

def leggi_tracking_backup():
    """Legge e formatta i dati dal file di backup tracking"""
    backup_file = Path("tracking_backup.txt")
    
    if not backup_file.exists():
        print("❌ File tracking_backup.txt non trovato!")
        return
    
    print("📊 DATI DI TRACKING - BACKUP LOCALE")
    print("="*50)
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        gps_data = []
        phone_data = []
        sessions = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('===') or 'INIZIALIZZATO' in line or 'Formato dati:' in line:
                continue
            
            print(line)
            
            # Estrai dati GPS per riassunto
            if '📍 GPS:' in line:
                try:
                    coords = line.split('GPS: ')[1]
                    lat, lon = coords.split(', ')
                    gps_data.append((lat, lon))
                except:
                    pass
            
            # Estrai numeri telefono
            elif '📱 Tel:' in line:
                try:
                    phone = line.split('Tel: ')[1]
                    phone_data.append(phone)
                except:
                    pass
        
        # Riassunto
        print("\n" + "="*50)
        print("📈 RIASSUNTO TRACKING:")
        print(f"📍 Coordinate GPS catturate: {len(gps_data)}")
        print(f"📱 Numeri telefono catturati: {len(phone_data)}")
        
        if gps_data:
            print("\n🗺️ COORDINATE GPS UNICHE:")
            unique_coords = list(set(gps_data))
            for i, (lat, lon) in enumerate(unique_coords, 1):
                print(f"  {i}. Lat: {lat}, Lon: {lon}")
                print(f"     Google Maps: https://www.google.com/maps?q={lat},{lon}")
        
        if phone_data:
            print(f"\n📞 NUMERI TELEFONO UNICI:")
            unique_phones = list(set(phone_data))
            for i, phone in enumerate(unique_phones, 1):
                print(f"  {i}. {phone}")
        
    except Exception as e:
        print(f"❌ Errore lettura file: {e}")

if __name__ == "__main__":
    leggi_tracking_backup()