#include "dataMan.h"
#include <iostream>
#include <string>
#include <fstream>

//CLASS FUNCTION DEFINITIONS

//Public contructor function for Cell class-------------------------CELL--------------------------------
Cell::Cell(){
    zone = ' ';
    x = 0;
    y = 0;
    pop = 0;
    apop = 0;
    poll = 0;
    updated = false;
}

//Public function to set zoning value
void Cell::setZone(char c){
    zone = c;
    return;
}

//Public function to set x,y (a,b) coordinates
void Cell::setCoord(int a, int b){
    x = a;
    y = b;
    return;
}

//Public function to set updated value
void Cell::setUpdated(bool b){
    updated = b;
    return;
}

//Public function to increase cell population by 1
void Cell::incPop(){
    pop += 1;
    return;
}

void Cell::incAPop(){
    apop += 1;
    return;
}

//Public function to set cell pollution value
void Cell::setPoll(int p){
    poll = p;
    return;
}

//Public function to return cell zoning info
char Cell::getZone(){
    return zone;
}

//Public function to return cell x coordinate
int Cell::getx(){
    return x;
}

//Public function to return cell y coordinate
int Cell::gety(){
    return y;
}

//Public function to return cell population value
int Cell::getPop(){
    return pop;
}

//Public function to return the cell's total adjacent population
int Cell::getAPop(){
    return apop;
}

//Public function to return cell pollultion value
int Cell::getPoll(){
    return poll;
}

//Public function to return the cell updated value
bool Cell::getUpdate(){
    return updated;
}

//Public function to clone cell population
void Cell::clonePop(int p){
    pop = p;
    return;
}

//Public function to clone cell pollution
void Cell:: clonePoll(int p){
    poll = p;
    return;
}

//Public contructor function for Region class-----------------REGION-------------------------------
Region::Region(int cnt, string* d){
    int z = (d[0].length() / 2) + 1;    //find xMax value
    int total;                          //for total num of zones
    int a = 0;                          //for independent incrementing
    int k = 0;                          //for correctly setting x coord

    //initialize region class variables
    xMax = z;
    yMax = cnt;
    workers = 0;
    goods = 0;
    listSize = 0;
	cellList = new int[listSize];
    cellList = nullptr;

    //determine the number of char in region
    total = xMax * yMax;

    //allocate memory for Cell* c
    c = new Cell[total];

    //assign zone values stored in d to c
    for(int i=0; i<yMax; i++){
        for(int j=0; j<d[0].length(); j++){
            if(d[i][j] != ','){

                //set cell zoning value
                c[a].setZone(d[i][j]);

                //set cell coordinates
                c[a].setCoord(k, i);

                //increment a to move to next cell and k to next x
                a++;
                k++;

            }
        }

        //once first x loop is done, reset k = 0
        k=0;
        
    }

}

//Public deconstructor function for Region class
Region::~Region(){
    //de-allocate memory from dynamic arrays
    delete[] cellList;
    delete[] c;
}

//Private function for finding adjacent cell bounds
void Region::adjBounds(int &aMin, int &aMax, int &bMin, int &bMax, int i){

    //find upper and lower bounds for adjacent x range
    //if adj x range is within matrix x range
    if(0 <= (c[i].getx() - 1) && xMax > (c[i].getx() + 1)){
        aMin = (c[i].getx() - 1);
        aMax = (c[i].getx() + 1);
    }
    //else if adj x range is within min but not max
    else if(0 <= (c[i].getx() - 1)){
        aMin = (c[i].getx() - 1);
        aMax = (xMax - 1);
    }
    //else adj x range is within max but not min
    else{
        aMin = 0;
        aMax = (c[i].getx() + 1);
    }

    //find upper and lower bounds for adjacent y range
    //if adj y range is within matrix y range
    if(0 <= (c[i].gety() - 1) && yMax > (c[i].gety() + 1)){
        bMin = (c[i].gety() - 1);
        bMax = (c[i].gety() + 1);
    }
    //else if adj y range is within min but not max
    else if(0 <= (c[i].gety() - 1)){
        bMin = (c[i].gety() - 1);
        bMax = (yMax - 1);
    }
    //else adj y range is within max but not min
    else{
        bMin = 0;
        bMax = (c[i].gety() + 1);
    }

    return;
}

