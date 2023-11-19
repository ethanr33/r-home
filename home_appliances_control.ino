#include <dht.h>
#include <Servo.h>


Servo garage_servo;
Servo lock_servo;

dht DHT;

#define led1 2
#define temp_sensor 5
#define but1 4
#define echoPin 53 
#define trigPin 52
#define button1 7
#define garage_pin 3
#define lock_pin 8
#define button2 9
#define warm 50
#define cool 44

bool temp_asked = false;
bool temp_read = false;
bool led_on = false;
int distance;
long duration;
int buttonPushed1 = 0;
int buttonPushed2 = 0;
bool lock_open = false;
String str;
int light_int;
int lock_distance_int;
int garage_int;
int lock_int;
int temp_int;
int actual_temperature;
int sensor;
int wanted_temp;

int email_int;
/////////////////////////// email //////////////////////////////////
void email()
{
  
 if(email_int == 1)
 {
   
   String email_str = "The current temperature is: " + String(actual_temperature) + " degrees and the desired temperature is: " + String(wanted_temp) + ". ";
   if(led_on)
   {
     email_str = email_str  + "The light is on. ";
   }
   else if(!led_on)
   {
     email_str = email_str  + "The light is off. ";
   }


   if(lock_open)
   {
     email_str = email_str  + "The door lock is unlocked. ";
   }
   else if(!lock_open)
   {
     email_str = email_str  + "The door lock is locked. ";
   }


    Serial.println("email_str");
    email_int = 0;
 }
}

/////////////////////////////// check temp //////////////////////////
void check_temp()
{
 int chk = DHT.read11(temp_sensor);
  //Serial.print("Temperature = ");
 int temp_F = (DHT.temperature * 9/5) + 32;
 actual_temperature = temp_F;
 if(!temp_read)
 {
   wanted_temp = temp_F;
   temp_read = true;
 }
 if(temp_int == 1 || temp_int == 0)
 {
  
   if(temp_asked)
   {
     if(temp_int == 1)
     {
       ++wanted_temp;
     }
     else
     {
       --wanted_temp;
     }
     temp_asked = false;
   }
  
 }
 if(wanted_temp > temp_F)
 {
   digitalWrite(cool,HIGH);
   digitalWrite(warm,LOW);
 }
 else if(wanted_temp < temp_F)
 {
  digitalWrite(cool,LOW);
   digitalWrite(warm,HIGH);
 }
 else
 {
   digitalWrite(cool,LOW);
   digitalWrite(warm,LOW);
 }
 
}

////////////////////////////// message ////////////////////////////
void message()
{
   if (Serial.available() > 0) 
    {
      str = Serial.readStringUntil('\n');
      light_int = str.charAt(0) - '0';
      lock_int = str.charAt(2) - '0';
      garage_int = str.charAt(4) - '0';
      temp_int = str.substring(6).toInt();
      if(temp_int != 2)
      {
        temp_asked = true;
      }
      else
      {
        temp_asked = false;
      }
    }
}

//////////////////////////// light checker //////////////////////
void check_light()
{
  if(light_int == 1) 
  {
    digitalWrite(led1, HIGH);
    //Serial.println("light on");
  }
  else
  {
    digitalWrite(led1, LOW);
    //Serial.println("light off");
  }
      
}

////////////////////////////// lock ///////////////////////
void lock_door()
{
 if(lock_int == 1)
 {
   lock_servo.write(70);
   lock_open = true;
 }
 else if(lock_int == 0)
 {
   lock_servo.write(130);
   lock_open = false;
 }
 lock_int = 2;
}

//////////////////////////// states ///////////////////////////
typedef struct task {
  int state;
  unsigned long period;
  unsigned long elapsedTime;
  int (*TickFct)(int);

} task;

int delay_gcd;
const unsigned short tasksNum = 5; //number of states
task tasks[tasksNum];

////////////////////////light state /////////////////////
enum SM1_States{SM1_INIT,lights};
int SM1_Tick(int state1)
{
  switch (state1)
  {
    case SM1_INIT:
      state1 = lights;
      break;
    
   
    case lights:
      state1 = lights;
      break;
  }

  switch (state1)
  {
    case SM1_INIT:
      break;
    
    case lights:
      message();
      check_light();
      break;
  }

  return state1;
}

///////////////////////// temperature state ///////////////////////
enum SM2_States{SM2_INIT,temp};
int SM2_Tick(int state2)
{
 switch (state2)
 {
   case SM2_INIT:
     state2 = temp;
     break;
  
 
   case temp:
     state2 = temp;
     break;
 }


 switch (state2)
 {
   case SM2_INIT:
     break;
  
   case temp:
     check_temp();
     break;
 }


 return state2;
}

/////////////////////// lock servo state /////////////////////////////
enum SM5_States{SM5_INIT,lock};
int SM5_Tick(int state5)
{
 switch (state5)
 {
   case SM5_INIT:
     state5 = lock;
     break;
  
  
   case lock:
     state5 = lock;
     break;
 }


 switch (state5)
 {
   case SM5_INIT:
     break;
  
   case lock:
     lock_door();
     break;
 }
 return state5;
}

//////////////////////// recieve message ////////////////////////
enum SM6_States{SM6_INIT,mes};
int SM6_Tick(int state6)
{
 switch (state6)
 {
   case SM6_INIT:
     state6 = mes;
     break;
  
  
   case mes:
     state6 = mes;
     break;
 }


 switch (state6)
 {
   case SM6_INIT:
     break;
  
   case mes:
     message();
     break;
 }


 return state6;
}

//////////////////////// email state ////////////////////////
enum SM7_States{SM7_INIT,send_email};
int SM7_Tick(int state7)
{
 switch (state7)
 {
   case SM7_INIT:
     state7 = mes;
     break;
  
  
   case send_email:
     state7 = send_email;
     break;
 }


 switch (state7)
 {
   case SM7_INIT:
     break;
  
   case send_email:
     email();
     break;
 }


 return state7;
}



//////////////////////// setup /////////////////////////
void setup() {
  
  unsigned char i = 0;
  tasks[i].state = SM1_INIT;
  tasks[i].period = 500; 
  tasks[i].elapsedTime = 0;
  tasks[i].TickFct = &SM1_Tick;
  ++i;
  tasks[i].state = SM2_INIT;
  tasks[i].period = 1000;
  tasks[i].elapsedTime = 0;
  tasks[i].TickFct = &SM2_Tick;
  ++i;
  tasks[i].state = SM5_INIT;
  tasks[i].period = 0;
  tasks[i].elapsedTime = 0;
  tasks[i].TickFct = &SM5_Tick;
  ++i;
  tasks[i].state = SM6_INIT;
  tasks[i].period = 0;
  tasks[i].elapsedTime = 0;
  tasks[i].TickFct = &SM6_Tick;
  ++i;
  tasks[i].state = SM7_INIT;
  tasks[i].period = 0;
  tasks[i].elapsedTime = 0;
  tasks[i].TickFct = &SM7_Tick;


  Serial.begin(9600);
  pinMode(led1, OUTPUT);
  lock_servo.attach(lock_pin);
}

/////////////////////////////////// loop ///////////////////////////////

void loop() {
  // put your main code here, to run repeatedly:
  unsigned char i;
  for (i = 0; i < tasksNum; ++i) 
  {
    if ( (millis() - tasks[i].elapsedTime) >= tasks[i].period) {
      tasks[i].state = tasks[i].TickFct(tasks[i].state);
      tasks[i].elapsedTime = millis(); // Last time this task was ran
    }
  }

}