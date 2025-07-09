#include <Servo.h>

Servo servo_horizontal;
Servo servo_vertical;

// Pinos do joystick
const int pinX = A0;
const int pinY = A1;

// Valores atuais da "posição" relativa
long posX = 0;
long posY = 0;

// Tempo de controle
unsigned long lastUpdate = 0;
const unsigned long interval = 50; // Atualização a cada 50ms

// Sensibilidade e zona morta
const int deadZone = 330;  // Ignora pequenas variações no centro
const float speedFactor = 0.05;  // Controla a velocidade de deslocamento

//LANÇADOR
const int out8 = 8;
const int out9 = 9;
const int ena = 10;
const int inA2 = A2;
int lancamentoStartTime, atirando;
//LANÇADOR

void setup() {
  Serial.begin(9600);
 
  servo_horizontal.attach(2);  // Pino do servo horizontal
  servo_vertical.attach(3);    // Pino do servo vertical
  //servo_horizontal.write(0);
  //servo_vertical.write(0);

  //LANÇADOR
  pinMode(out8, OUTPUT);
  pinMode(out9, OUTPUT);
  pinMode(ena, OUTPUT);
  pinMode(inA2, INPUT);
  //LANÇADOR
}

void atirar()
{
  lancamentoStartTime = millis();
  atirando = 1;
  //Serial.println("atirando!");
}

void lancador()
{
  int sensorValue = analogRead(inA2);
  
  /*
  Serial.print("sensorValue: ");
  Serial.println(sensorValue);
  Serial.print("millis() - lancamentoStartTime: ");
  Serial.println(millis() - lancamentoStartTime);
  */

  if ((sensorValue || millis() - lancamentoStartTime < 1000) && atirando)
  {
    // Run motor forward
    digitalWrite(out8, LOW);
    digitalWrite(out9, HIGH);
    analogWrite(ena, 50); // set speed
  } 
  else
  {
    // Stop motor
    digitalWrite(out8, HIGH);
    digitalWrite(out9, HIGH);
    analogWrite(ena, 0);
    atirando = 0;
  }
}

void loop() {
  delay(20);

  //LANÇADOR
  lancador();
  //LANÇADOR

  if (Serial.available() > 0) 
  {
    String texto = Serial.readStringUntil('\n');
    texto.trim(); // Remove espaços em branco e quebras de linha

    //LANÇADOR
    if (texto == "Disparar")
    {
      atirar();
    }
    //LANÇADOR
    else
    {
      int separador = texto.indexOf(',');
      if (separador > 0)
      {
        String horizontalStr = texto.substring(0, separador);
        String verticalStr = texto.substring(separador + 1);

        int horizontal = horizontalStr.toInt();
        int vertical = verticalStr.toInt();

        // Garante que os valores estejam entre 0 e 180
        horizontal = constrain(horizontal, 0, 180);
        vertical = constrain(vertical, 0, 180);

        servo_horizontal.write(horizontal);
        servo_vertical.write(vertical);

        Serial.print("Servo horizontal: ");
        Serial.print(horizontal);
        Serial.print(" | Servo vertical: ");
        Serial.println(vertical);
      }
    }
  }
}