//Private function to increase the size of the cell list array
void Region::resizeList(int n){
    
    //create old array to shuffle data
	int* oldArr = new int[listSize];
	
	//pass cellList values to oldArr
	for(int i=0; i<listSize; i++){
		oldArr[i] = cellList[i];
	}

	//delete cellList and increase arrSize
	delete[] cellList;
	listSize += n;

	//reallocate memory to cellList
	cellList = new int[listSize];

	//pass old values back to cellList
	for(int i=0; i<(listSize - n); i++){
		cellList[i] = oldArr[i];
	}

    return;
}

//Private function to reset cellList array to 0 elements
void Region::resetList(){
    //delete cellList and set listSize to 0
    delete[] cellList;
    listSize = 0;

    //allocate size of 0 and assign null
    cellList = new int[listSize];
    cellList = nullptr;

    return;
}

//Public function to increase available worker count by 1
void Region::incWorkers(){
    workers += 1;
    return;
}

//Public function to decrease available worker count by a
void Region::decWorkers(int a){
    workers -= a;
    return;
}

//Public function to increase available goods count by 1
void Region::incGoods(){
    goods += 1;
    return;
}

//Public function to decrease available goods count by 1
void Region::decGoods(){
    goods -= 1;
    return;
}

//Public function to increase pollution with industrial population
//for parameter, pass in increment from external cell walk
void Region::incPoll(int inc){
    int axMin, axMax;       //for adjacent x range
    int ayMin, ayMax;       //for adjacent y range
    int ai;                 //for incrementing through adjacent
    int xdif;               //for incrementing through adjacent

    //find upper and lower bounds for adjacent x and y ranges
    adjBounds(axMin, axMax, ayMin, ayMax, inc);

    //set y difference for later increments
    //this is needed since the cells are stored in a 1d array
    xdif = ((axMax - axMin) + 1);

    //math to find first adjacent cell without looping all
    //this is needed since the cells are stored in a 1d array
    ai = (((ayMin + 1) * xMax) - (xMax - axMin));

    //increase the current cell's pollution = its population
    if( (c[inc].getPoll() < c[inc].getPop()) && (c[inc].getZone() == 'I') ){
        c[inc].setPoll(c[inc].getPop());
    }

    //loop through adjacent cells
    //loop through y values
    for(int i=ayMin; i<=ayMax; i++){
        //loop through x values
        for(int j=axMin; j<=axMax; j++){

            //if the cell pollution is less than the current cell pop
            //set adj cell poll = to current cell pop - 1
            if( c[ai].getPoll() < (c[inc].getPoll() - 1) ){
                c[ai].setPoll( (c[inc].getPoll() - 1) );
            }

            //increment through the adjacent cell x range
            ai++;

        }

        //increment through the adjacent cell y range
        ai += (xMax - xdif);

    }

    return;
}

//Public function to update all pollution values for entire region
void Region::updatePoll(){

    for(int i=0; i<cellCount(); i++){
        incPoll(i);
    }

    return;
}

//Public function that returns the highest pop for the given zoning z
//count tracks the number of cells with equally high zoning for prioritization
//last should be initialized to -1 wherever this function is called
int Region::getHiPop(char z, int &count, int last){
    int n = 0;      //stores the high population value

    //for each cell, if zone = z and pop >= n, n = pop and hic++
    for(int i=0; i<cellCount(); i++){
        if(c[i].getZone() == z){
            if( (c[i].getPop() > n) && ((c[i].getPop() < last) || (last == -1)) ){
                n = c[i].getPop();
                count = 1;
            }
            else if(c[i].getPop() == n){
                count++;
            }
        }
    }

    return n;       //return the highest population value
}

//Public function that returns the available workers count
int Region::getWorkers(){
    return workers;
}

//Public function that returns the available goods count
int Region::getGoods(){
    return goods;
}

//Public function that returns the max x value
int Region::getxMax(){
    return xMax;
}

//Public function that returns the max y value
int Region::getyMax(){
    return yMax;
}

