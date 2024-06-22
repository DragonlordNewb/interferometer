#define LAS_PWR 2
#define SNS_PWR 3
#define SNS_DAT 5
#define BUZ_PWR 7
#define RED_PWR 8
#define YLO_PWR 9
#define GRN_PWR 10
#define BLU_PWR 11

#define MEASUREMENTS_PER_DATA_POINT 100
#define LASER_COOLDOWN_TIME_MS 5
#define THRESHOLD 0.05

unsigned int currentMeasurement = 0;
unsigned int measurements[MEASUREMENTS_PER_DATA_POINT];
unsigned int measurement;
unsigned long long s;
unsigned int t;
double dataPoint = 0;
double lastDataPoint = 0;
double ratio;

void ding(int lightPin = -1) {
  if (lightPin != -1) {
    digitalWrite(lightPin, HIGH);
  }
  tone(BUZ_PWR, 440, 100);
  delay(100);
  tone(BUZ_PWR, 707, 100);
  delay(100);
  if (lightPin != -1) {
    digitalWrite(lightPin, LOW);
  }
  delay(100);
}

void beep(int lightPin = -1) {
  if (lightPin != -1) {
    digitalWrite(lightPin, HIGH);
  }
  tone(BUZ_PWR, 330, 250);
  delay(250);
  if (lightPin != -1) {
    digitalWrite(lightPin, LOW);
  }
  delay(250);
}

void wow() {
  digitalWrite(GRN_PWR, HIGH);
  tone(BUZ_PWR, 1000, 100);
  delay(100);
  digitalWrite(GRN_PWR, LOW);
}

void systemsCheck() {
  digitalWrite(SNS_PWR, HIGH)
  while (digitalRead(SNS_DAT) == 0) {
    beep(RED_PWR);
  }
  ding(RED_PWR);
  digitalWrite(LAS_PWR, HIGH);
  while (digitalRead(SNS_DAt) == 1) {
    beep(RED_PWR);
  }
  ding(RED_PWR);
  digitalWrite(LAS_PWR, LOW);
}

void collectMeasurement() {
  measurement = 0;
  digitalWrite(LAS_PWR, HIGH);
  while (digitalRead(SNS_DAT) == 1);
  while (digitalRead(SNS_DAT) == 1) { measurement++; }
  digitalWrite(LAS_PWR, LOW);
  measurements[currentMeasurement] = measurement;
  currentMeasurement++;
  delay(LASER_COOLDOWN_TIME_MS);
}

void collectDataPoint() {
  lastDataPoint = dataPoint;
  s = 0;
  for (int i = 0; i < MEASUREMENTS_PER_DATA_POINT; i++) {
    t = s;
    s += measurements[i];
    if (s < t) {
      Serial.write("Overflow error\n");
    }
  }
  dataPoint = static_cast<double>(s) / MEASUREMENTS_PER_DATA_POINT;
  currentMeasurement = 0;
}

void setupPins() {
  pinMode(LAS_PWR, OUTPUT);
  pinMode(SNS_PWR, OUTPUT);
  pinMode(SNS_DAT, INPUT);
  pinMode(RED_PWR, OUTPUT);
  pinMode(YLO_PWR, OUTPUT);
  pinMode(GRN_PWR, OUTPUT);
  pinMode(BLU_PWR, OUTPUT);
}

void warning() {
  ding(YLO_PWR);
  for (int i = 0; i < 5; i++) {
    beep(YLO_PWR);
  }
}

void notify() {
  ding(YLO_PWR);
  ding(GRN_PWR);
  digitalWrite(GRN_PWR, HIGH);
}

void setup() {
  Serial.begin(9600);
  setupPins();
  systemsCheck();
  warning();
  notify();
}

void loop() {
  for (int i = 0; i < MEASUREMENTS_PER_DATA_POINT; i++) {
    collectMeasurement();
  }
  collectDataPoint();
  Serial.print(dataPoint);
  Serial.write("\n\r");
  if (dataPoint == 0) {
    beep(RED_PWR);
  }
  ratio = dataPoint / lastDataPoint;
  if (ratio > 1 + THRESHOLD || ratio < 1 - THRESHOLD) {
    wow();
  }
}
