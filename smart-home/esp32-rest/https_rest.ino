// LIBRARIES & VARS

// Parsing Libraries
#include <ArduinoJson.h>
#include <string.h>
#include "time.h"

// Connection Libraries
#include <WiFiClientSecure.h>       // includes Wifi.h

// Network Vars
String ssid = "";
String password = "";

// REST / AWS API Gateway Vars
int port = 443;
const char* host = "tg0crx57g5.execute-api.us-east-2.amazonaws.com";
String path = "/a2b/dev";

// Initialize Server & Wifi Over SSL
// Server needs to be set to port 80 for direct wireless communications
WiFiServer server(80);
WiFiClientSecure sClient;

// Polling Vars
unsigned long last_poll;
unsigned long current;
// rate is set to 5s for demo with 1 device
// rate should be higher for prod (30 sec?)
// rate can be lower in prod if using smart polling (15 sec?)
unsigned long poll_rate = 5000;   // 5 sec

// Smart Device Variables
// Basic info describing the device; must be set during manufacture
int dev_subid_count = 1;      // number of sub-devices for this device
String dev_type = "switch";   // type of device

// AWS PUT Queue for Config Updates
// Only covers configs that the device will update indepently of the app
// Indexes in order: 0:devState, 1:devLogs, 2:acctNet
int put_queue[3] = {0,0,0};

// JSON Config Variables
// Read in from file system & keep global
JsonDocument devState;
JsonDocument devInfo;
JsonDocument devTimer;
JsonDocument devSched;
JsonDocument devLogs;
JsonDocument acctNet;
JsonDocument acctUpdates;

// Amazon's root CA. This should be the same for everyone.
// NOTE: Could be saved in a file and read from the file system
const char* aws_root_ca = "-----BEGIN CERTIFICATE-----\n" \
"MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\n" \
"ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\n" \
"b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\n" \
"MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\n" \
"b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\n" \
"ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\n" \
"9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\n" \
"IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\n" \
"VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\n" \
"93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\n" \
"jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\n" \
"AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\n" \
"A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\n" \
"U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\n" \
"N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\n" \
"o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\n" \
"5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\n" \
"rqXRfboQnoZsG4q5WTP468SQvvG5\n" \
"-----END CERTIFICATE-----\n";

// =========================================================
// Functions - Utility
// =========================================================

// Setup Time ----------------------------------------------
void setup_time(){
  const char* ntpServer = "pool.ntp.org";
  //const long  gmtOffset_sec = 0;
  //const int   daylightOffset_sec = 3600;

  // Initialize and get current time - gets UTC time with no offsets
  // param1 = gmtOffset in seconds, param2 = dstOffset in seconds
  configTime(0, 0, ntpServer);

  // setup polling variables
  last_poll = millis();
}

// Get timestamp as y-m-d-s --------------------------------
// Output: Current time as "y-m-d-s"
String get_current_time(){
  // Var for time info
  struct tm timeinfo;

  // Attempt to get current UTC time
  if(!getLocalTime(&timeinfo)){
    //Serial.println("Failed to obtain time");
    return "";
  }

  // Assign date values to up
  int y = timeinfo.tm_year + 1900;
  int m = timeinfo.tm_mon + 1;
  int d = timeinfo.tm_mday;
  int s = (timeinfo.tm_hour*3600) + (timeinfo.tm_min*60) + timeinfo.tm_sec;

  // Build & return as a string
  String timestamp = String(y) + "-" + String(m) + "-" + String(d) + "-" + String(s);

  return timestamp;
}

// Get Time Difference in Days -----------------------------
// Input: tnew = told = time as strings in 'y-m-d-s' format
// NOTE: expects tnew to be larger (newer) than told (older)
int get_tdiff_days(String tnew, String told){
  int i, j;
  int y, m, d;
  String sy, sm, sd;
  int ntd, nty, otd, oty;
  int diff;

  // convert tnew into int array without seconds
  i = tnew.indexOf("-");
  sy = tnew.substring(0,i);
  y = sy.toInt();
  j = tnew.indexOf("-", (i+1));
  sm = tnew.substring(i,j);
  m = sm.toInt();
  i = tnew.indexOf("-", (j+1));
  sd = tnew.substring(j,i);
  d = sd.toInt();
  int nt[3] = {y, m, d};

  // convert told into int array without seconds
  i = told.indexOf("-");
  sy = told.substring(0,i);
  y = sy.toInt();
  j = told.indexOf("-", (i+1));
  sm = told.substring(i,j);
  m = sm.toInt();
  i = told.indexOf("-", (j+1));
  sd = told.substring(j,i);
  d = sd.toInt();
  int ot[3] = {y, m, d};

  // build list of days in each month (months are indices)
  // each element is day of year for the 1st of that month
  // m:d - 1:31, 2:28/29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31
  // if year % 4 = 0 and month is > 2, add 1
  int months[12] = {1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335};
  int leap_mon[12] = {1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336};

  // find day of year for tnew
  if((nt[0] % 4) == 0){
    ntd = leap_mon[nt[1]-1] + nt[2]; }
  else{
    ntd = months[nt[1]-1] + nt[2]; }

  // find day of year & days in year for told
  if((ot[0] % 4) == 0){
    otd = leap_mon[ot[1]-1] + ot[2];
    oty = 366; }
  else{
    otd = months[ot[1]-1] + ot[2];
    oty = 365; }

  // find diff in days based on if years are equal or not
  if(nt[0] == ot[0]){
    diff = ntd - otd; }
  else{
    diff = ntd + (oty - otd); }

  return diff;
}

