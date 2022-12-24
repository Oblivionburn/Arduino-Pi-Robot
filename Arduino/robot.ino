#include <SoftwareSerial.h>
#include <Servo.h>

//Not every servo has the same min/max pulse width, so check specs on it
int pulseMin = 500;
int pulseMax = 2500;

//If your servo only goes to 180, then set max to 180
int angleMin = 0;
int angleMax = 360;

//Init globals
byte dataIndex = 0;
const byte dataLimit = 64;
char receivedData[dataLimit];

boolean newData = false;
boolean receiving = false;

String command = "";
String commandData = "";

//Init servo array
Servo Servo0;
Servo Servo1;
Servo Servo2;
Servo Servo3;
Servo Servo4;
Servo Servo5;
Servo Servo6;
Servo Servo7;
Servo Servo8;
Servo Servo9;
Servo Servo10;
Servo Servo11;
Servo Servo12;
Servo Servo13;
Servo Servo14;
Servo Servo15;

Servo Servos[] = 
{
  Servo0,
  Servo1,
  Servo2,
  Servo3,
  Servo4,
  Servo5,
  Servo6,
  Servo7,
  Servo8,
  Servo9,
  Servo10,
  Servo11,
  Servo12,
  Servo13,
  Servo14,
  Servo15
};

//Init method that runs automatically when Arduino is powered on
void setup() 
{
  for (byte i = 0; i <= 15; i++)
  {
    //Adding 2 to start with pin D2 and end with D18 for a total of 16 servos
    Servos[i].attach(i + 2, pulseMin, pulseMax);

    //Default to starting position 0
    Servos[i].writeMicroseconds(map(0, angleMin, angleMax, pulseMin, pulseMax));
  }

  Serial.begin(9600);
  Send("Ready");
}

//Loop that Arduino will run in once setup() has finished
void loop()
{
  Receive();
  Acknowledge();
  ParseCommand();
  Finish();
}

void Receive()
{
  //Check this character for new data transmission
  char startMarker = '<';

  //Check this character for data transmission is finished
  char endMarker = '>';

  /*
    Note: pulling data out of the Serial buffer will outpace the
      device sending the data, so we'll need to resume where we
      left off when loop() comes back around to this. We'll stitch
      the chunks of data together in the receivedData buffer.
  */
  while (Serial.available() > 0 &&
         !newData)
  {
    //Pull and remove next character from Serial buffer
    char c = Serial.read();

    if (c == '?')
    {
      //Test connection
      Send("Connected");
    }
    else if (receiving)
    {
      if (c != endMarker)
      {
        //Write data to buffer
        receivedData[dataIndex] = c;
        dataIndex++;
  
        if (dataIndex >= dataLimit)
        {
          //Prevent overflowing the buffer
          dataIndex = dataLimit - 1;
        }
      }
      else 
      {
        //We've reached the end of the transmission
        
        //Terminate with null for converting receivedData to a String object
        receivedData[dataIndex] = '\0';
  
        //Reset for next transmission
        receiving = false;
        dataIndex = 0;
  
        //Let the rest of Loop() know we finished
        newData = true;
      }
    }
    else if (c == startMarker)
    {
      //We've started receiving a new transmission
      receiving = true;
    }
  }
}

void Acknowledge()
{
  //Don't do anything if we're still receiving a transmission
  if (newData)
  {
    //Let other device know we received the data
    Send(receivedData);
  }
}

void ParseCommand()
{
  //Don't do anything if we're still receiving a transmission
  if (newData)
  {
    //Turn char buffer into whole String object so we can use String functions on it
    String received = receivedData;

    //Check for this character to separate command from data, Example: "<rotate:motor00;180>"
    int index = received.indexOf(":");

    //If we received "<rotate:motor00;180>", get just the "rotate" command
    //Note: starting/ending < and > chars will not be in the receivedData
    command = received.substring(0, index);

    //If we received "<rotate:motor00;180>", get just the "motor00;180" data
    commandData = received.substring(index + 1, received.length());

    if (command == "rotate")
    {
      RotateMotor();
    }
  }
}

void RotateMotor()
{
  //Check for this character to separate data parts, Example: "motor00;180"
  int index = commandData.indexOf(";");

  //If we received "motor00;180", get just the "00" as int 0 for Servos[] index
  String motorStr = commandData.substring(index - 2, index);
  int motor = motorStr.toInt();

  //If we received "motor00;180", get just the 180 angle for rotation
  String motorAngleStr = commandData.substring(index + 1, commandData.length());
  int motorAngle = motorAngleStr.toInt();

  //Convert angle to pulses in microseconds
  int nextPulse = map(motorAngle, angleMin, angleMax, pulseMin, pulseMax);

  //Rotate the requested motor to requested angle
  Servos[motor].writeMicroseconds(nextPulse);
}

void Finish()
{
  //Don't do anything if we're still receiving a transmission
  if (newData)
  {
    //Let other device know we finished
    Send("Finished");

    /*
      Clear our data buffer, in case next transmission is smaller size
      Example:
        Transmission 1: "<rotate:motor00;180>"
        Transmission 2: "<rotate:motor00;2>"
      Without clearing, string for transmission 2 would be "<rotate:motor00;2>0>"
        due to leftover chars from transmission 1 in the rest of the array.
      We can use memset to replace all elements in the array with null.
    */
    memset(receivedData, '\0', sizeof(receivedData));

    //We can start receiving data again now on Serial channel
    newData = false;
  }
}

void Send(String data)
{
  if (data != "")
  {
    Serial.print("Arduino: ");
    Serial.println(data);

    //Block execution until we finished sending Serial data
    //Serial.flush();
  }
}
