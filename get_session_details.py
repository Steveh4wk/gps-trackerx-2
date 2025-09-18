#!/usr/bin/env python3
"""
Script per estrarre TUTTI i dati dettagliati di una specifica sessione
Usa il Session ID per trovare informazioni complete
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def get_session_details(session_id):
    """Estrae tutti i dati dettagliati per un session ID specifico"""
    
    print(f"🔍 DETTAGLI COMPLETI SESSIONE: {session_id}")
    print("=" * 70)
    
    # 1. CERCA NEL BACKUP TXT
    backup_file = Path("tracking_backup.txt")
    if backup_file.exists():
        print("📄 BACKUP TXT:")
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        session_events = []
        for line in lines:
            if session_id in line:
                session_events.append(line.strip())
        
        if session_events:
            for event in session_events:
                print(f"  {event}")
        else:
            print(f"  ❌ Sessione {session_id} non trovata nel backup")
    
    print("\n" + "=" * 70)
    
    # 2. CERCA NEL FILE JSONL SPECIFICO DELLA SESSIONE
    session_file = Path(f"data/tracking/{session_id}.jsonl")
    if session_file.exists():
        print("📋 DATI JSONL COMPLETI:")
        with open(session_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            try:
                data = json.loads(line.strip())
                print(f"\n🔹 EVENTO {i}: {data.get('eventType', 'UNKNOWN')}")
                print(f"   ⏰ Timestamp: {data.get('timestamp')}")
                print(f"   🌐 User Agent: {data.get('userAgent', 'N/A')}")
                print(f"   🔗 Referrer: {data.get('referrer', 'N/A')}")
                print(f"   📍 URL: {data.get('url', 'N/A')}")
                
                # Dettagli specifici per tipo evento
                event_data = data.get('data', {})
                if data.get('eventType') == 'device_info_captured':
                    print(f"   📱 INFORMAZIONI DISPOSITIVO:")
                    if 'screen' in event_data:
                        screen = event_data['screen']
                        print(f"      🖥️  Schermo: {screen.get('width')}x{screen.get('height')}")
                    if 'browser' in event_data:
                        browser = event_data['browser']
                        print(f"      🌐 Browser: {browser.get('userAgent', 'N/A')}")
                        print(f"      🗣️  Lingua: {browser.get('language', 'N/A')}")
                        print(f"      💾 Platform: {browser.get('platform', 'N/A')}")
                    if 'hardware' in event_data:
                        hw = event_data['hardware']
                        print(f"      🔧 RAM: {hw.get('deviceMemory', 'N/A')} GB")
                        print(f"      ⚙️  CPU Cores: {hw.get('hardwareConcurrency', 'N/A')}")
                    if 'connection' in event_data and event_data['connection']:
                        conn = event_data['connection']
                        print(f"      📶 Rete: {conn.get('effectiveType', 'N/A')}")
                        print(f"      ⚡ Velocità: {conn.get('downlink', 'N/A')} Mbps")
                
                elif data.get('eventType') == 'ip_info_captured':
                    print(f"   🌐 INFORMAZIONI IP:")
                    print(f"      🔍 IP: {event_data.get('ip', 'N/A')}")
                    print(f"      🏙️  Città: {event_data.get('city', 'N/A')}")
                    print(f"      🌍 Paese: {event_data.get('country', 'N/A')}")
                    print(f"      📡 ISP: {event_data.get('isp', 'N/A')}")
                    if 'latitude' in event_data and 'longitude' in event_data:
                        print(f"      📍 GPS IP: {event_data['latitude']}, {event_data['longitude']}")
                
                elif data.get('eventType') == 'location_captured_immediate':
                    print(f"   📍 GPS IMMEDIATO:")
                    print(f"      🎯 Coordinate: {event_data.get('latitude')}, {event_data.get('longitude')}")
                    print(f"      🎯 Accuratezza: {event_data.get('accuracy', 'N/A')} metri")
                    print(f"      📈 Altitudine: {event_data.get('altitude', 'N/A')} m")
                    print(f"      🧭 Direzione: {event_data.get('heading', 'N/A')}°")
                    print(f"      🏃 Velocità: {event_data.get('speed', 'N/A')} m/s")
                
                elif data.get('eventType') == 'battery_info_captured':
                    print(f"   🔋 BATTERIA:")
                    print(f"      ⚡ Carica: {event_data.get('level', 'N/A') * 100 if event_data.get('level') else 'N/A'}%")
                    print(f"      🔌 In ricarica: {'Sì' if event_data.get('charging') else 'No'}")
                
                elif data.get('eventType') == 'phone_captured':
                    print(f"   📱 TELEFONO:")
                    print(f"      📞 Numero: {event_data.get('phone', 'N/A')}")
                
                # Mostra tutti i dati raw se richiesto
                if len(str(event_data)) < 200:
                    print(f"   📊 Raw Data: {json.dumps(event_data, ensure_ascii=False)}")
                else:
                    print(f"   📊 Raw Data: {len(str(event_data))} caratteri (troppo lungo da mostrare)")
                    
            except json.JSONDecodeError:
                print(f"❌ Errore parsing riga {i}")
    else:
        print(f"❌ File sessione {session_file} non trovato")
    
    print("\n" + "=" * 70)
    
    # 3. CERCA NEI FILE AGGREGATI
    print("📊 DATI AGGREGATI:")
    
    # GPS coordinates
    gps_file = Path("data/tracking/gps_coordinates.jsonl")
    if gps_file.exists():
        with open(gps_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('session_id') == session_id:
                        print(f"📍 GPS: {data.get('latitude')}, {data.get('longitude')} (±{data.get('accuracy')}m)")
                except:
                    pass
    
    # Phone numbers
    phones_file = Path("data/tracking/phone_numbers.jsonl")
    if phones_file.exists():
        with open(phones_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('session_id') == session_id:
                        print(f"📱 Telefono: {data.get('phone')}")
                except:
                    pass
    
    # Session summaries
    summary_file = Path("data/tracking/session_summaries.jsonl")
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if session_id in str(data):
                        print(f"✅ Summary: {json.dumps(data, ensure_ascii=False)}")
                except:
                    pass

def list_available_sessions():
    """Lista tutte le sessioni disponibili"""
    print("📋 SESSIONI DISPONIBILI:")
    print("=" * 30)
    
    # Cerca nei file di sessione
    tracking_dir = Path("data/tracking")
    if tracking_dir.exists():
        session_files = list(tracking_dir.glob("session_*.jsonl"))
        if session_files:
            for session_file in session_files:
                session_id = session_file.stem
                print(f"  🔹 {session_id}")
        else:
            print("  ❌ Nessuna sessione trovata")
    
    # Cerca nel backup
    backup_file = Path("tracking_backup.txt")
    if backup_file.exists():
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        sessions = set(re.findall(r'session_\w+', content))
        if sessions:
            print(f"\n📄 Dal backup TXT:")
            for session in sorted(sessions):
                print(f"  🔹 {session}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        if session_id.lower() == 'list':
            list_available_sessions()
        else:
            get_session_details(session_id)
    else:
        print("💡 Uso: python get_session_details.py <session_id>")
        print("💡 O: python get_session_details.py list")
        print()
        list_available_sessions()
