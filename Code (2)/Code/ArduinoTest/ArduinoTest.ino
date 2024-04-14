

//Motor 1 = moteur gauche


void setup() {
  Serial.begin(74880);
  Serial.setTimeout(1);
  Serial.println("D");
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



void HandleT(String serial_communication)
{
  Serial.print("22  55");
  Serial.println("D");
}


void HandleU()
{
  Serial.println("D");
}

void HandleD()
{
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