// Test if Time A is Older than Time B ---------------------
// Input: a = b = time as strings in 'y-m-d-s' format
bool a_isOlder(String a, String b){
  // get difference in days
  int diff = get_tdiff_days(b, a);

  // test difference in days
  if(diff > 0){         // a is older
    return true;
  }
  else if(diff == 0){   // same day, compare sec
    // get a sec, then b sec
    int i = a.lastIndexOf("-") + 1;
    int j = b.lastIndexOf("-") + 1;
    String sub_a = a.substring(i);
    String sub_b = b.substring(j);
    i = sub_a.toInt();
    j = sub_b.toInt();

    // find difference & return accordingly
    if((j - i) > 0){        // a is older
      return true;
    }
  }

  // default return
  return false;
}

// Convert JSON doc to String ------------------------------
// Input: JSON-formatted data
// Output: JSON data as a String
String json2str(JsonDocument jDoc){
  String jStr;
  serializeJson(jDoc, jStr);
  return jStr;
}

// Convert String to JSON doc ------------------------------
// Input: JSON data as a String
// Output: JSON-formatted data
JsonDocument str2json(String jStr){
  JsonDocument jDoc;
  deserializeJson(jDoc, jStr);
  return jDoc;
}

// =========================================================
// Functions - Networking
// =========================================================

// Connect to Wi-Fi ----------------------------------------
// NOTE: Will only try to connect for 10s, call again if needed
void connectWifi(){
  // Start connection
  Serial.print("\nAttempting to connecting to "); Serial.print(ssid);
  WiFi.begin(ssid.c_str(), password.c_str());

  // Wait up to 10s for the WiFi to connect
  int waiting = 0;
  int timeout = 5;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); Serial.print('.');
    if(waiting == timeout){
      Serial.println(); break; }
    else{ waiting++; }
  }

  // Run failed to connect case & return early
  if(waiting == timeout){
    Serial.println("\nConnection failed!");
    return;
  }

  // Save IP address & print confirmation message
  Serial.println("\nConnection established!");
  Serial.print("IP address: "); Serial.println(WiFi.localIP());

  // Set up time
  setup_time();

  // Update acctNet
  update_acctNet();

  // Set Up SSL for Secure Client & return normally
  sClient.setCACert(aws_root_ca);
  return;
}

// Set Up ESP32 as Wi-Fi Access Point ----------------------
void setupWifiAP(){
  // ap = hostname, ssid, & password of the device as an AP
  const char* ap = "VSP-ESP32";
  const char* apssid = "esp32-qr-test";
  const char* appass = "Esp32!test";

  // Set hostname
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(ap);

  // Connect to Wi-Fi network with (SSID, password)
  // To make the AP open, remove the password parameter
  Serial.print("Setting AP (Access Point)...");
  WiFi.softAP(apssid, appass);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
}

// Setup Network -------------------------------------------
void setupNet(){
  // Set Wi-Fi Mode to act as an AP & a station
  WiFi.mode(WIFI_AP_STA);

  // Setup Access Point & start server
  setupWifiAP();
  server.begin();

  // If SSID & Password are known, connect to Wi-Fi
  if(ssid != ""){ connectWifi(); }
}

// =========================================================
// Functions - REST API
// =========================================================

