// Local
#include "led_handler.h"
#include "PinUtils.h"

LedHandler::LedHandler() {}

void LedHandler::init() {
  pin_ = LED_BUILTIN; 
  pinMode(pin_, OUTPUT);
  digitalWrite(pin_, false);

  // Provide a visible signal that setup has been entered.
  if (Serial) {
    // 2 seconds of fast blinks.
    for (int i = 0; i < 40; ++i) {
      delay(50);
      toggle_led();
    }
    Serial.println("LED blink complete");
  } else {
    // 2 seconds of slow blinks.
    for (int i = 0; i < 10; ++i) {
      delay(200);
      toggle_led();
    }
  }
}

void LedHandler::update() {
  unsigned long now = millis();
  if (next_change_ms_ <= now) {
    toggle_led();
    next_change_ms_ += (Serial ? 1000 : 100);
    if (next_change_ms_ <= now) {
      next_change_ms_ = now;
    }
  }
}

void LedHandler::setValue(int value) {
  if (value == 0) {
    turn_pin_off(pin_);
  } else {
    turn_pin_on(pin_);
  }
}