//Public function that returns the max number of cells in the region
int Region::cellCount(){
    return (xMax * yMax);
}

//Public function that returns the size of cellList for population increases
int Region::cellListSize(){
    return listSize;
}

//Public function that returns the zoning value for a cell at the inc position
char Region::cellZone(int inc){
    return c[inc].getZone();
}

//Public function that returns the population of a cell at inc
int Region::cellPop(int inc){
    return c[inc].getPop();
}

//Public function that returns the updated value of a cell at inc
bool Region::cellUpdated(int inc){
    return c[inc].getUpdate();
}

//Public function that returns the value stored in cellList at inc
int Region::getListItem(int inc){
    return cellList[inc];
}

//Public function that returns true if there are adjacent powerlines
bool Region::byPower(int inc){
    int axMin, axMax;       //for adjacent x range
    int ayMin, ayMax;       //for adjacent y range
    int ai;                 //for incrementing through adjacent
    int xdif;               //for incrementing through adjacent

    //find upper and lower bounds for adjacent x and y ranges
    adjBounds(axMin, axMax, ayMin, ayMax, inc);

    //set y difference for later increments
    //this is needed since the cells are stored in a 1d array
    xdif = ((axMax - axMin) + 1);

    //math to find first adjacent cell without looping all
    //this is needed since the cells are stored in a 1d array
    ai = (((ayMin + 1) * xMax) - (xMax - axMin));

    //loop through adjacent cells
    //loop through y values
    for(int i=ayMin; i<=ayMax; i++){
        //loop through x values
        for(int j=axMin; j<=axMax; j++){

            //if the cell == 'T' or '#', then return true
            if(c[ai].getZone() == 'T' || c[ai].getZone() == '#'){
                //verify that adj cell (ai) isnt the current (inc)
                if(ai != inc){
                    return true;
                }
            }

            //increment through the adjacent cell x range
            ai++;

        }

        //increment through the adjacent cell y range
        ai += (xMax - xdif);

    }

    return false;
}

//Public function that returns the num n of adj cells with pop p or higher
int Region::adjPop(int p, int inc){
    int axMin, axMax;       //for adjacent x range
    int ayMin, ayMax;       //for adjacent y range
    int ai;                 //for incrementing through adjacent
    int xdif;               //for incrementing through adjacent
    int n=0;                //for counting adj cells of pop p+

    //find upper and lower bounds for adjacent x and y ranges
    adjBounds(axMin, axMax, ayMin, ayMax, inc);

    //set y difference for later increments
    //this is needed since the cells are stored in a 1d array
    xdif = ((axMax - axMin) + 1);

    //math to find first adjacent cell without looping all
    //this is needed since the cells are stored in a 1d array
    ai = (((ayMin + 1) * xMax) - (xMax - axMin));

    //loop through adjacent cells
    //loop through y values
    for(int i=ayMin; i<=ayMax; i++){
        //loop through x values
        for(int j=axMin; j<=axMax; j++){

            //if the adj cell has been updated, check its population - 1
            if(c[ai].getUpdate()){
                //if the adj cell pop - 1 is >= p and isnt currnet cell (inc), increment n
                if( ((c[ai].getPop() - 1) >= p) && (ai != inc) ){
                    n++;
                }
            }
            //else, check its population as is
            else{
                //if the adj cell pop is >= p and isnt currnet cell (inc), increment n
                if( (c[ai].getPop() >= p) && (ai != inc) ){
                    n++;
                }
            }

            //increment through the adjacent cell x range
            ai++;

        }

        //increment through the adjacent cell y range
        ai += (xMax - xdif);

    }

    return n;
}