// REST Request - Get IP Address of "dev_id" ---------------
// Input: dev = "dev_id" of the destination device
// Output: ip = String type of IP address for destination device
String getDevIP(String dev){
  // Verify that acctNet is not null before proceding
  if(acctNet.isNull()){ return "NO NET DATA"; }

  // Get the size of acctNet["data"] & acctNet["data"][i]["sdata"] & interate
  int dSize = acctNet["data"].size();
  for(int i=0; i<dSize; i++){
    int sdSize = acctNet["data"][i]["sdata"].size();
    for(int j=0; j<sdSize; j++){

      // If dev.toInt() matches "dev_id", return the IP address
      if(acctNet["data"][i]["sdata"][j]["dev_id"] == dev.toInt()){
        return acctNet["data"][i]["sdata"][j]["local_ip"].as<String>();
      }

    }
  }

  // Return default String value
  return "IP NOT FOUND";
}

// REST Request - GET --------------------------------------
// Input: table = config data to GET, dest = "aws" or "dev_id" for GET
// Output: config data or error message retrieved
String rest_get(String table, String dest){
  String rest_host;
  String rest_path;
  String query = "?table=" + table;

  // Build query based on destination - "aws" or "dev"
  if(dest == "aws"){
    query += "&acct=" + devInfo["account"].as<String>();
    query += "&dev=" + devInfo["dev_id"].as<String>();
  }

  // Select the host & path based on destination - "aws" or "dev"
  if(dest == "aws"){
    rest_host = String(host);
    rest_path = path; }
  else{
    // should always get an IP if sending device-to-device
    rest_host = getDevIP(dest);
    rest_path = "/"; }

  if(!sClient.connect(rest_host.c_str(), port)){
    Serial.println("Connection to the server failed!"); }
  else{
    // Make a HTTP request
    sClient.println("GET " + rest_path + query + " HTTP/1.1");
    sClient.println("Host: " + rest_host);
    sClient.println("Accept: application/json");
    sClient.println("Connection: close\r\n");

    // eat response header
    while(sClient.connected()){
      String line = sClient.readStringUntil('\n');
      if(line == "\r"){ break; } }

    // read any incoming bytes from the server
    String body = "";
    while(sClient.available()){
      char c = sClient.read();
      body = body + c; }

    sClient.stop();

    // return response body
    return body;
  }
}

// REST Request - PUT --------------------------------------
// Input: table = config type to PUT, doc = config data, dest = "aws" or "dev_id" to PUT to
// Output: SUCCESS response or newer config data
String rest_put(String table, JsonDocument doc, String dest){
  String rest_host;
  String rest_path;

  // Convert the JsonDocument data into a JSON string & get its length
  String data = json2str(doc);
  String len = String(data.length());
  Serial.println(data);

  // Select the host & path based on destination - "aws" or "dev"
  if(dest == "aws"){
    rest_host = String(host);
    rest_path = path; }
  else{
    rest_host = getDevIP(dest);
    rest_path = "/"; }

  if(!sClient.connect(rest_host.c_str(), port))
    Serial.println("Connection to the server failed!");
  else{
    // Make a HTTP request:
    sClient.println("PUT " + rest_path + "?table=" + table + " HTTP/1.1");
    sClient.println("Host: " + rest_host);
    sClient.println("Content-Type: application/json");
    sClient.println("Content-Length: " + len);
    sClient.println("Connection: close\r\n");
    sClient.print(data);

    // eat response header
    while(sClient.connected()){
      String line = sClient.readStringUntil('\n');
      if (line == "\r") { break; } }

    // read any incoming bytes from the server
    String body = "";
    while(sClient.available()){
      char c = sClient.read();
      body = body + c; }

    sClient.stop();

    // return response body
    return body;
  }
}

// =========================================================
// Functions - JSON Data Management
// =========================================================

// Initialize devInfo --------------------------------------
// NOTE: Only use when no devInfo.json file exists at startup
void init_devInfo(){
  // Build initial structure
  devInfo["account"] = 0;
  devInfo["dev_id"] = 0;
  devInfo["last_update"] = get_current_time();
  devInfo["net_ssid"] = "";
  devInfo["net_pass"] = "";

  // Build initial data
  for(int i=0; i<dev_subid_count; i++){
    devInfo["data"][i]["dev_subid"] = i+1;
    devInfo["data"][i]["pow"] = 0;
    devInfo["data"][i]["amp"] = 0;
    devInfo["data"][i]["dev_type"] = dev_type;
    if(i == 0){ devInfo["data"][i]["dev_name"] = "living room light";}
    if(i == 1){ devInfo["data"][i]["dev_name"] = "bedroom fan";}
  }

  return;
}

// Initialize devState -------------------------------------
// NOTE: Only use when no devState.json file exists at startup
void init_devState(){
  // Build initial structure
  devState["account"] = 0;
  devState["dev_id"] = 0;
  devState["last_update"] = get_current_time();

  // Build initial data
  for(int i=0; i<dev_subid_count; i++){
    devState["data"][i]["dev_subid"] = i+1;
    devState["data"][i]["v_percent"] = 0;
    devState["data"][i]["locked"] = 0;
  }

  return;
}

