#!/usr/bin/env python3
"""
Script per analizzare tutti i dati di tracking raccolti
"""

import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_client_info():
    """Analizza le informazioni sui client"""
    print("👥 ANALISI CLIENT INFO")
    print("=" * 30)
    
    client_file = Path("data/tracking/client_info.jsonl")
    if not client_file.exists():
        print("❌ File client_info.jsonl non trovato")
        return
    
    clients = []
    with open(client_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                clients.append(json.loads(line.strip()))
            except:
                continue
    
    if not clients:
        print("📭 Nessun dato client trovato")
        return
    
    print(f"📊 Totale sessioni: {len(clients)}")
    
    # Raggruppa per IP
    ips = defaultdict(list)
    devices = defaultdict(int)
    browsers = defaultdict(int)
    
    for client in clients:
        ip = client.get('client_info', {}).get('ip', 'unknown')
        ips[ip].append(client)
        
        device_info = client.get('client_info', {}).get('device', {})
        if device_info.get('is_android'):
            devices['Android'] += 1
        elif device_info.get('is_iphone'):
            devices['iPhone'] += 1
        elif device_info.get('is_ipad'):
            devices['iPad'] += 1
        elif device_info.get('is_windows'):
            devices['Windows'] += 1
        elif device_info.get('is_macos'):
            devices['macOS'] += 1
        elif device_info.get('is_linux'):
            devices['Linux'] += 1
        else:
            devices['Unknown'] += 1
        
        ua = client.get('client_info', {}).get('user_agent', '').lower()
        if 'firefox' in ua:
            browsers['Firefox'] += 1
        elif 'chrome' in ua:
            browsers['Chrome'] += 1
        elif 'safari' in ua:
            browsers['Safari'] += 1
        elif 'edge' in ua:
            browsers['Edge'] += 1
        else:
            browsers['Other'] += 1
    
    print(f"\n🌐 IP Unici: {len(ips)}")
    for ip, sessions in ips.items():
        print(f"   {ip}: {len(sessions)} sessioni")
    
    print(f"\n📱 Dispositivi:")
    for device, count in devices.items():
        print(f"   {device}: {count}")
    
    print(f"\n🌍 Browser:")
    for browser, count in browsers.items():
        print(f"   {browser}: {count}")

def analyze_gps_data():
    """Analizza i dati GPS"""
    print("\n\n📍 ANALISI DATI GPS")
    print("=" * 30)
    
    gps_file = Path("data/tracking/gps_coordinates.jsonl")
    if not gps_file.exists():
        print("❌ File gps_coordinates.jsonl non trovato")
        return
    
    coords = []
    with open(gps_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                coords.append(json.loads(line.strip()))
            except:
                continue
    
    if not coords:
        print("📭 Nessun dato GPS trovato")
        return
    
    print(f"📊 Totale coordinate: {len(coords)}")
    
    # Analisi accuracy
    accuracies = [c.get('accuracy', 0) for c in coords if c.get('accuracy')]
    if accuracies:
        avg_acc = sum(accuracies) / len(accuracies)
        min_acc = min(accuracies)
        max_acc = max(accuracies)
        
        print(f"\n🎯 Precisione GPS:")
        print(f"   Media: {avg_acc:.1f} metri")
        print(f"   Migliore: {min_acc:.1f} metri")
        print(f"   Peggiore: {max_acc:.1f} metri")
        
        # Clasifica precisione
        excellent = sum(1 for a in accuracies if a <= 5)
        good = sum(1 for a in accuracies if 5 < a <= 20)
        poor = sum(1 for a in accuracies if 20 < a <= 100)
        bad = sum(1 for a in accuracies if a > 100)
        
        print(f"\n📊 Qualità GPS:")
        print(f"   Eccellente (≤5m): {excellent}")
        print(f"   Buona (5-20m): {good}")
        print(f"   Scarsa (20-100m): {poor}")
        print(f"   Pessima (>100m): {bad}")
    
    # Raggruppa per IP
    ips_gps = defaultdict(list)
    for coord in coords:
        ip = coord.get('ip', 'unknown')
        ips_gps[ip].append(coord)
    
    print(f"\n🌐 GPS per IP:")
    for ip, gps_list in ips_gps.items():
        print(f"   {ip}: {len(gps_list)} coordinate")

def analyze_phone_data():
    """Analizza i dati telefono"""
    print("\n\n📱 ANALISI NUMERI TELEFONO")
    print("=" * 30)
    
    phone_file = Path("data/tracking/phone_numbers.jsonl")
    if not phone_file.exists():
        print("❌ File phone_numbers.jsonl non trovato")
        return
    
    phones = []
    with open(phone_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                phones.append(json.loads(line.strip()))
            except:
                continue
    
    if not phones:
        print("📭 Nessun numero di telefono trovato")
        return
    
    print(f"📊 Totale numeri: {len(phones)}")
    
    # Raggruppa per numero
    numbers = defaultdict(list)
    for phone in phones:
        num = phone.get('phone', 'unknown')
        numbers[num].append(phone)
    
    print(f"\n📞 Numeri unici: {len(numbers)}")
    for num, entries in numbers.items():
        ip_list = list(set(e.get('ip', 'unknown') for e in entries))
        print(f"   {num}: {len(entries)} catture, IP: {ip_list}")

def analyze_sessions():
    """Analizza le sessioni complete"""
    print("\n\n🎯 ANALISI SESSIONI COMPLETE")
    print("=" * 30)
    
    sessions_file = Path("data/tracking/session_summaries.jsonl")
    if not sessions_file.exists():
        print("❌ File session_summaries.jsonl non trovato")
        return
    
    sessions = []
    with open(sessions_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                sessions.append(json.loads(line.strip()))
            except:
                continue
    
    if not sessions:
        print("📭 Nessuna sessione completa trovata")
        return
    
    print(f"📊 Sessioni complete: {len(sessions)}")
    
    for i, session in enumerate(sessions, 1):
        ip = session.get('client_info', {}).get('ip', 'unknown')
        phone = session.get('phone', 'N/A')
        location = session.get('location', {})
        lat = location.get('latitude', 'N/A')
        lon = location.get('longitude', 'N/A')
        acc = location.get('accuracy', 'N/A')
        
        print(f"\n   Sessione {i}:")
        print(f"   • IP: {ip}")
        print(f"   • Telefono: {phone}")
        print(f"   • GPS: {lat}, {lon} (±{acc}m)")

def show_recent_activity():
    """Mostra attività recente dal backup"""
    print("\n\n⏰ ATTIVITÀ RECENTE")
    print("=" * 30)
    
    backup_file = Path("tracking_backup.txt")
    if not backup_file.exists():
        print("❌ File tracking_backup.txt non trovato")
        return
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mostra ultime 10 righe con dati
    data_lines = [line for line in lines if 'Session:' in line]
    recent = data_lines[-10:] if len(data_lines) > 10 else data_lines
    
    if not recent:
        print("📭 Nessuna attività recente")
        return
    
    print(f"📊 Ultime {len(recent)} attività:")
    for line in recent:
        line = line.strip()
        if line:
            print(f"   {line[:100]}...")

def main():
    print("🔍 ANALISI COMPLETA TRACKING GPS")
    print("=" * 50)
    
    try:
        analyze_client_info()
        analyze_gps_data() 
        analyze_phone_data()
        analyze_sessions()
        show_recent_activity()
        
        print("\n\n✅ Analisi completata!")
        print("\n💡 Per vedere tutti i dettagli:")
        print("• Controlla i file in data/tracking/")
        print("• Usa 'cat tracking_backup.txt | tail -20'")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'analisi: {e}")

if __name__ == "__main__":
    main()