//Public function to increase the apop value for adjacent cells when pop is increased
void Region::incAdjPop(int inc){
    int axMin, axMax;       //for adjacent x range
    int ayMin, ayMax;       //for adjacent y range
    int ai;                 //for incrementing through adjacent
    int xdif;               //for incrementing through adjacent

    //find upper and lower bounds for adjacent x and y ranges
    adjBounds(axMin, axMax, ayMin, ayMax, inc);

    //set y difference for later increments
    //this is needed since the cells are stored in a 1d array
    xdif = ((axMax - axMin) + 1);

    //math to find first adjacent cell without looping all
    //this is needed since the cells are stored in a 1d array
    ai = (((ayMin + 1) * xMax) - (xMax - axMin));

    //loop through adjacent cells
    //loop through y values
    for(int i=ayMin; i<=ayMax; i++){
        //loop through x values
        for(int j=axMin; j<=axMax; j++){
            //if c[ai] is not the current cell
            if(ai != inc){
                //if the adj cell is zoned as R, I, or C, increase apop
                if( (c[ai].getZone() == 'R') || (c[ai].getZone() == 'I') || (c[ai].getZone() == 'C') ){
                    //increase apop for the adjacent cell by 1
                    c[ai].incAPop();
                }
            }

            //increment through the adjacent cell x range
            ai++;
        }

        //increment through the adjacent cell y range
        ai += (xMax - xdif);

    }

    return;
}

//Public function to reset the updated value for all cells
//Call when finished increasing pop for the current time step
void Region::resetUpdate(){
    for(int i=0; i<cellCount(); i++){
        //if updated = true, reset it - comparing rather than writing all
        if(c[i].getUpdate()){
            c[i].setUpdated(false);
        }
    }
}

//Public function to prioritize a zoning type's cells for pop increases
void Region::prioritizeCells(char z){
    int m = 0;      //to aid in filling cellList array
    int o;          //to count the number of cells with equally high pop
    int p = -1;     //to track the highest pop for the given zone
    int* temp1;     //to track the cells with the highest pop
    int* temp2;     //to aid in sorting the values in temp1

    //reset the list
    resetList();

    //loop until all cells of zone z have been prioritized and added to cellList
    while(p != 0){

        //STEP 1: GET CELLS WITH HIGHEST POPULATION

        //initialize o to 0 before passing to getHiPop()
        o = 0;
        m = 0;

        //find the highest pop for the given zone
        p = getHiPop(z, o, p);

        //manage array sizes
        temp1 = new int[o];
        temp2 = new int[o];
        resizeList(o);

        //loop through all cells to find cells of zone z and pop p
        for(int i=0; i<cellCount(); i++){
            if( (c[i].getZone() == z) && (c[i].getPop() == p) ){
                //add zone address to temp
                temp1[m] = i;
                m++;
            }
        }

        //STEP 2: SORT CELLS BY HIGHEST ADJACENT POP

        //set m to o for tracking sorting
        m = o;

        while(m != 0){
            for(int i=0; i<o; i++){
                //if not on the last element
                if((i+1) < o){
                    //if temp[i] adjPop is less than temp[i+1] adjPop
                    if( c[temp1[i]].getAPop() < c[temp1[i+1]].getAPop() ){
                        //sort these elements of the array
                        temp2[i] = temp1[i+1];
                        temp2[i+1] = temp1[i];
                        //add in the preceding elements if any
                        if(i > 0){
                            for(int j=0; j<i; j++){
                                temp2[j] = temp1[j];
                            }
                        }
                        //add in the succeeding elements if any
                        if((i+2) < o){
                            for(int j=(i+2); j<o; j++){
                                temp2[j] = temp1[j];
                            }
                        }
                        //copy temp2 elements back to temp1 in new order
                        for(int k=0; k<o; k++){
                            temp1[k] = temp2[k];
                        }
                    }
                    //else, these two are sorted, move on
                }
            }

            //once the for loop exits, decrement m
            //once m = 0, the array should be sorted
            m--;
        }

        //add each value in the sorted array into cellList
        for(int i=0; i<o; i++){
            cellList[listSize - (o - i)] = temp1[i];
        }

        //reinitialize the sorted temp array before the next loop
        delete[] temp1;
        delete[] temp2;
        temp1 = nullptr;
        temp2 = nullptr;

    }

    return;
}