// Update devState -----------------------------------------
// Input: subid = dev_subid that was altered,
//        v_percent = v_percent that device was changed to,
//        lock = lock state device was changed to (0 = unlocked, 1 = locked)
void update_devState(int subid, int v_percent, int lock){
  int flag = 0;     // update flag, 0 if no updates occurred

  // test if v_percent changed, update accordingly
  if(devState["data"][subid-1]["v_percent"].as<unsigned int>() != v_percent){
    flag = 1;
    devState["data"][subid-1]["v_percent"] = v_percent;
  }

  // test if lock changed, update accordingly
  if(devState["data"][subid-1]["locked"].as<unsigned int>() != lock){
    flag = 1;
    devState["data"][subid-1]["locked"] = lock;
  }

  // Update "last_update" & put_queue if change occurred
  if(flag == 1){
    devState["last_update"] = get_current_time();

    // if "account" is not null, update PUT queue
    if(devState["account"] > 0){
      // update PUT queue - indexes in order: 0:devState, 1:devLogs, 2:acctNet
      put_queue[0] = 1;
    }
  }

  return;
}

// Initialize devLogs --------------------------------------
// NOTE: Only use when no devLogs.json file exists at startup
void init_devLogs(){
  // Build initial structure
  devLogs["account"] = 0;
  devLogs["dev_id"] = 0;
  devLogs["last_update"] = get_current_time();

  // Build initial data
  devLogs["data"][0]["time"] = devLogs["last_update"].as<String>();
  devLogs["data"][0]["dev_subid"] = 1;
  devLogs["data"][0]["pow"] = 0;
  devLogs["data"][0]["amp"] = 0;
  devLogs["data"][0]["chg_from"] = 0;
  devLogs["data"][0]["chg_to"] = 0;
  devLogs["data"][0]["trigger"] = "Initialization";
  devLogs["data"][0]["message"] = "Initialized devLogs";

  return;
}

// Add Log to devLogs --------------------------------------
// Input: subid = sub-device, chg_to = v_percent changed to
//        trig = event trigger, msg = event message
void addLog_devLogs(int subid, int chg_to, String trig, String msg){
  // Get size of logs["data"] for index
  int ls = devLogs["data"].size();

  // Update "last_update"
  devLogs["last_update"] = get_current_time();

  // Build initial data
  devLogs["data"][ls]["time"] = devLogs["last_update"].as<String>();
  devLogs["data"][ls]["dev_subid"] = subid;
  devLogs["data"][ls]["pow"] = devInfo["data"][subid-1]["pow"].as<unsigned int>();
  devLogs["data"][ls]["amp"] = devInfo["data"][subid-1]["amp"].as<float>();
  devLogs["data"][ls]["chg_from"] = devLogs["data"][ls-1]["chg_from"].as<unsigned int>();
  devLogs["data"][ls]["chg_to"] = chg_to;
  devLogs["data"][ls]["trigger"] = trig;
  devLogs["data"][ls]["message"] = msg;

  // if "account" is not null, update PUT queue
  if(devLogs["account"] > 0){
    // update PUT queue - indexes in order: 0:devState, 1:devLogs, 2:acctNet
    put_queue[1] = 1;
  }

  return;
}

// Purge Logs Older Than 7 Days ----------------------------
void purge7d_devLogs(){
  // Get size of logs["data"] for index
  int ls = devLogs["data"].size();
  int diff;
  String time = get_current_time();

  // Reverse interate through each log & apply 7 day purge
  for(int i=ls; i>=0; i--){
    diff = get_tdiff_days(time, devLogs["data"][i]["time"]);
    if(diff > 7){
      devLogs["data"].remove(i); }
  }

  return;
}

// Initialize acctNet --------------------------------------
// NOTE: Only use when a Wi-Fi connection is made & acctNet is null
void init_acctNet(){
  // Build IP Address for current connection
  IPAddress ip = WiFi.localIP();
  String ipStr = String(ip[0]) + "." + String(ip[1]) + "." + String(ip[2]) + "." + String(ip[3]);

  // Build initial structure
  acctNet["account"] = devInfo["account"].as<unsigned int>();
  acctNet["last_update"] = get_current_time();

  // Build initial data
  acctNet["data"][0]["net_ssid"] = devInfo["net_ssid"].as<String>();
  acctNet["data"][0]["sdata"][0]["dev_id"] = devInfo["dev_id"].as<unsigned int>();
  acctNet["data"][0]["sdata"][0]["local_ip"] = ipStr;
  acctNet["data"][0]["sdata"][0]["connected_on"] = acctNet["last_update"].as<String>();

  return;
}

