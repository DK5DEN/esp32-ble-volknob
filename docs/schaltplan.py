"""
Schematic for the ESP32 BLE Volume Knob - ESP32-C3 Super Mini <-> KY-040.
Writes docs/schaltplan.svg and docs/schaltplan.png:  python docs/schaltplan.py

Both files are saved with an opaque white background so they stay readable on
hosts that render them against a dark page, such as GitHub in dark mode.
"""
import schemdraw
import schemdraw.elements as elm

schemdraw.config(font='sans-serif', fontsize=11)

# --- grid -------------------------------------------------------------------
X_ESP_L, X_ESP_R = -5.4, -1.6   # board outline
X_LEAD = 0.4                    # end of the pin leads
X_CAP = 1.8                     # optional capacitors
X_NODE = 4.6                    # signal node inside the module
X_BUS = 9.8                     # module + rail (vertical)

Y_VCC = 4.2                     # 3V3 line
Y_GND = -13.2                   # GND line
Y_TOP, Y_BOT = 5.0, -13.9       # board outline edges

# (module pin, GPIO, contact, C designator, R designator, y)
ROWS = [
    ('CLK', 'GPIO1', 'Channel A',  'C1', 'R1', 0.0),
    ('DT',  'GPIO3', 'Channel B',  'C2', 'R2', -4.4),
    ('SW',  'GPIO4', 'Push-button', 'C3', 'R3', -8.8),
]

with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.0)

    # =====================================================================
    # Title
    # =====================================================================
    d += elm.Label().at((2.5, Y_TOP + 3.0)).label(
        'ESP32 BLE Volume Knob - ESP32-C3 Super Mini ↔ KY-040', fontsize=15)
    d += elm.Label().at((2.5, Y_TOP + 2.2)).label(
        'BLE HID media keyboard · turn = volume, press = mute',
        fontsize=10, color='gray')

    # =====================================================================
    # ESP32-C3 Super Mini outline with pin leads
    # =====================================================================
    for a, b in (((X_ESP_L, Y_TOP), (X_ESP_R, Y_TOP)),
                 ((X_ESP_R, Y_TOP), (X_ESP_R, Y_BOT)),
                 ((X_ESP_R, Y_BOT), (X_ESP_L, Y_BOT)),
                 ((X_ESP_L, Y_BOT), (X_ESP_L, Y_TOP))):
        d += elm.Line().at(a).to(b).color('#333')

    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_TOP - 1.6)).label(
        'ESP32-C3\nSuper Mini', fontsize=12)
    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_TOP - 3.4)).label(
        'CLK/DT/SW set to\nINPUT_PULLUP', fontsize=8.5, color='gray')
    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_BOT + 3.4)).label(
        'leave unused:\nGPIO2 (strapping)\nGPIO8 (LED)\nGPIO9 (BOOT)',
        fontsize=8.5, color='gray')
    d += elm.Label().at(((X_ESP_L + X_ESP_R) / 2, Y_BOT + 1.4)).label(
        'antenna sits at the end\nopposite the USB-C jack -\nkeep it clear',
        fontsize=8.5, color='gray')

    def pin(y, name):
        d.add(elm.Line().at((X_ESP_R, y)).to((X_LEAD, y)))
        d.add(elm.Label().at((X_ESP_R - 0.25, y)).label(name, fontsize=10, halign='right'))

    pin(Y_VCC, '3V3')
    for modpin, gpio, contact, cref, rref, y in ROWS:
        pin(y, gpio)
    pin(Y_GND, 'GND')

    # =====================================================================
    # 3V3: run to the right, decoupling cap, then the vertical + rail
    # =====================================================================
    d += elm.Line().at((X_LEAD, Y_VCC)).to((X_BUS, Y_VCC))
    d += elm.Label().at((X_BUS - 2.4, Y_VCC + 0.45)).label(
        '3V3 - not 5V', fontsize=9.5, color='#a33')

    d += elm.Dot().at((X_CAP, Y_VCC))
    d += elm.Capacitor().down().at((X_CAP, Y_VCC)).length(1.5).label(
        'C4\n100 nF\noptional', loc='bottom', fontsize=8.5, color='gray')
    d += elm.Ground()

    bus_top = d.add(elm.Dot().at((X_BUS, Y_VCC)))
    d += elm.Line().at((X_BUS, Y_VCC)).to((X_BUS, ROWS[-1][5]))
    d += elm.Label().at((X_BUS + 0.35, Y_VCC - 0.55)).label('+', fontsize=12, halign='left')

    # =====================================================================
    # GND: run to the module, reference ground there
    # =====================================================================
    d += elm.Line().at((X_LEAD, Y_GND)).to((X_NODE, Y_GND))
    gnd_mod = d.add(elm.Ground().at((X_NODE, Y_GND)))
    d += elm.Label().at((X_NODE + 0.35, Y_GND + 0.1)).label(
        'GND', fontsize=10, halign='left')

    # =====================================================================
    # The three signal branches
    # =====================================================================
    box = [bus_top, gnd_mod]

    for modpin, gpio, contact, cref, rref, y in ROWS:
        # optional debounce cap on the wire to the module
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

        # module pull-up to + (horizontal, into the rail)
        r = elm.Resistor().right().at((X_NODE, y)).length(2.4).label(
            rref + '\n10 kΩ', fontsize=9)
        d += r
        box.append(r)
        d += elm.Line().to((X_BUS, y))
        box.append(d.add(elm.Dot().at((X_BUS, y))))

        # contact to ground (vertical, downwards)
        sw = elm.Switch().down().at((X_NODE, y)).length(2.0).label(
            contact, loc='bottom', fontsize=9)
        d += sw
        box.append(sw)
        d += elm.Line().down().length(0.7)
        box.append(d.add(elm.Ground()))

    # =====================================================================
    # Module outline
    # =====================================================================
    d += elm.EncircleBox(box, padx=0.9, pady=0.9).linestyle('--').color('#888')
    d += elm.Label().at((X_NODE + 2.0, Y_VCC + 1.6)).label(
        'KY-040 (module board)', fontsize=11.5, color='#555')

    # =====================================================================
    # Notes
    # =====================================================================
    d += elm.Label().at((2.2, Y_GND - 2.4)).label(
        'Every ground symbol inside the frame is the GND pin of the module;\n'
        'the encoder contacts and the push-button switch against it.',
        fontsize=9, color='gray', halign='center')
    d += elm.Label().at((2.2, Y_GND - 4.2)).label(
        'If the + pin is left open, R1 and R2 connect CLK and DT through\n'
        '10 kΩ + 10 kΩ = 20 kΩ. A single contact then pulls both pins low,\n'
        'the quadrature becomes unreadable and no click is ever sent.',
        fontsize=9, color='#a33', halign='center')
    d += elm.Label().at((2.2, Y_GND - 6.4)).label(
        'Fit C1-C3 only if the firmware shows double steps (τ ≈ 100 µs).\n'
        'Not every KY-040 variant has a pull-up on SW, so the firmware sets INPUT_PULLUP.',
        fontsize=9, color='gray', halign='center')

# Opaque white background instead of the transparent default.
d.save('docs/schaltplan.svg', transparent=False)
d.save('docs/schaltplan.png', transparent=False, dpi=150)
print('written: docs/schaltplan.svg + .png')
