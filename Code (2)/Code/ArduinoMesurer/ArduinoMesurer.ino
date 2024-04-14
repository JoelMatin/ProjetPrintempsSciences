#include <EPB_Encoder.h>
#include <EPB_DCmotor.h>


#define DIR_PIN 2
#define PWM_PIN 3

#define ENC_CHA 12
#define ENC_CHB 6

#define INACTIVE  0
#define ACTIVE    1
float timer = -100;


EPB_DCmotor motor(PWM_PIN, DIR_PIN);

EPB_encoder encoder(ENC_CHA, ENC_CHB);
int state;
long newPosition, oldPosition;
char c;
long nextTime;

int startPos = 0;
void setup() {
  Serial.begin(9600);
  motor.begin();
  encoder.begin();
  state = INACTIVE;
  oldPosition = 0;
}


void loop() {


  if (Serial.available()) {
    c = Serial.read();
    if (c == 'B') {         // BEGIN command
      motor.setSpeed(50);
      nextTime = millis();
      timer = millis();
      startPos = encoder.read();
      state = ACTIVE;
    }
    else if (c == 'E') {    // END command
      motor.setSpeed(0);
      state = INACTIVE;
    }
  }

  if (state == ACTIVE) {
    if (millis() >= nextTime) {
      nextTime = nextTime + 10;
      newPosition = encoder.read();
      Serial.print(millis() - timer);
      Serial.print("   ");
      Serial.println(newPosition - startPos);
      if (abs(newPosition - startPos) > 710)
       {
        motor.setSpeed(0);
      state = INACTIVE;
        }
    }
  }
}