// Update acctNet ------------------------------------------
void update_acctNet(){
  // Build IP Address & SSID for current connection
  IPAddress ip = WiFi.localIP();
  String ipStr = String(ip[0]) + "." + String(ip[1]) + "." + String(ip[2]) + "." + String(ip[3]);
  ssid = String(WiFi.SSID());

  // If acctNet is null, initialize it - shouldn't be a case for this
  if(acctNet.isNull()){
    init_acctNet();
  }
  else{   // update acctNet if needed
    // Find correct "net_ssid"
    int dSize = acctNet["data"].size();
    for(int i=0; i<dSize; i++){
      if(acctNet["data"][i]["net_ssid"] == ssid){
        
        // Find correct "dev_id"
        int sdSize = acctNet["data"][i]["sdata"];
        for(int j=0; j<sdSize; j++){
          if(acctNet["data"][i]["sdata"][j]["dev_id"] == devInfo["dev_id"]){
            
            // If "local_ip" does not match current IP, update it & "last_update"
            if(acctNet["data"][i]["sdata"][j]["local_ip"] != ipStr){
              acctNet["data"][i]["sdata"][j]["local_ip"] = ipStr;
              acctNet["last_update"] = get_current_time();

              // update PUT queue - indexes in order: 0:devState, 1:devLogs, 2:acctNet
              // Assumes that AWS connection exists since acctNet is only set when it does
              put_queue[2] = 1;
            }

            // Break inner for loop
            break;
          }
        }

        // Break outer for loop
        break;
      }
      else{
        // else SSID is not in acctNet, re-initialize it
        acctNet.clear();
        init_acctNet();
      }
    }

    // Update devInfo if SSID is different than what is known
  }

  return;
}

// Reset Device --------------------------------------------
// Called when devDelete found in acctUpdates or app sends DELETE command
void reset_device(){
  // clear ssid & password
  ssid = "";
  password = "";

  // clear all configs
  devState.clear();
  devInfo.clear();
  devTimer.clear();
  devSched.clear();
  devLogs.clear();
  acctNet.clear();
  acctUpdates.clear();

  // delete all configs
  // delete devState, devInfo, devTimer, devSched, devLogs, acctNet
  // no need to delete acctUpdates

  // reinitialize basic configs
  init_devInfo();
  init_devState();
  init_devLogs();

  return;
}

// Rename Device -------------------------------------------
// Called when "new_id-###" is found in acctUpdates or PUT by app
void rename_device(String rename){
  // get new_id from String
  int slen = rename.length();
  int i = rename.indexOf("-");
  String dev = rename.substring(i,slen);
  int new_id = dev.toInt();

  //set "new_id" as "dev_id" in devInfo
  // devInfo is used for "dev_id" in rest_get()
  devInfo["dev_id"] = new_id;

  return;
}

// Initialize System ---------------------------------------
// Used to initialize all data from the file system
// FIX ME - needs file logic
void init_system(){
  // Initialize SPI & Device - FIX ME

  // load all configs
  // for each load, only assign to JSON var if data exists
  // load devInfo, devState, devTimer, devSched, devLogs, acctNet
  // no need to initialize acctUpdates.json

  // if devInfo is null, initialize
  if(devInfo.isNull()){
    init_devInfo();
  }
  else{     // else, not null, set ssid & password
    ssid = devInfo["net_ssid"].as<String>();
    password = devInfo["net_pass"].as<String>();
  }

  // if devState is null, initialize
  if(devState.isNull()){
    init_devState();
  }

  // if devLogs is null, initialize
  if(devLogs.isNull()){
    init_devLogs();
  }

  return;
}

// =========================================================
// Functions - Primary Loop Functions
// =========================================================

