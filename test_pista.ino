#define LED_RED 9
#define LED_BLUE 10
#define LED_WHITE 6
#define LED_YELLOW 11

typedef enum {
  GREEN,
  YELLOW,
  RED,
} status_t;

typedef struct {
  int id;
  status_t status;
  int pin_out;
} street_t;

void change_status(int street_id, status_t status);
void parse_cmd(String cmd, int *id, status_t *status);

street_t streets[] = {
  {1, RED, LED_RED},
  {2, RED, LED_BLUE},
  {3, RED, LED_YELLOW},
  {4, RED, LED_WHITE},
};

void setup () {
  Serial.begin(9600);  // Avvia la comunicazione seriale a 9600 baud
  for (int i = 0; i < sizeof(streets) / sizeof(street_t); i++) {
	pinMode(streets[i].pin_out, OUTPUT);
    change_status(i + 1, streets[i].status);
  }
}

void loop () {
  int     id;
  status_t  status;

  while (Serial.available() == 0)
    ;
  String cmd = Serial.readStringUntil('\n');
  parse_cmd(cmd, &id, &status);
  change_status(id, status);
  delay(500);
}

/*
* Parse command "ID,STATUS\n"
*/
void parse_cmd(String cmd, int *id, status_t *status) {
  int commaIndex = cmd.indexOf(",");
  if (commaIndex == -1) {
    Serial.println("Invalid command format");
    return;
  }

  String id_str = cmd.substring(0, commaIndex);
  String status_str = cmd.substring(commaIndex + 1, cmd.indexOf("\n"));

  Serial.println(id_str);
  Serial.println(status_str);

  *id = id_str.toInt();
  *status = (status_t)(status_str.toInt());
}

/*
* Cambia lo stato di una strada
*/
void change_status(int street_id, status_t status) {
  if (street_id < 1 || street_id > 4) {
    Serial.println("Errore: id strada non valido");
    return;
  }

  street_t street = streets[street_id - 1];
  switch (status) {
  case RED:
  case YELLOW:
    digitalWrite(street.pin_out, LOW);
	Serial.print("Strada ");
	Serial.print(street.id);
	Serial.println(" LED spento");
    break;
  case GREEN:
 	 Serial.print("Strada ");
	Serial.print(street.id);
	Serial.println("LED acceso");
    digitalWrite(street.pin_out, HIGH);
    break;
  default:
    Serial.println("Errore: stato non valido");
    return;
  }
  street.status = status;
}
