#include <EPB_DCmotor.h>
#include <EPB_EncoderV2.h>

#include <Servo.h>

//Motor 1 = moteur gauche

EPB_DCmotor motor1(3, 2);
EPB_DCmotor motor2(5, 4);

EPB_Encoder encoder1(12, 6, 1); // définir l'encodeur sur (pinA, pinB, numéro de l'encodeur)
EPB_Encoder encoder2(9, 8, 2);

float maxMotorSpeed = 100; // Monter
float minMotorSpeed = -30;  // Descendre
float timeToAccelerate = 1000; // Le temps d'accélération en milliseconde.
float restSpeed = 10; // Mettre sur 20 quand sur le mur
    
float wantedSpeedMotor1 = restSpeed;
float wantedSpeedMotor2 = restSpeed;

//float K1 = 80;
//float K2 = 80;
//float u01Down = -16;
//float u02Down = -16;
//float u01Up = 70;
//float u02Up = 50;

float K1 = 4000000;
float K2 = 4000000;
float u01Down = 100;
float u02Down = 100;
float u01Up = 100;
float u02Up = 100;
float u01 = 100;
float u02 = 100;

/*float up1multi = 0.9; // OK AVEC BIC
float down1multi = 1 / (1 + 1/3); // PARFAIT

float up2multi = 1; // OK AVEC BIC
float down2multi = 1; //BON AUSSI*/


float up1multi = 1; // OK AVEC BIC
float down1multi = 1; // PARFAIT

float up2multi = 1; // OK AVEC BIC
float down2multi = 1; //BON AUSSI


float E = 0 ; // erreur acceptable/ seuil d'erreur
int maxRepetition = 1000;

long lastPos1 = 0;
long lastPos2 = 0;


bool up = false;


long lastPosition1 = 0;
long lastPosition2 = 0;
  
Servo myservo;

void setup() {
  Serial.begin(74880);
  Serial.setTimeout(1);
  motor1.begin();
  motor2.begin();
  encoder1.begin(1);
  encoder2.begin(2);
  motor1.setSpeed(restSpeed);    
  motor2.setSpeed(-restSpeed);
  myservo.attach(11);
  HandleU();
}

String Serial_get() {
  while (!Serial.available());
  delay(5); 
  String serial_communication = "";
  while (Serial.available() > 0)
  {
    serial_communication += Serial.readString();
  }
  return serial_communication;
}

bool isNumeric(char character)
{
  return (character == '1' ||character == '2' ||character == '3' || character == '4' ||character == '5' || character == '6' ||character == '7' ||character == '8' ||character == '9' ||character == '0'||character == '-');
}

float signOf(float angle)
{
  float sign = 1;
  if (angle < 0)
  {
    sign = -0.5;
  }
  return (sign);
}

float getMaxSpeed(float timeSinceStart)
{
  float toReturn = maxMotorSpeed;
  if (timeSinceStart < timeToAccelerate)
  {
    toReturn = restSpeed + ( maxMotorSpeed - restSpeed )* timeSinceStart / timeToAccelerate;
  }
  return toReturn;
}

float getMinSpeed(float timeSinceStart)
{
  float toReturn = minMotorSpeed;
  if (timeSinceStart < timeToAccelerate)
  {
    toReturn = restSpeed + ( minMotorSpeed - restSpeed )* timeSinceStart / timeToAccelerate;
  }
  return toReturn;
}


float checkSpeed(float tension, float timeSinceStart)
{
  float usedMax = getMaxSpeed(timeSinceStart);
  float usedMin = getMinSpeed(timeSinceStart);
  if (tension > usedMax)
  {
    tension = usedMax;
  }
  else if (tension < usedMin)
  {
    tension = usedMin;
  }
  return tension;
}

int numberSteps(float wantedPosition1, float wantedPosition2)
{
  return max(abs(wantedPosition1), abs(wantedPosition2)) * 0.8;
}
void turn2(float wantedPosition1, float wantedPosition2)
{

  if (wantedPosition1 < 0)
  {
   wantedPosition1 *=  down1multi;
  }

  if (wantedPosition1 > 0)
  {
   wantedPosition1 *=  up1multi;
  }
 

  if (wantedPosition2 < 0)
  {
   wantedPosition2  *=  down2multi;
  }
  if (wantedPosition2 > 0)
  {
   wantedPosition2 *=  up2multi;
  }
  

  
  int steps = numberSteps(wantedPosition1, wantedPosition2);
  int iterSteps = 0;
  float runingPosition1 = 0; // Consigne amovible
  float runingPosition2 = 0;
  float deltaRunPos1 = wantedPosition1 / steps;
  float deltaRunPos2 = wantedPosition2 / steps;
  float error1 = E + 1;
  float error2 = E + 1; 
  
  float startTime = millis();


  
  float u01 = u01Down;
  float u02 = u02Down;

  if (wantedPosition1 >= 0)
  {
    u01 = u01Up;
  }
  

  if (wantedPosition2 >= 0)
  {
    u02 = u02Up;
  }

  while (iterSteps <= steps)
  {
    
    float realPosition1 = (encoder1.read(1) - lastPosition1);
    float realPosition2 = (encoder2.read(2) - lastPosition2);

    
    error1 = runingPosition1 - (realPosition1 * (360.0 / 710.0)); // Calcule l'erreur
    error2 = runingPosition2 - (realPosition2 * (360.0 / 710.0));
    Serial.println(String(error1) + "  " + String(error2));
    float V1 = restSpeed;
    float V2 = restSpeed;
    if (E < abs(error1))
    {
      V1 = K1 * error1 + u01;
    }
    if (E < abs(error2))
    {
      V2 = K2 * error2 + u02;
    }
    if (E >= abs(error1) && E >= abs(error2))
    {
      runingPosition1 = runingPosition1 + deltaRunPos1;
      runingPosition2 = runingPosition2 + deltaRunPos2;
      iterSteps++;
    }
    
    float timeSinceStart = millis() - startTime;
    V1 = checkSpeed(V1, timeSinceStart);
    V2 = checkSpeed(V2, timeSinceStart);
    motor1.setSpeed(V1);
    motor2.setSpeed(-V2);
  }
  motor1.setSpeed(restSpeed);
  motor2.setSpeed(-restSpeed);
  
  lastPosition1 = encoder1.read(1);
  lastPosition2 = encoder2.read(2);
}

