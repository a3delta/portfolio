#include "region.h"
#include <iostream>
#include <string>
#include <fstream>
#include <list>
#include <bits/stdc++.h> 

//CLASS FUNCTION DEFINITIONS

Region::Region(string *f, int lCount){
	//copy over values from config file
	infectedArea = stoi(f[3]);
	infectiousPeriod = stoi(f[4]);
	contactRate = stoi(f[5]);
	vaccineNumber = stoi(f[6]);
	mSize = lCount;
	
	
	//oh boy let's assing populations 
	ifstream in;	//file stream input
	string temp;	//for string manipulation
	
	//open file
	in.open(f[0], ios::in);
	
	//resize vector
	populations.resize(lCount);
	
	//cut off first 2 digits of each string and assign values to the populations vector
	for (int i = 0; i < lCount; i++){
		getline(in, temp);
		if (i < 9){
			temp.erase(0, 2);
		} else if (i < 99){
			temp.erase(0, 3);
		} else if (i < 999){
			temp.erase(0, 4);
		} else {
			temp.erase(0, 4);
		}

		
		//assign value
		populations.at(i) = stoi(temp);
	}

}



//ADJACENY CHECKS
//create adjacency matrix (nested vectors in this case)
void Region::fillAdjacenyMatrix(string* f){
	//resize matrix
	adjMatrix.resize(mSize);
	
	//fill adjMatrix with adjacencies
	for (int i = 0; i < mSize; i++){
		for (int j = 0; j < mSize; j++){
			if ((i+1) < 10){
				if (f[i+1].at((2*(j+1))) == '1'){
					adjMatrix[i].push_back(j+1);
				}
			} else {
				if (f[i+1].at((2*(j+1))+1) == '1'){
					adjMatrix[i].push_back(j+1);
				}
			}
		}
	}
}


//check if a is adjacent to b
bool Region::adjacenyCheckSpecific(int a, int b){
	//variable
	bool validity = false;

	//check adjMatrix
	for(int i=0; i<adjMatrix[a-1].size(); i++){
		if( (adjMatrix[a-1][i] == b) && (a != b) ){
			validity = true;
			i = adjMatrix[a-1].size();
		}
	}

	return validity;
}


//CENTRALITY
int Region::distanceNumber(int a, int b){
	int d = 1;			//default distance is 1
	list<int> clevel;	//current level in tree, check this one
	list<int> nlevel;	//next level in tree, to track distance better
	vector<int> vis;	//to prevent repeat adj checks

	//add a to check list
	clevel.push_back(a);

	//loop through check list until empty
	while(clevel.size() > 0){
		//add clevel.front() to vis
		vis.push_back(clevel.front());

		if(nlevel.size() == 0){

			//determine new nlevel
			for(list<int>::iterator it=clevel.begin(); it != clevel.end(); ++it){
				//add adjacents to nlevel
				for(int i=0; i<getAdjCountAt(*it); i++){
					nlevel.push_back(getAdjAt(*it, i));
				}
			}
			//remove any visited and duplicates and sort
			nlevel.sort();
			nlevel.unique();
			for(int i=0; i<vis.size(); i++){
				nlevel.remove(vis[i]);
			}

		}

		//check if front is adjacent to b
		if(adjacenyCheckSpecific(clevel.front(), b)){
			//empty clevel and return d
			clevel.clear();
		}
		else{
			//pop from front of list, dec counter
			clevel.pop_front();
			//if clevel.size() == 0, and nlevel doesnt
			if( (clevel.size() == 0) && (nlevel.size() != 0) ){
				//transfer nlevel to clevel
				for(int i=0; nlevel.size() != 0; i++){
					clevel.push_back(nlevel.front());
					nlevel.pop_front();
				}
				//increment distance
				d++;
			}
		}

	}

	return d;
}

//closeness centrality
double Region::getCCentrality(int area){
	//variables
	double runningTotal = 0;

	for (int i = 0; i < mSize; i++){
		//dont check distance from area to itself
		if(area != (i+1)){
			runningTotal += distanceNumber(area, (i+1));
		}
	}

	return (runningTotal/(mSize-1));
}


//PRINT FUNCTIONS
void Region::printAllA(){
	for (int i = 0; i < adjMatrix.size(); i++){
		//show what value is processed
		cout << i+1 << ": ";
		for (int j =0; j<adjMatrix[i].size(); j++){
			cout << adjMatrix[i][j] << " ";
		}
		cout << endl;
	}
	cout << endl;
	
}

void Region::printPopulations(){
	//loop through and print pops
	for (int i = 0; i < mSize; i++){
		//show what value is processed
		cout << i+1 << " ";
		//print pop
		cout << populations.at(i) << endl;
	}
cout << endl;
}



//OTHER FUNCTION DEFINITIONS

//Function to validate config file input
int validateConfig(string fname, string* f){
    int val;        //validity value - 1/0 = T/F
    int len;        //string length for string manipulation
    string temp;    //temp for string comparisons
    ifstream in;    //file stream input

    //variables for expected file content comparisons
    string expected[] = {"Population","Region", "", "Infected Area", "Infectious Period", "Contact Rate", "Number of Vaccines"};
    int expLen[] = {10, 6, 0, 13, 17, 12, 18};  //lengths of expected[] elements

    //pull last 4 char (file type) from input for validation
    len = fname.length();
    for(int i=4; i>0; i--){
        temp += fname[len - i];
    }

    //if file is .txt, check further for validity
    if(temp == ".txt"){

        //open file, read in first 3 lines, close file
        in.open(fname, ios::in);
        for(int i=0; i<7; i++){
            getline(in, f[i]);
        }
        in.close();

        //check file contents line by line
        for(int i=0; i<7; i++){

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
				i = 7;
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
    for(int i=0; i<=cnt; i++){
        getline(in, f[i]);
    }
    in.close();

    return;
}