// Main Polling --------------------------------------------
void main_polling(){
  // Return if SSID has not been set, else, attempt to connect if not connected
  if(ssid == ""){ return; }
  else if(WiFi.status() != WL_CONNECTED){ connectWifi(); }

  // Return if outside of the polling interval
  // put polling rate check in loop() around this function instead
  //if((current - last_poll) < poll_rate){ return; }

  // Only run if WiFi is connected
  if(WiFi.status() == WL_CONNECTED){
    // Send any updates queued in put_queue - indexes: 0:devState, 1:devLogs, 2:acctNet
    String resp;
    if(put_queue[0] == 1){        // devState
      resp = rest_put("devState", devState, "aws");
      put_queue[0] = 0;
      Serial.println("PUTting devState");

      // handle unsucessful rest_put response - newer data returned
      if(resp != "SUCCESS"){
        devState.clear();
        devState = str2json(resp);
      }
    }
    else if(put_queue[1] == 1){  // devLogs
      resp = rest_put("devLogs", devLogs, "aws");
      put_queue[1] = 0;
      Serial.println("PUTting devLogs");

      // handle unsucessful rest_put response - newer data returned
      if(resp != "SUCCESS"){
        devLogs.clear();
        devLogs = str2json(resp);
      }
    }
    else if(put_queue[2] == 1){  // acctNet
      resp = rest_put("acctNet", acctNet, "aws");
      put_queue[2] = 0;
      Serial.println("PUTting acctNet");

      // handle unsucessful rest_put response - newer data returned
      if(resp != "SUCCESS"){
        acctNet.clear();
        acctNet = str2json(resp);
      }
    }

    // Get updates for the account
    String updates = rest_get("acctUpdates", "aws");
    Serial.print("Updates retrieved: "); Serial.println(updates);

    // Convert the string to JSON
    acctUpdates = str2json(updates);

/*    // Parse acctUpdates - Check JSON keys to see which format was returned
    if(acctUpdates.containsKey("net_ssid")){
      // smart network polling - acctUpdates in "net_ssid" JSON format:
      // {"net_ssid":"ssid","sdata":[{"dev_id":dev_id,"updates":["update",...]},{...}]}
      int uSize = 0;

      // FIX ME - smart polling logic goes here
      // smart polling is not setup, so this will never trigger

      // process updates for this device first
      // then process update handling for other devices on the network

      // manage special cases - acctNet priority update
      // acctNet is only a priority with smart polling
      for(int i=0; i<uSize; i++){
        if(acctUpdates["updates"][i].as<String>() == "acctNet"){
          // GET updates, clear JsonDocument, & convert string to JSON
          updates = rest_get("acctNet", "aws");
          acctNet.clear();
          acctNet = str2json(updates);

          // remove update from "updates" list and break for loop
          acctUpdates["updates"].remove(i);
          break;
        }
      }

      // clear acctUpdates when done
      acctUpdates.clear();
    }
    else{
*/      // simple device polling - acctUpdates in "dev_id" JSON format:
      // {"dev_id":dev_id,"updates":["update",...]}
      String first = "";

      // get size of "updates" list
      int uSize = acctUpdates["updates"].size();
      
      // return if no updates were found
      if(uSize == 0){ return; }
  
      // get first update for special cases
      if(uSize == 1){
        first = acctUpdates["updates"][0].as<String>();
      }

      // manage special cases - devRename & devDelete cases
      // "new_id-###" & devDelete will always be the only update when made
      if(first != ""){
        if(first == "devDelete"){               // devDelete case
          reset_device();
        }
        else if(first.startsWith("new_id-")){   // "new_id-###" case
          // rename the device
          rename_device(first);
          acctUpdates.clear();
          // other updates tied to "new_id" will be retrieved next polling cycle
        }
      }

      // rest_get each update if acctUpdates is not null after special cases
      // assumes devDelete & new_id-### options will be the only update in list if present
      if(!acctUpdates.isNull()){
        for(int i=0; i<uSize; i++){

          // if devState, devInfo, devTimer, devSched, or acctNet - overwrite data
          if(acctUpdates["updates"][i].as<String>() == "devState"){
            // GET updates, clear JsonDocument, & convert string to JSON
            updates = rest_get("devState", "aws");
            devState.clear();
            devState = str2json(updates);
            Serial.println("GETting devState");
            Serial.println(updates);

            // remove update from "updates" list and break for loop
            acctUpdates["updates"].remove(i);
          }
          if(acctUpdates["updates"][i].as<String>() == "devInfo"){
            // GET updates, clear JsonDocument, & convert string to JSON
            updates = rest_get("devInfo", "aws");
            devInfo.clear();
            devInfo = str2json(updates);
            Serial.println("GETting devInfo");
            Serial.println(updates);

            // remove update from "updates" list and break for loop
            acctUpdates["updates"].remove(i);
          }
          if(acctUpdates["updates"][i].as<String>() == "devTimer"){
            // GET updates, clear JsonDocument, & convert string to JSON
            updates = rest_get("devTimer", "aws");
            devTimer.clear();
            devTimer = str2json(updates);
            Serial.println("GETting devTimer");
            Serial.println(updates);

            // remove update from "updates" list and break for loop
            acctUpdates["updates"].remove(i);
          }
          if(acctUpdates["updates"][i].as<String>() == "devSched"){
            // GET updates, clear JsonDocument, & convert string to JSON
            updates = rest_get("devSched", "aws");
            devSched.clear();
            devSched = str2json(updates);
            Serial.println("GETting devSched");
            Serial.println(updates);

            // remove update from "updates" list and break for loop
            acctUpdates["updates"].remove(i);
          }
          if(acctUpdates["updates"][i].as<String>() == "acctNet"){
            // GET updates, clear JsonDocument, & convert string to JSON
            updates = rest_get("acctNet", "aws");
            acctNet.clear();
            acctNet = str2json(updates);
            Serial.println("GETting acctNet");
            Serial.println(updates);

            // remove update from "updates" list and break for loop
            acctUpdates["updates"].remove(i);
          }
        }
      }

      // clear acctUpdates
      acctUpdates.clear();
//    }
  }
  else {
    Serial.println("WiFi disconnected!");
    connectWifi();
  }

  return;
}