// void turn du premier quadri
void turn(float wantedPosition1, float wantedPosition2)
{
  int steps = numberSteps(wantedPosition1, wantedPosition2);
  int iterSteps = 0;
  float runingPosition1 = 0; // Consigne amovible
  float runingPosition2 = 0;
  float deltaRunPos1 = wantedPosition1 / steps;
  float deltaRunPos2 = wantedPosition2 / steps;
  float error1 = E + 1;
  float error2 = E + 1; 
  long lastPosition1 = encoder1.read(1);
  long lastPosition2 = encoder2.read(2);
  
  float startTime = millis();
  
  while (iterSteps <= steps)
  {
    float realPosition1 = encoder1.read(1) - lastPosition1;
    float realPosition2 = encoder2.read(2) - lastPosition2;
    error1 = runingPosition1 - (realPosition1 * (360.0 / 710.0)); // Calcule l'erreur
    error2 = runingPosition2 - (realPosition2 * (360.0 / 710.0));
    float V1 = restSpeed;
    float V2 = restSpeed;
    if (E < abs(error1))
    {
      V1 = K1 * error1 + u01 * signOf(runingPosition1);
    }
    if (E < abs(error2))
    {
      V2 = K2 * error2 + u02* signOf(runingPosition2);
    }
    if (E >= abs(error1) && E >= abs(error2))
    {
      runingPosition1 = runingPosition1 + deltaRunPos1;
      runingPosition2 = runingPosition2 + deltaRunPos2;
      iterSteps++;
    }
    
    float timeSinceStart = millis() - startTime;
    V1 = checkSpeed(V1, timeSinceStart);
    V2 = checkSpeed(V2, timeSinceStart);
    motor1.setSpeed(V1);
    motor2.setSpeed(-V2);
  }
  motor1.setSpeed(restSpeed);
  motor2.setSpeed(-restSpeed);
 /* Serial.println("Finit");
  Serial.println((encoder1.read(1) - lastPosition1) * (360.0 / 710.0) - wantedPosition1);
  delay(1000);
  Serial.println((encoder1.read(1) - lastPosition1) * (360.0 / 710.0) - wantedPosition1);*/
  lastPosition1 = encoder1.read(1);
  lastPosition2 = encoder2.read(2);
  
}

void HandleS(String serial_communication)
{
  String str_delta_angle1 = "";
    String str_delta_angle2 = "";
    
    int i = 1;
    
    while (isNumeric(serial_communication[i]) || serial_communication[i] == '.')
    {
      str_delta_angle1 += serial_communication[i];
      i++;
    }
    i++;    
    while (isNumeric(serial_communication[i]) || serial_communication[i] == '.')
    {
      str_delta_angle2 += serial_communication[i];
      i++;
    }
    float delta_angle1 = str_delta_angle1.toFloat();
    float delta_angle2 = str_delta_angle2.toFloat();   
    turn(delta_angle1, delta_angle2);
    Serial.println("D");
}

void HandleU()
{
  if (!up)
  {
    for  (int i = 1; i <= 100; i += 5){
      myservo.write(i);
      delay(10);
    }
    myservo.write(100);  
    delay(1000);
    up = true;
  }
  Serial.println("D");
}

void HandleD()
{
  if (up)
  {
    for  (int i = 1; i <= 100; i += 5){
      myservo.write(100 - i);
      delay(10);
    }
    myservo.write(0);  
    delay(1000);
    up = false;
  }  
  Serial.println("D");
}

void loop() {
  String serial_communication = Serial_get();
  switch (serial_communication[0])
  {
    case 'T':
    HandleS(serial_communication);
    break;
    case 'U':
    HandleU();
    break;
    case 'D':
    HandleD();
    break;
    default:
    Serial.println(serial_communication);
    break;
    
  }
}
