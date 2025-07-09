/*
 *  Quadro XY para cesta de basquete ― versão sincronizada
 *  - Todos os comprimentos em centímetros
 *  - Os quatro motores terminam juntos
 *  - Espera 10 s antes do 1.º movimento
 */
#include <Stepper.h>
#include <math.h>
unsigned long atual;
unsigned long anterior = 0;
int sentido = 0;
int intervalo = 15000;

const int sensorPin = A4;

const int STEPS_REV = 2048;


/* --------- Instâncias dos quatro motores --------- */
Stepper stepperTL(STEPS_REV, 10, 12, 11, 13);     // (0,0) -1
Stepper stepperBL(STEPS_REV,  2,  4,  3,  5);     // (w,0) BL
Stepper stepperBR(STEPS_REV, A3, A1, A2, A0);     // (0,h) BR
Stepper stepperTR(STEPS_REV,  6,  8,  7,  9);     // (w,h) -1 



void moveUp(){
  for (int i = 0; i < 10; ++i) {
    stepperTL.step(-1);
    stepperTR.step(-1);
    stepperBL.step(-1); 
    stepperBR.step(-1);
  } 
}

void moveDown(){
  for (int i = 0; i < 10; ++i) {
    stepperTL.step(1);
    stepperTR.step(1);
    stepperBL.step(2); 
    stepperBR.step(2);
  } 
}

void moveLeft(){
  for (int i = 0; i < 10; ++i) {
    stepperTL.step(-2);
    stepperTR.step(1);
    stepperBL.step(2); 
    stepperBR.step(-1);
  } 
}

void moveRight(){
  for (int i = 0; i < 10; ++i) {
    stepperTL.step(1);
    stepperTR.step(-2);
    stepperBL.step(-1); 
    stepperBR.step(2);
  } 
}

/* ---------- Arduino ---------- */
void setup()
{
  Serial.begin(9600);
  stepperTL.setSpeed(15);   // rpm iguais para todos
  stepperTR.setSpeed(15);
  stepperBL.setSpeed(15);
  stepperBR.setSpeed(15);
  pinMode(sensorPin, INPUT);

  delay(4000);         
}

void quadrado(){
  unsigned long atual = millis();
  if(sentido == 0){
    moveUp();
  } else if(sentido == 1){
    moveRight();
  } else if(sentido == 2){
    moveDown();
  } else if(sentido == 3){
    moveLeft();
  }

  if((atual - anterior) >= intervalo){
    anterior = atual;
    sentido++;
    if (sentido > 3){
      sentido = 0;
    }
  }
}

void loop(){
  int sensorValue = digitalRead(sensorPin);
  if (sensorValue == HIGH){
    Serial.println("acertou");
    delay(50);
  }

  if(Serial.available() > 0) {
    String comando = Serial.readStringUntil("\n");
    comando.trim()

    if(comando == "up"){
      moveUp();
    } else if{comando == "down"}(
      moveDown();
    ) else if{comando == "right"}(
      moveRight();
    ) else if{comando == "left"}(
      moveLeft();
    )
  }
  
  


  delay(10);
}