// Main AP Listening ---------------------------------------
void main_listening(){
  String header = "";
  String body = "";

  // listen for connections
  // will only return clients that are immediately available
  WiFiClient svrClient = server.available();

  // If connection made, interact with it
  if(svrClient){
    Serial.println("Client connected.");

    // read incoming header bytes
    while(svrClient.connected()){
      String line = svrClient.readStringUntil('\n');
      header = header + "\n" + line;
      if (line == "\r") { break; }
    }
    header.trim();
    Serial.println("Header:");
    Serial.println(header);

    // read incoming body bytes
    while(svrClient.available()){
      char c = svrClient.read();
      body = body + c;
    }
    body.trim();
    Serial.println("Body:");
    Serial.println(body);
  }

  // if header is an empty string, return, else parse
  if(header == ""){ return; }
  else{
    String method = "";
    String table = "";

    // determine the HTTP method
    if(header.startsWith("GET")){
      method = "GET"; }
    else if(header.startsWith("PUT")){
      method = "PUT"; }
    else if(header.startsWith("DELETE")){
      method = "DELETE"; }
    
    // if method is DELETE, reset the device
    if(method == "DELETE"){
      reset_device();
    }
    else{   // else, extract the table
      // find index of first "=" & "&", then extract table
      // expects: ".../?table=devConfig&..."
      int eq = header.indexOf("=");
      int amp = header.indexOf("&");
      table = header.substring((eq+1), amp);

      if(method == "GET"){      // if method is GET
        JsonDocument get_data;

        // copy table to get_data - if devInfo, remove "net_pass"
        if(table == "devInfo"){ get_data = devInfo; get_data["net_pass"] = ""; }
        else if(table == "devState"){ get_data = devState; }
        else if(table == "devTimer"){ get_data = devTimer; }
        else if(table == "devSched"){ get_data = devSched; }
        else if(table == "devLogs"){ get_data = devLogs; }

        // convert get_data to string & get length
        String respBody = json2str(get_data);
        int respLen = respBody.length();

        // print to serial
        Serial.print("Sending: "); Serial.println(respBody);

        // respond
        svrClient.println("HTTP/1.1 200 OK");
        svrClient.println("Content-Type: application/json");
        svrClient.print("Content-Length: "); svrClient.println(respLen);
        svrClient.println("Connection: close");
        svrClient.println();
        svrClient.println(respBody);
      }
      else if(method == "PUT"){     // else if method is PUT
        JsonDocument jBody = str2json(body);
        body = "";    // reinitialize

        // check if PUT data is newer, clear old data & store new data
        if(table == "devInfo"){
          if(a_isOlder(devInfo["last_update"].as<String>(), jBody["last_update"].as<String>())){
            devInfo.clear();
            devInfo = jBody;

            // check for SSID & password, then set if found
            ssid = devInfo["net_ssid"].as<String>();
            password = devInfo["net_pass"].as<String>();
          }
          else{   // PUT data is older, respond with newer data
            body = json2str(devInfo);
          }
        }
        else if(table == "devState"){
          if(a_isOlder(devState["last_update"].as<String>(), jBody["last_update"].as<String>())){
            devState.clear();
            devState = jBody;
          }
          else{   // PUT data is older, respond with newer data
            body = json2str(devState);
          }
        }
        else if(table == "devTimer"){
          if(a_isOlder(devTimer["last_update"].as<String>(), jBody["last_update"].as<String>())){
            devTimer.clear();
            devTimer = jBody;
          }
          else{   // PUT data is older, respond with newer data
            body = json2str(devTimer);
          }
        }
        else if(table == "devSched"){
          if(a_isOlder(devSched["last_update"].as<String>(), jBody["last_update"].as<String>())){
            devSched.clear();
            devSched = jBody;
          }
          else{   // PUT data is older, respond with newer data
            body = json2str(devSched);
          }
        }
        else if(table == "devLogs"){
          if(a_isOlder(devLogs["last_update"].as<String>(), jBody["last_update"].as<String>())){
            devLogs.clear();
            devLogs = jBody;
          }
          else{   // PUT data is older, respond with newer data
            body = json2str(devLogs);
          }
        }
        else if(table == "acctUpdates"){
          // used during smart polling - not implemented yet, so this will not get called
          if(acctUpdates.isNull()){   // if null, assign new updates
            acctUpdates = jBody;
          }
          else{                       // else, append anything missing
            int oldSize = acctUpdates["updates"].size();
            int newSize = jBody["updates"].size();
            int count = 0;

            // loop through each array & append missing updates into acctUpdates
            for(int i=0; i<newSize; i++){
              for(int j=0; j<oldSize; j++){
                count = j;
                if(jBody["updates"][i] == acctUpdates["updates"][j]){
                  break;
                }
              }

              // if all acctUpdates checked with no match, then add new update at i
              if((count+1) == oldSize){
                acctUpdates["updates"].add( jBody["updates"][i].as<String>() );
              }
            }
          }
        }

        // clear jBody
        jBody.clear();

        // get length of body & respond to PUT
        int respLen = body.length();

        // print to serial
        Serial.print("\nSending: "); Serial.println(body);
        Serial.println();

        // respond
        svrClient.println("HTTP/1.1 200 OK");
        svrClient.println("Content-Type: application/json");
        svrClient.print("Content-Length: "); svrClient.println(respLen);
        svrClient.println("Connection: close");
        svrClient.println();
        svrClient.println(body);
      }
    }
  }
  
  // Terminate the connection
  svrClient.stop();

  return;
}

