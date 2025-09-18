#!/usr/bin/env python3
"""
Script per monitorare in tempo reale i dati di tracking
Ricarica automaticamente il file backup ogni 5 secondi
"""

import time
import os
import json
from datetime import datetime
from pathlib import Path

def clear_screen():
    """Pulisce lo schermo"""
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_tracking():
    """Monitora i dati di tracking in tempo reale"""
    backup_file = Path("tracking_backup.txt")
    last_size = 0
    
    print("🔄 MONITOR TRACKING TEMPO REALE")
    print("=" * 50)
    print("⏰ Aggiornamento ogni 5 secondi")
    print("🛑 Premi Ctrl+C per fermare")
    print("=" * 50)
    
    while True:
        try:
            if backup_file.exists():
                current_size = backup_file.stat().st_size
                
                # Se il file è cambiato, ricarica i dati
                if current_size != last_size:
                    clear_screen()
                    print("🔄 MONITOR TRACKING TEMPO REALE")
                    print("=" * 50)
                    print(f"⏰ Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}")
                    print("🛑 Premi Ctrl+C per fermare")
                    print("=" * 50)
                    
                    # Leggi e mostra i dati
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    gps_count = 0
                    phone_count = 0
                    session_count = 0
                    
                    print("📄 CONTENUTO FILE:")
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        print(line)
                        
                        # Conta i diversi tipi di eventi
                        if '📍 GPS:' in line:
                            gps_count += 1
                        elif '📱 Tel:' in line:
                            phone_count += 1
                        elif 'SESSION_COMPLETE' in line:
                            session_count += 1
                    
                    print("\n" + "=" * 50)
                    print("📊 STATISTICHE LIVE:")
                    print(f"📍 Coordinate GPS: {gps_count}")
                    print(f"📱 Numeri telefono: {phone_count}")
                    print(f"✅ Sessioni complete: {session_count}")
                    print(f"📁 Dimensione file: {current_size} bytes")
                    
                    last_size = current_size
                else:
                    # Mostra solo un punto per indicare che sta monitorando
                    print(f"⏳ Monitoraggio attivo... {datetime.now().strftime('%H:%M:%S')}", end='\r')
            else:
                print("❌ File tracking_backup.txt non trovato!")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoraggio fermato dall'utente")
            break
        except Exception as e:
            print(f"❌ Errore: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    monitor_tracking()