// compile: gcc client.c -o client
// usage  : ./client hostname port

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <time.h>
 
int main(int argc, char *argv[]){

	int sockfd = 0, n = 0, portno, tal=0;
	char *host;
	char recvBuff[1025];
	char sendBuff[1025];
	struct sockaddr_in serv_addr;

	struct hostent *h;
	struct in_addr **addr_list;

	time_t t1, t2;
	double rtt=0, sum=0, min=0, max=0, avg;

	// test the number of command line arguments
	if(argc != 3){
		// error for too many or too few arguments
		printf("Usage: ./minor4svr <hostname> <port>\n");
		exit(EXIT_FAILURE);
	}

	// convert hostname to ip
	if ( (h = gethostbyname(argv[1]) ) == NULL){
		// get the host info
		herror("gethostbyname");
		return 1;
	}
	addr_list = (struct in_addr **) h->h_addr_list;
	strcpy(host, inet_ntoa(*addr_list[0]));

	// initialize buffers
	memset(recvBuff, '0', sizeof(recvBuff));
	memset(sendBuff, '0', sizeof(sendBuff));

	// setup socket using UDP over internet
	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0){
		printf("socket error\n");
		exit(EXIT_FAILURE);
	}

	// assign connection values for serv_addr
	serv_addr.sin_family = AF_INET;
	portno = atoi(argv[2]);
	serv_addr.sin_port = htons(portno);
	serv_addr.sin_addr.s_addr = inet_addr(host);

	// try connecting to the server
	if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0){
		printf("connect error\n");
		exit(EXIT_FAILURE);
	}

	// PING the server x10
	for(int i=1; i<11; i++){
		// get current time for RTT
		t1 = time(NULL);

		// communicate with the server
		strcpy(sendBuff, "[client]: PING\n");
		write(sockfd, sendBuff, strlen(sendBuff));

		// try to receive response PONG
		if(strcmp(recvBuff, "[server]: PONG\n") == 0){		//if received
			// get current time for RTT
			t2 = time(NULL);

			// calculate the RTT in ms
			rtt = (difftime(t1, t2) / 1000);

			// print single ping report
			printf("%d: Sent... RTT=%f ms\n", i, rtt);

			// tally successful pings
			tal++;

			// add current RTT to running sum for average calc
			sum += rtt;

			// calc if current RTT is min or max
			if(tal == 1){
				min = rtt;
				max = rtt;
			}
			else{
				if(rtt < min){
					min = rtt;
				}
				else if(rtt > max){
					max = rtt;
				}
			}
		}
		else{								// not received
			printf("%d: Sent... Timed Out\n", i);
		}
	}

	// calc PING report
	avg = sum / tal;

	// output report
	printf("10 pkts xmited, %d pkts rcvd, %d%% pkt loss", tal, (tal*10));
	printf("min: %f ms, max: %f ms, avg: %f ms", min, max, avg);

	// try reading from server
	while ((n = read(sockfd, recvBuff, sizeof(recvBuff)-1)) > 0){
		recvBuff[n] = 0;
		if (fputs(recvBuff, stdout) == EOF){
			printf("fputs error\n");
		}
	}
 
	if (n < 0){
		printf("read error\n");
	}
 
	return 0;
}
