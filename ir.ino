#include <IRremote.h>

// Define pin numbers
const int buttonPin = 2;    // Pin for the button
const int buzzerPin = 3;    // Pin for the buzzer
const int ledPin = 4;       // Pin for the LED
const int irReceiverPin = 5; // Pin for the IR receiver
bool sleep = 0;
// Define IR remote codes
#define IR_BUTTON_CODE 0xFFA25D

// Initialize the IR receiver
IRrecv irrecv(irReceiverPin);
decode_results results;

// Function to initialize hardware
void setup() {
  pinMode(buttonPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  irrecv.enableIRIn();  // Start the IR receiver
}

// Function to handle the button press
void handleButtonPress() {
  if(sleep == 0) {
    tone(buzzerPin, 1000);  // Activate the buzzer
    digitalWrite(ledPin, HIGH);  // Turn on the LED
  }
  else {
  noTone(buzzerPin);  // Turn off the buzzer
  digitalWrite(ledPin, LOW);  // Turn off the LED
  }
}

// Main loop
void loop() {
  if (digitalRead(buttonPin) == LOW && sleep == 0) {
    handleButtonPress();
  }
  else {noTone(buzzerPin);  // Turn off the buzzer
    digitalWrite(ledPin, LOW);  // Turn off the LED
    }
  if(sleep == 1) {
    noTone(buzzerPin);  // Turn off the buzzer
    digitalWrite(ledPin, LOW);  // Turn off the LED
  }


  // Check for IR remote signals
  if (irrecv.decode(&results)) {
   // if (results.value == IR_BUTTON_CODE) {
      // Turn off buzzer and LED
      sleep = !sleep;
      //noTone(buzzerPin);
      //digitalWrite(ledPin, LOW);
  //  }
    irrecv.resume();  // Receive the next value
  }
}
