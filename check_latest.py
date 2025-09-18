#!/usr/bin/env python3
"""
Script rapido per controllare l'ultima attività di tracking
"""

from datetime import datetime
from pathlib import Path

def check_latest_activity():
    """Controlla l'ultima attività senza monitor continuo"""
    backup_file = Path("tracking_backup.txt")
    
    if not backup_file.exists():
        print("❌ File tracking_backup.txt non trovato!")
        return
    
    print("🔍 CHECK RAPIDO TRACKING")
    print("=" * 30)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 30)
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Statistiche rapide
        gps_count = 0
        phone_count = 0
        session_count = 0
        last_activity = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('===') or 'INIZIALIZZATO' in line:
                continue
                
            # Estrai timestamp dall'ultima riga con timestamp
            if line.startswith('['):
                last_activity = line
            
            # Conta eventi
            if '📍 GPS:' in line:
                gps_count += 1
            elif '📱 Tel:' in line:
                phone_count += 1
            elif 'SESSION_COMPLETE' in line:
                session_count += 1
        
        # Mostra risultati
        print(f"📊 STATISTICHE:")
        print(f"  📍 GPS catturati: {gps_count}")
        print(f"  📱 Telefoni: {phone_count}")
        print(f"  ✅ Sessioni: {session_count}")
        print(f"  📁 Righe totali: {len([l for l in lines if l.strip()])}")
        
        if last_activity:
            print(f"\n🕐 ULTIMA ATTIVITÀ:")
            print(f"  {last_activity}")
        else:
            print(f"\n📭 Nessuna attività di tracking ancora")
            
        # Dimensione file
        file_size = backup_file.stat().st_size
        print(f"\n📦 Dimensione file: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Errore lettura: {e}")

if __name__ == "__main__":
    check_latest_activity()