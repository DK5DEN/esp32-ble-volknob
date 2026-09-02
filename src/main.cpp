#include <Arduino.h>
#include <BleKeyboard.h>

#define PIN_CLK 1          // Drahtbrücke, Steckbrett-Prototyp: 0
#define PIN_DT  3          // Steckbrett-Prototyp: 1
#define PIN_SW  4          // Steckbrett-Prototyp: 3

#define DETENT_STEPS 4      // KY-040: 4 quadrature steps per click
#define BTN_DEBOUNCE 50     // ms

BleKeyboard bleKeyboard("VolKnob", "DIY", 100);

volatile int8_t  encDelta = 0;
volatile uint8_t encState = 0;

// quadrature state machine lookup
const int8_t encTable[16] = { 0,-1, 1, 0,
                              1, 0, 0,-1,
                             -1, 0, 0, 1,
                              0, 1,-1, 0 };

void IRAM_ATTR encISR() {
  encState = ((encState << 2) |
              (digitalRead(PIN_CLK) << 1) |
               digitalRead(PIN_DT)) & 0x0F;
  encDelta += encTable[encState];
}

void setup() {
  pinMode(PIN_CLK, INPUT_PULLUP);
  pinMode(PIN_DT,  INPUT_PULLUP);
  pinMode(PIN_SW,  INPUT_PULLUP);

  // Startzustand aus den echten Pegeln uebernehmen. Ohne das startet encState
  // auf 00, waehrend die Pins in Ruhe auf 11 liegen -- die erste Flanke faellt
  // dann auf Tabellenindex 3 (= 0) und ein Quadraturschritt geht verloren.
  encState = (digitalRead(PIN_CLK) << 1) | digitalRead(PIN_DT);

  attachInterrupt(PIN_CLK, encISR, CHANGE);
  attachInterrupt(PIN_DT,  encISR, CHANGE);

  bleKeyboard.begin();
}

void loop() {
  if (!bleKeyboard.isConnected()) { delay(100); return; }

  // --- rotation ---
  noInterrupts();
  int8_t d = encDelta;
  if (d >= DETENT_STEPS || d <= -DETENT_STEPS) {
    encDelta -= (d / DETENT_STEPS) * DETENT_STEPS;
  } else {
    d = 0;
  }
  interrupts();

  int clicks = d / DETENT_STEPS;
  while (clicks > 0)  { bleKeyboard.write(KEY_MEDIA_VOLUME_UP);   clicks--; delay(15); }
  while (clicks < 0)  { bleKeyboard.write(KEY_MEDIA_VOLUME_DOWN); clicks++; delay(15); }

  // --- button ---
  static bool     lastState = HIGH;
  static uint32_t lastEdge  = 0;
  bool now = digitalRead(PIN_SW);

  if (now != lastState && millis() - lastEdge > BTN_DEBOUNCE) {
    lastEdge  = millis();
    lastState = now;
    if (now == LOW) bleKeyboard.write(KEY_MEDIA_MUTE);
  }

  delay(2);
}
