"""
Schaltplan ESP32 BLE Volume Knob — ESP32-C3 Super Mini <-> KY-040
Erzeugt docs/schaltplan.svg + .png:  python docs/schaltplan.py
"""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(font='sans-serif', fontsize=11)

# --- Raster -----------------------------------------------------------------
X_ESP_L, X_ESP_R = -5.4, -1.6   # Gehaeuse des Boards
X_LEAD = 0.4                    # Ende der Pin-Leitungen
X_CAP = 1.8                     # optionale Kondensatoren
X_NODE = 4.6                    # Signalknoten im Modul
X_BUS = 9.8                     # +-Schiene des Moduls (senkrecht)

Y_VCC = 4.2                     # 3V3-Leitung
Y_GND = -13.2                   # GND-Leitung
Y_TOP, Y_BOT = 5.0, -13.9       # Gehaeusekanten

# (Modulpin, GPIO, Kontakt, C-Bezeichner, R-Bezeichner, y)
ROWS = [
    ('CLK', 'GPIO1', 'Kanal A', 'C1', 'R1', 0.0),
    ('DT',  'GPIO3', 'Kanal B', 'C2', 'R2', -4.4),
    ('SW',  'GPIO4', 'Taster',  'C3', 'R3', -8.8),
]

with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.0)

    # =====================================================================
    # Titel
    # =====================================================================
    d += elm.Label().at((2.5, Y_TOP + 3.0)).label(
        'ESP32 BLE Volume Knob — ESP32-C3 Super Mini ↔ KY-040', fontsize=15)
    d += elm.Label().at((2.5, Y_TOP + 2.2)).label(
        'BLE-HID-Media-Tastatur · Drehen = Lautstärke, Drücken = Mute',
        fontsize=10, color='gray')

    # =====================================================================
    # ESP32-C3 Super Mini als Gehaeuse mit Pin-Leitungen
    # =====================================================================
    for a, b in (((X_ESP_L, Y_TOP), (X_ESP_R, Y_TOP)),
                 ((X_ESP_R, Y_TOP), (X_ESP_R, Y_BOT)),
                 ((X_ESP_R, Y_BOT), (X_ESP_L, Y_BOT)),
                 ((X_ESP_L, Y_BOT), (X_ESP_L, Y_TOP))):
        d += elm.Line().at(a).to(b).color('#333')

    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_TOP - 1.6)).label(
        'ESP32-C3\nSuper Mini', fontsize=12)
    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_TOP - 3.4)).label(
        'CLK/DT/SW als\nINPUT_PULLUP', fontsize=8.5, color='gray')
    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_BOT + 2.6)).label(
        'frei lassen:\nGPIO2 (Strapping)\nGPIO8 (LED)\nGPIO9 (BOOT)',
        fontsize=8.5, color='gray')

    def pin(y, name):
        d.add(elm.Line().at((X_ESP_R, y)).to((X_LEAD, y)))
        d.add(elm.Label().at((X_ESP_R - 0.25, y)).label(name, fontsize=10, halign='right'))

    pin(Y_VCC, '3V3')
    for modpin, gpio, kontakt, cref, rref, y in ROWS:
        pin(y, gpio)
    pin(Y_GND, 'GND')

    # =====================================================================
    # 3V3: Leitung nach rechts, Abblock-C, dann senkrechte +-Schiene
    # =====================================================================
    d += elm.Line().at((X_LEAD, Y_VCC)).to((X_BUS, Y_VCC))
    d += elm.Label().at((X_BUS - 2.4, Y_VCC + 0.45)).label(
        '3V3 — nicht 5V!', fontsize=9.5, color='#a33')

    d += elm.Dot().at((X_CAP, Y_VCC))
    d += elm.Capacitor().down().at((X_CAP, Y_VCC)).length(1.5).label(
        'C4\n100 nF\noptional', loc='bottom', fontsize=8.5, color='gray')
    d += elm.Ground()

    bus_top = d.add(elm.Dot().at((X_BUS, Y_VCC)))
    d += elm.Line().at((X_BUS, Y_VCC)).to((X_BUS, ROWS[-1][5]))
    d += elm.Label().at((X_BUS + 0.35, Y_VCC - 0.55)).label('+', fontsize=12, halign='left')

    # =====================================================================
    # GND: Leitung zum Modul, dort Bezugsmasse
    # =====================================================================
    d += elm.Line().at((X_LEAD, Y_GND)).to((X_NODE, Y_GND))
    gnd_mod = d.add(elm.Ground().at((X_NODE, Y_GND)))
    d += elm.Label().at((X_NODE + 0.35, Y_GND + 0.1)).label(
        'GND', fontsize=10, halign='left')

    # =====================================================================
    # Die drei Signalzweige
    # =====================================================================
    box = [bus_top, gnd_mod]

    for modpin, gpio, kontakt, cref, rref, y in ROWS:
        # optionaler Entprell-C auf der Leitung zum Modul
        d += elm.Line().at((X_LEAD, y)).to((X_CAP, y))
        cnode = d.add(elm.Dot().at((X_CAP, y)))
        d += elm.Capacitor().down().at((X_CAP, y)).length(1.5).label(
            cref + '\n10 nF\noptional', loc='bottom', fontsize=8.5, color='gray')
        d += elm.Ground()
        d += elm.Line().at(cnode.center).to((X_NODE, y))

        node = d.add(elm.Dot().at((X_NODE, y)))
        box.append(node)
        d += elm.Label().at((X_NODE - 0.15, y + 0.4)).label(
            modpin, fontsize=10, halign='right')

        # Modul-Pullup nach + (waagerecht zur Schiene)
        r = elm.Resistor().right().at((X_NODE, y)).length(2.4).label(
            rref + '\n10 kΩ', fontsize=9)
        d += r
        box.append(r)
        d += elm.Line().to((X_BUS, y))
        box.append(d.add(elm.Dot().at((X_BUS, y))))

        # Kontakt gegen Masse (senkrecht nach unten)
        sw = elm.Switch().down().at((X_NODE, y)).length(2.0).label(
            kontakt, loc='bottom', fontsize=9)
        d += sw
        box.append(sw)
        d += elm.Line().down().length(0.7)
        box.append(d.add(elm.Ground()))

    # =====================================================================
    # Modulrahmen
    # =====================================================================
    d += elm.EncircleBox(box, padx=0.9, pady=0.9).linestyle('--').color('#888')
    d += elm.Label().at((X_NODE + 2.0, Y_VCC + 1.6)).label(
        'KY-040 (Modulplatine)', fontsize=11.5, color='#555')

    # =====================================================================
    # Fussnoten
    # =====================================================================
    d += elm.Label().at((2.2, Y_GND - 2.4)).label(
        'Alle Massezeichen innerhalb des Rahmens sind der GND-Pin des Moduls;\n'
        'Encoder-Kontakte und Taster schalten gegen diese Masse.',
        fontsize=9, color='gray', halign='center')
    d += elm.Label().at((2.2, Y_GND - 4.2)).label(
        'Bleibt der +-Pin offen, koppeln R1 und R2 die Pins CLK und DT über\n'
        '10 kΩ + 10 kΩ = 20 kΩ zusammen. Ein Kontakt zieht dann beide Pins nach\n'
        'unten, die Quadratur wird unlesbar und es wird nie ein Click gesendet.',
        fontsize=9, color='#a33', halign='center')
    d += elm.Label().at((2.2, Y_GND - 6.4)).label(
        'C1–C3 erst bestücken, wenn die Firmware Doppelsprünge zeigt (τ ≈ 100 µs).\n'
        'Nicht jede KY-040-Variante hat einen Pullup auf SW — Firmware setzt INPUT_PULLUP.',
        fontsize=9, color='gray', halign='center')

d.save('docs/schaltplan.svg')
d.save('docs/schaltplan.png', dpi=150)
print('geschrieben: docs/schaltplan.svg + .png')