//Public function to increase population of a certain cell
//Logic will be affected by how incCellPop() is called
//cellPriority() will affect this
void Region::incCellPop(int inc){

    //increase pop by 1 and mark as updated
    c[inc].incPop();
    c[inc].setUpdated(true);

    //increase apop for adjacent cells by 1
    incAdjPop(inc);

    //if zone is of type 'C'
    //decrease workers and goods by 1
    if(c[inc].getZone() == 'C'){
        decWorkers(1);
        decGoods();
    }
    //else if zone is of type 'I'
    //decrease workers by 2, increase goods by 1, increase poll
    else if(c[inc].getZone() == 'I'){
        decWorkers(2);
        incGoods();
    }
    //else if zone is of type 'R'
    //increase workers by 1
    else if(c[inc].getZone() == 'R'){
        incWorkers();
    }

    return;
}

//Public function to print region state
void Region::printRegState(){
    int a=0;        //for independent increments through cells

    for(int i=0; i<yMax; i++){

        //if y == 0, print an upper region wall
        if(i == 0){
            for(int k=0; k < ((xMax * 2) + 2); k++){
                cout << "-";
            }
            cout << endl;
        }

        for(int j=0; j<xMax; j++){

            //if x == 0, print a left region wall
            if(j == 0){
                cout << '|';
            }

            //if getPop() == 0, print the zone value and a space
            if(c[a].getPop() == 0){
                cout << c[a].getZone() << ' ';
            }
            //else, print the zone population value and a space
            else{
                cout << c[a].getPop() << ' ';
            }

            //increment a to move to the next cell
            a++;

            //else if x == (xMax - 1), print a right region wall and endl
            if(j == (xMax - 1)){
                cout << '|' << endl;
            }

        }

        //if y == (yMax - 1), print a lower region wall
        if(i == (yMax - 1)){
            for(int k=0; k < ((xMax * 2) + 2); k++){
                cout << "-";
            }
            cout << endl;
        }

    }

    return;
}

//Public function to print pollution state
void Region::printPollState(){
    int a=0;        //for independent increments through cells

    for(int i=0; i<yMax; i++){

        //if y == 0, print an upper region wall
        if(i == 0){
            for(int k=0; k < ((xMax * 2) + 2); k++){
                cout << "-";
            }
            cout << endl;
        }

        for(int j=0; j<xMax; j++){

            //if x == 0, print a left region wall
            if(j == 0){
                cout << '|';
            }

            //print the zone value and a space, increment a
            cout << c[a].getPoll() << ' ';
            a++;

            //else if x == (xMax - 1), print a right region wall and endl
            if(j == (xMax - 1)){
                cout << '|' << endl;
            }

        }

        //if y == (yMax - 1), print a lower region wall
        if(i == (yMax - 1)){
            for(int k=0; k < ((xMax * 2) + 2); k++){
                cout << "-";
            }
            cout << endl;
        }

    }

    //add an endl after the completed region state
    cout << endl;

    return;
}

//Public function to print region analysis
//Parameters are for min x,y (a1,b1) and max x,y (a2,b2) coords
void Region::printAnalysis(int a1, int b1, int a2, int b2){
    int resPop=0, indPop=0, comPop=0;   //for zone pop counts
    int pollTotal=0;                    //for pollution count
    int w=0;                            //for walking cells

    //navigate through cells - outer loop does rows, inner loop does columns
    for(int i=b1; i<b2; i++){
        for(int j=a1; j<a2; j++){

            //switch statement to count pop per zoning
            switch(c[w].getZone()){
                case 'R':
                    resPop += c[w].getPop();
                    break;
                case 'I':
                    indPop += c[w].getPop();
                    break;
                case 'C':
                    comPop += c[w].getPop();
                    break;
            }

            //increase pollTotal for every cells pollution count
            pollTotal += c[w].getPoll();

            //increment w to walk to the next cell
            w++;

        }
    }

    //print out the results of the analysis
    cout << "The total populations for the requested area are:" << endl;
    cout << "Residential: " << resPop << endl;
    cout << "Industrial: " << indPop << endl;
    cout << "Commercial: " << comPop << endl;
    cout << "The total amount of pollution for the requested area is ";
    cout << pollTotal << " units." << endl;

    return;
}