// =========================================================
// Functions - SETUP & LOOP
// =========================================================

// General layout of setup for production
// 0. Start serial connection for testing
// 1. Initialize file system/SD card & read in all existing config data
// 2. Initialize any time functionality
// 3. Setup ESP32 network

// SETUP - run once code -----------------------------------
void setup(){
  // 0. Start serial connection for testing
  Serial.begin(115200);
  delay(3000);          // wait 3 sec for serial port to connect
  Serial.println('\n');

  // 1. Initialize file system/SD card & read in all existing config data
  // FIX ME: THIS FUNCTION IS NOT COMPLETE. ADD FILE LOADING TO COMPLETE.
  init_system();

  // 2. Initialize any time functionality
  //setup_time();
  // commented out because it should only be called when connected to Wi-Fi

  // 3. Setup ESP32 network
  setupNet();
}

// General layout of loop for production - may be best to make each operation its own function
// 0. Run new day tasks - like time updates, purging logs older than 7 days, etc
// 1. If Wi-Fi is connected, poll AWS for updates, log changes
// 2. Listen for direct wireless connections, log changes
// 3. Check devState & alter device to match
// 4. Check & run devTimer functionality
// 5. Check & run devSched functionality

// Interrupts should be caused by physical use of the device
// If device is not locked, let the device state change, update devState, log change

// testing variables
String test_devInfo = "";
int counter = 0;

// LOOP - run forever code ---------------------------------
void loop(){
  // 0. Run new day tasks - like time updates, purging logs older than 7 days, etc

  // 1. If Wi-Fi is connected, poll AWS for updates, log changes
  main_polling();

  // 2. Listen for direct wireless connections, log changes
  main_listening();

  // QR testing - print init devInfo, then print devInfo each time it changes
  String temp = json2str(devInfo);
  if(test_devInfo == ""){
    test_devInfo = temp;
    Serial.println(test_devInfo);
  }
  else if(test_devInfo != temp){
    test_devInfo = temp;
    Serial.println(test_devInfo);
  }

  // REST PUT to AWS test - run if connected to Wi-Fi
  if(counter == 0){
    if(WiFi.status() == WL_CONNECTED){
      String response = rest_put("devInfo", devInfo, "aws");
      Serial.println(response);
      counter = 1;

      // update acctNet once connected and rest_put
      update_acctNet();
      String response2 = rest_put("acctNet", acctNet, "aws");
      //Serial.println(response2);
    }
  }

  // 3. Check devState & alter device to match
    // This can be used to update the devState JSON variable
    // Input: subid = updated dev_subid, v_percent = new change, lock = new lock state (0 = unlocked, 1 = locked)
    // void update_devState(int subid, int v_percent, int lock)

  // 4. Check & run devTimer functionality

  // 5. Check & run devSched functionality

  // Delay before looping - will remove after testing is done
  //Serial.println("Wait 5 seconds");
  delay(5000);
}
