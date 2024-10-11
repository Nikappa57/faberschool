typedef enum {
  GREEN,
  YELLOW,
  RED,
} status_t;

typedef struct {
  int id;
  status_t status;
  int pin_green;
  int pin_yellow;
  int pin_red;
  int pin_btn1;
  int pin_btn2;
} street_t;

void change_status(int street_id, status_t status);
void parse_cmd(String cmd, int *id, status_t *status);
void check_btn();

street_t streets[] = {
  {0, RED, 11, 12, 13, 10, 9},
};

void setup () {
  Serial.begin(9600);  // Avvia la comunicazione seriale a 9600 baud
  for (int i = 0; i < sizeof(streets) / sizeof(street_t); i++) {
    pinMode(streets[i].pin_green, OUTPUT);
    pinMode(streets[i].pin_yellow, OUTPUT);
    pinMode(streets[i].pin_red, OUTPUT);
    pinMode(streets[i].pin_btn1, INPUT);
    pinMode(streets[i].pin_btn2, INPUT);
    change_status(i, streets[i].status);
  }
}

void loop () {
  int     id;
  status_t  status;

  if (Serial.available() > 0) {
  String cmd = Serial.readStringUntil('\n');
    parse_cmd(cmd, &id, &status);
   change_status(id, status);
  }
  check_btn();
  delay(100);
}

/*
* Parse command "ID,STATUS\n"
*/
void parse_cmd(String cmd, int *id, status_t *status) {
  int commaIndex = cmd.indexOf(",");
  if (commaIndex == -1) {
    Serial.println("Errore: formato non valido");
    return;
  }

  String id_str = cmd.substring(0, commaIndex);
  String status_str = cmd.substring(commaIndex + 1, cmd.indexOf("\n"));

  *id = id_str.toInt();
  *status = (status_t)(status_str.toInt());
}

/*
* Cambia lo stato di una strada
*/
void change_status(int street_id, status_t status) {
  if (street_id < 0 || street_id >= sizeof(streets) / sizeof(street_t)) {
    Serial.println("Errore: id strada non valido");
    return;
  }

  street_t street = streets[street_id];
  
  switch (status) {
  case RED:
    digitalWrite(street.pin_green, LOW);
    digitalWrite(street.pin_yellow, LOW);
    digitalWrite(street.pin_red, HIGH);
    break;
  case YELLOW:
    digitalWrite(street.pin_green, LOW);
    digitalWrite(street.pin_yellow, HIGH);
    digitalWrite(street.pin_red, LOW);
    break;
  case GREEN:
    digitalWrite(street.pin_green, HIGH);
    digitalWrite(street.pin_yellow, LOW);
    digitalWrite(street.pin_red, LOW);
    break;
  default:
    Serial.println("Errore: stato non valido");
    return;
  }
  street.status = status;
}

void check_btn() {
  for (int i = 0; i < sizeof(streets) / sizeof(street_t); i++) {
    if (digitalRead(streets[i].pin_btn1) == HIGH) {
      Serial.print(i);
      Serial.println(",0\n");
    }
    if (digitalRead(streets[i].pin_btn2) == HIGH) {
      Serial.print(i);
      Serial.println(",1\n");
    }
  }
}
