#include <EPB_DCmotor.h>
#include <EPB_EncoderV2.h>

#include <Servo.h>

//Motor 1 = moteur gauche

EPB_DCmotor motor1(3, 2);
EPB_DCmotor motor2(5, 4);

EPB_Encoder encoder1(6, 12, 1); // définir l'encodeur sur (pinA, pinB, numéro de l'encodeur)
EPB_Encoder encoder2(8, 9, 2);


float timeToAccelerate = 1000; // Le temps d'accélération en milliseconde.
float restSpeed = 10; // Mettre sur 20 quand sur le mur


float wantedSpeedMotor1 = restSpeed;
float wantedSpeedMotor2 = restSpeed;

float K1 = 0.29;
float K2 = 0.29;


float E = 4; // erreur acceptable/ seuil d'erreur
int maxRepetition = 1000;

long lastPos1 = 0;
long lastPos2 = 0;


bool up = true;


long lastPosition1 = 0;
long lastPosition2 = 0;

float lastError1 = 0;
float lastError2 = 0;

int i = 1; //Used by multiple fcts to read Serial com
  
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



float getMaxSpeed(float voltage)
{
  float toReturn = voltage;
  if (toReturn > 185)
  {
    toReturn = 185;
  }
  return toReturn;
}

float getMinSpeed(float voltage)
{
  float toReturn = voltage;

   if (toReturn < -75)
  {
    toReturn = -75;
  }
  return toReturn;
}

/*
int signOf(float angle)
{
    int toReturn = -1;
    if (angle > 0)
    {
      toReturn = 1;
      }
      return toReturn;
}*/
void turn(float wantedPosition1, float wantedPosition2, float u1, float u2)
{ 
 
  wantedPosition1 += lastError1;
  
  wantedPosition2 += lastError2;
    
    
  
  float error1 = E + 1;
  float error2 = E + 1; 

  
  float timeAtStart = millis();
  
  while ((abs(error1)> E or abs(error2)> E) &&  millis() - timeAtStart < 4000)
  {
    float V1 = restSpeed;
    float V2 = restSpeed;
    if (abs(error1)>E){
      float realPosition1 = (encoder1.read(1) - lastPosition1); // Position de l'encodeur se reset a chaque itération
      error1 = wantedPosition1 - (realPosition1 * (360.0 / 710.0)); // Calcule l'erreur
      V1 = getMaxSpeed(getMinSpeed(K1 * error1 + getUFromError(error1)));
    }
    if (abs(error2)>E){
      float realPosition2 = (encoder2.read(2) - lastPosition2); 
      error2 = wantedPosition2 - (realPosition2 * (360.0 / 710.0));
      V2 = getMaxSpeed(getMinSpeed(K2 * error2 + getUFromError(error2)));
    }    

    motor1.setSpeed(V1);
    motor2.setSpeed(-V2);
  }
  
  float realPosition1 = (encoder1.read(1) - lastPosition1); // Position de l'encodeur se reset a chaque itération
  error1 = wantedPosition1 - (realPosition1 * (360.0 / 710.0)); // Calcule l'erreur

  float realPosition2 = (encoder2.read(2) - lastPosition2); 
  error2 = wantedPosition2 - (realPosition2 * (360.0 / 710.0));
 

  lastError2 = error2;
  lastError1 = error1;
    
  lastPosition1 = encoder1.read(1);
  lastPosition2 = encoder2.read(2);
}
float getUFromError(float error)
{
  
  float toReturn= -35;
  
  if (error > 0)
  {
    toReturn = 80;
  }
  
  return toReturn;
}
String GetNumberFromCommunication(String serial_communication)
{
  String toReturn = "";
  while (isNumeric(serial_communication[i]) || serial_communication[i] == '.')
    {
      toReturn += serial_communication[i];
      i++;
    }
   return toReturn;
}

void HandleT(String serial_communication)
{
    i = 1;
    float delta_angle1 = GetNumberFromCommunication(serial_communication).toFloat();
    i++;
    float delta_angle2 = GetNumberFromCommunication(serial_communication).toFloat();
    i++;
    float u1 = GetNumberFromCommunication(serial_communication).toFloat();
    i++;
    float u2 = GetNumberFromCommunication(serial_communication).toFloat();
    int numOfSteps = round(max(abs(delta_angle1), abs(delta_angle2)) / 20);
   numOfSteps = max(1, numOfSteps);
     float angleToPrint = 0;
     float toDdelte = 0;
    for (int i = 0; i < numOfSteps; i++)
    {
      angleToPrint += delta_angle1 / numOfSteps;
      toDdelte = lastPosition1;
      turn(delta_angle1 / numOfSteps, delta_angle2 / numOfSteps, u1, u2);
    }
    
    motor1.setSpeed(restSpeed);
    motor2.setSpeed(-restSpeed);
    Serial.println("D");
}


void HandleU()
{
  if (!up)
  {
    for  (int i = 1; i <= 50; i += 2){
      myservo.write(i);
      delay(20);
    }
    myservo.write(50);  
    delay(1000);
    up = true;
  }
  Serial.println("D");
}


void HandleD()
{
  if (up)
  {
    for  (int i = 1; i <= 50; i += 2){
      myservo.write(50 - i);
      delay(20);
    }
    myservo.write(0);  
    delay(350);
    up = false;
  }  
  Serial.println("D");
}

void loop() {
  String serial_communication = Serial_get();
  switch (serial_communication[0])
  {
    case 'T':
    HandleT(serial_communication);
    break;
    case 'U':
    //Serial.println("D");
    HandleU();
    break;
    case 'D':
    //Serial.println("D");
    HandleD();
    break;
    default:
    Serial.println(serial_communication);
    break;
    
  }
}