//Public function that validates user-input x,y coords
int Region::validateCoord(int a1, int b1, int a2, int b2){
    if((a1 < 0) || (a1 > xMax)){        //if x1 is out of bounds, return false
        return 0;
    }
    else if((b1 < 0) || (b1 > yMax)){   //if y1 is out of bounds, return false
        return 0;
    }
    else if((a2 < 0) || (a2 > xMax)){   //if x2 is out of bounds, return false
        return 0;
    }
    else if((b2 < 0) || (b2 > yMax)){   //if y2 is out of bounds, return false
        return 0;
    }
    else if((a1 > a2) || (b1 > b2)){    //if x1 > x2 or y1 > y2, return false
        return 0;
    }

    //default to true if none of the above conditions are met
    return 1;
}

//Public function that creates a region clone for comparisons to previous state
void Region::cloneRegion(int &prevW, int &prevG, int* prevP){
    int max = (xMax * yMax);

    //clone worker and goods counts
    prevW = workers;
    prevG = goods;

    //loop through cells and clone pop and poll
    for(int i=0; i<max; i++){
        prevP[i] = c[i].getPop();
    }

    return;
}

//Public function that returns true if current region state == previous
bool Region::isEqual(int prevW, int prevG, int prevP[]){
    int max = cellCount();      //pull the total number of cells to iterate

    //compare region workers and goods, if = to prev, continue, else return false
    if(workers != prevW){
        return false;
    }
    else if(goods != prevG){
        return false;
    }
    //iterate through all cells and compare population
    for(int i=0; i<max; i++){
        if(c[i].getPop() != prevP[i]){
            return false;
        }
    }

    //if all comparisons are equal, return true
    return true;
}

//OTHER FUNCTION DEFINITIONS

//Function to validate config file input
int validateConfig(string fname, string* f){
    int val;        //validity value - 1/0 = T/F
    int len;        //string length for string manipulation
    string temp;    //temp for string comparisons
    ifstream in;    //file stream input

    //variables for expected file content comparisons
    string expected[] = {"Region Layout","Time Limit","Refresh Rate"};
    int expLen[] = {13,10,12};  //lengths of expected[] elements

    //pull last 4 char (file type) from input for validation
    len = fname.length();
    for(int i=4; i>0; i--){
        temp += fname[len - i];
    }

    //if file is .txt, check further for validity
    if(temp == ".txt"){

        //open file, read in first 3 lines, close file
        in.open(fname, ios::in);
        for(int i=0; i<3; i++){
            getline(in, f[i]);
        }
        in.close();

        //check file contents line by line
        for(int i=0; i<3; i++){

            //pull the expected number of char before the ":"
            //reinitialize sTemp
            temp = "";
            for(int j=0; j<expLen[i]; j++){
                temp += f[i][j];
            }

            //if pulled char != expected, error and try again
            //exits outer for loop before checking further lines
            if(temp != expected[i]){
                cout << "Invalid configuration file input." << endl;
                val = 0;
                i = 3;
            }
            //else, line is valid, continue outer for loop
            //if all 3 lines are valid, while loop will exit
            else{
                val = 1;

                //trim identifying info out of strings
                temp = "";
                len = f[i].length() - expLen[i];
                for(int j=1; j<len; j++){
                    temp += f[i][expLen[i] + j];
                }
                f[i] = temp;
            }
        }
    }
    //else, config file name is invalid, error and loop
    else{
        cout << "Invalid configuration file input." << endl;
        val = 0;
    }

    return val;
}

//Function to find line count in region csv for allocation
int countRegionCSV(string fname){
    int count=0;    //for counting lines
    ifstream in;    //file stream input
    string temp;    //for line input

    //open file, read in lines until EOF, add to count, close
    in.open(fname, ios::in);
    for(int i=0; in.eof() != true; i++){
        getline(in, temp);
        count++;
    }
    in.close();

    return count - 1;
}

//Function to open region csv and pull contents
void openRegionCSV(string fname, int cnt, string* f){
    ifstream in;    //file stream input
    string temp;    //for string manipulation

    //open file, read in lines until EOF, close file
    in.open(fname, ios::in);
    for(int i=0; i<cnt; i++){
        getline(in, f[i]);
    }
    in.close();

    return;
}
