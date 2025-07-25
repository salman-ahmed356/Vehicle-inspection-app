#!/usr/bin/env python3
NAME_MAP = {
    'Şaşi No Kontrol':                     'Chassis Number Check',
    'İç Aydınlatma':                       'Interior Lighting',
    'Dikiz Aynası':                        'Rearview Mirror',
    'Emniyet Kemerleri Kontrol':           'Seat Belt Check',
    'Güneşlikler Kontrol':                 'Sun Visor Check',
    'Torpito Kontrol':                     'Glove Compartment Check',
    'Direksiyon Kontrol':                  'Steering Check',
    'Koltuklar Kontrol':                   'Seat Check',
    'Tavan Döşeme Kontrol':                'Headliner Check',
    'Araç İçi Döşeme Kontrol':             'Interior Upholstery Check',
    'Cam Kumandası Kontrol':               'Window Control Check',
    'Klima Kontrol':                       'Air Conditioning Check',
    'Gösterge Paneli Kontrol':             'Instrument Panel Check',
    'Radyo, Teyp, Navigasyon Kontrol':     'Radio/Tape/Navigation Check',
    'Korna':                               'Horn',
    'Ön Farlar':                           'Front Headlights',
    'Far Yıkama':                          'Headlight Washer',
    'Ön - Arka Sisler':                    'Front & Rear Fog Lights',
    'Sinyaller ve Dörtlü İkaz':            'Turn Signals & Hazard Lights',
    'Silecekler':                          'Wipers',
    'Aynalar':                             'Mirrors',
    'Sunroof veya Cam Tavan':              'Sunroof or Glass Roof',
    'Camlar':                              'Windows',
    'Kapı Kolları':                        'Door Handles',
    'Arka Stoplar':                        'Rear Taillights',
    'Plaka Aydınlatma':                    'License Plate Lighting',
    'Bagaj İçi':                           'Trunk Interior',
    'Stepne':                              'Spare Tire',
    'Motor gücü':                          'Engine Power',
    'Beygir gücü':                         'Horsepower',
    'Performans':                          'Performance',
    'Sol Ön Çamurluk':                     'Left Front Fender',
    'Sol Ön Kapı':                         'Left Front Door',
    'Sol Arka Çamurluk':                   'Left Rear Fender',
    'Ön Tampon':                           'Front Bumper',
    'Kaput':                               'Hood',
    'Tavan':                               'Roof',
    'Bagaj Kapağı':                        'Trunk Lid',
    'Arka Tampon':                         'Rear Bumper',
    'Sağ Ön Çamurluk':                     'Right Front Fender',
    'Sağ Ön Kapı':                         'Right Front Door',
    'Sağ Arka Kapı':                       'Right Rear Door',
    'Sağ Arka Çamurluk':                   'Right Rear Fender',
    'Sol Arka Kapı':                       'Left Rear Door',
    'Sol Ön Şase':                         'Left Front Chassis',
    'Sol İç Podye':                        'Left Inner Wheel Arch',
    'Sol İç Direk':                        'Left Inner Pillar',
    'Sol Üst Direk':                       'Left Upper Pillar',
    'Sol Marşpiyel':                       'Left Sill',
    'Sol Arka Şase':                       'Left Rear Chassis',
    'Ön Panel':                            'Front Panel',
    'Ön Cam':                              'Front Windshield',
    'Arka Cam':                            'Rear Window',
    'Arka Panel':                          'Rear Panel',
    'Arka Havuz İçi':                      'Rear Wheel Well Interior',
    'Sağ Ön Şase':                         'Right Front Chassis',
    'Sağ İç Podye':                        'Right Inner Wheel Arch',
    'Sağ İç Direk':                        'Right Inner Pillar',
    'Sağ Üst Direk':                       'Right Upper Pillar',
    'Sağ Marşpiyel':                       'Right Sill',
    'Sağ Arka Şase':                       'Right Rear Chassis',
    'Motor Koruyucu Kapağı':               'Engine Protective Cover',
    'Hava Filtre Kabini':                  'Air Filter Housing',
    'Motor Elektrik Tesisatı':             'Engine Electrical System',
    'Motor Yağı ve Sızdırmazlık':          'Engine Oil & Sealing',
    'Motor Yağ Seviyesi':                  'Engine Oil Level',
    'Yağ Soğutucusu':                      'Oil Cooler',
    'Motor Isı ve Ses İzolasyon':          'Engine Heat & Sound Insulation',
    'Turbo İntercooler Kontrolü':          'Turbo Intercooler Check',
    'Egr Valfi ve Enjektör Kontrolü':       'EGR Valve & Injector Check',
    'Görünen Tüm Kayışlar':                'All Visible Belts',
    'Motor Su Sızdırmazlık':               'Engine Water Tightness',
    'Yakıt Sistemi ve Sızdırmazlık':       'Fuel System & Sealing',
    'Direksiyon Pompa Kontrolü':           'Steering Pump Check',
    'Soğutma Fanları':                     'Cooling Fans',
    'Motor Su Radyatörü ve Paneli':        'Engine Radiator & Core',
    'Klima Radyatörü ve Boruları':         'A/C Radiator & Pipes',
    'Motor Üfleme':                        'Engine Blow-by',
    'Fren Hidroliği':                      'Brake Fluid',
    'Motor Vuruntulu/Düzensiz Çalışma':    'Engine Knocking/Irregular Operation',
    'Turbo Genel Kontrolü':                'Turbo General Inspection',
    'Akü':                                 'Battery',
    'Sol Ön':                              'Front Left',
    'Sol Arka':                            'Rear Left',
    'SOL ÖN':                              'Front Left',
    'SAĞ ÖN':                              'Front Right',
    'SOL ARKA':                            'Rear Left',
    'SAĞ ARKA':                            'Rear Right',
    'ÖN SOL FREN':                         'Front Left Brake',
    'ÖN SAĞ FREN':                         'Front Right Brake',
    'ARKA SOL FREN':                       'Rear Left Brake',
    'ARKA SAĞ FREN':                       'Rear Right Brake',
    'EL FRENI SOL':                        'Parking Brake Left',
    'EL FRENI SAĞ':                        'Parking Brake Right',
    'Hava Yastığı Elektroniğinde':         'Airbag Electronics',
    'Motor Arıza Lambası':                 'Engine Warning Light',
    'ABS / ESP / ESR Elektroniği':         'ABS/ESP/ESR Electronics',
    'Klima Elektroniği':                   'A/C Electronics',
    'Lastik Basınç Elektroniği':           'Tire Pressure Electronics',
    'Elektirikli Direksiyon':              'Electric Steering',
    'Motor Beyin Elektroniği':             'Engine Control Unit Electronics',
    'Şanzıman Elektroniği':                'Transmission Electronics',
    'Yay ve Amörtisör (Sağ Ön)':           'Spring & Shock Absorber (Front Right)',
    'Yay ve Amörtisör (Sol Ön)':           'Spring & Shock Absorber (Front Left)',
    'Yay ve Amörtisör (Sağ Arka)':         'Spring & Shock Absorber (Rear Right)',
    'Yay ve Amörtisör (Sol Arka)':         'Spring & Shock Absorber (Rear Left)',
    'Fren Disk Durumu (Sağ Ön)':           'Brake Disc Condition (Front Right)',
    'Fren Disk Durumu (Sol Ön)':           'Brake Disc Condition (Front Left)',
    'Fren Disk Durumu (Sağ Arka)':         'Brake Disc Condition (Rear Right)',
    'Fren Disk Durumu (Sol Arka)':         'Brake Disc Condition (Rear Left)',
    'Fren Balatası (Sağ Ön)':              'Brake Pad (Front Right)',
    'Fren Balatası (Sol Ön)':              'Brake Pad (Front Left)',
    'Fren Balatası (Sağ Arka)':            'Brake Pad (Rear Right)',
    'Fren Balatası (Sol Arka)':            'Brake Pad (Rear Left)',
    'Rot Kolları ve Rot Başları':          'Tie Rods & Ball Joints',
    'Salıncak Burç Rotilleri':             'Control Arm Bushing & Link Rods',
    'Aks ve Aks Körükleri':                'Axle & Axle Boots',
    'Jant ve Lastik (Sağ Ön)':             'Wheel & Tire (Front Right)',
    'Jant ve Lastik (Sol Ön)':             'Wheel & Tire (Front Left)',
    'Jant ve Lastik (Sağ Arka)':           'Wheel & Tire (Rear Right)',
    'Jant ve Lastik (Sol Arka)':           'Wheel & Tire (Rear Left)',
    'Davlumbazların Kontrolü':             'Underbody Shield Check',
    'Motor ve Şanzıman Alt Takozlar':       'Engine & Transmission Mounts',
    'Motor Yağ Sızdırmazlık':              'Engine Oil Sealing',
    'Şanzıman Yağ Sızdırmazlık':           'Transmission Oil Sealing',
    'Diferansiyel Yağ Sızdırmazlık':        'Differential Oil Sealing',
    'Direksiyon Kutusu Yağ Sızdırmazlık':  'Steering Gearbox Oil Sealing',
    'Klima Kompresörü Yağ Sızdırmazlık':   'A/C Compressor Oil Sealing',
    'Debriyaj Kontrol':                    'Clutch Check',
    'Egzoz Bölge Siyah Duman':             'Exhaust Area Black Smoke',
    'Egzoz Bölge Mavi Duman':              'Exhaust Area Blue Smoke',
    'Katalizör Sistemi':                   'Catalytic Converter System',
    'Elektrikli Direksiyon':               'Electric Power Steering',
}

for turkish, english in NAME_MAP.items():
    # escape any single‐quotes in your English text
    e = english.replace("'", "''")
    t = turkish.replace("'", "''")
    print(f"UPDATE expertise_features SET name = '{e}' WHERE name = '{t}';")
