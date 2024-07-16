// compile: gcc server.c -o server
// usage  : ./server port

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
 
int main(int argc, char *argv[]){

	int listenfd = 0, connfd = 0, cli_size, portno, on = 1, n = 0;
	struct sockaddr_in serv_addr, cli_addr;
	char sendBuff[1025];
	char recvBuff[1025];

	// test the number of command line arguments
	if(argc != 2){
		// error for too many or too few arguments
		printf("Usage: ./minor4svr <port>\n");
		exit(EXIT_FAILURE);
	}

	// setup socket using UDP over internet
	if ((listenfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1){
		printf("socket error\n");
		exit(EXIT_FAILURE);
	}

	// initialize serv_addr and buffers
	memset(&serv_addr, '0', sizeof(serv_addr));
	memset(sendBuff, '0', sizeof(sendBuff));
	memset(recvBuff, '0', sizeof(recvBuff));

	// assign connection values for serv_addr
	serv_addr.sin_family = AF_INET;    
	serv_addr.sin_addr.s_addr = htonl(INADDR_ANY); 
	portno = atoi(argv[1]);
	serv_addr.sin_port = htons(portno);

	// set socket options
	setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

	// try binding the socket
	if (bind(listenfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1){
		printf("bind error\n");
		exit(EXIT_FAILURE);
	}

	// try listening for connections - or not...because UDP doenst listen
	//if (listen(listenfd, 10) == -1){
	//	printf("listen error\n");
	//	exit(EXIT_FAILURE);
	//}

	// message sent if connection setup successful
	printf("[server]: Ready to accept data...\n");

	// loop indefinitely while trying to make connections
	while (1){
		cli_size = sizeof(cli_addr);

		// try making connections to clients
		//if ((connfd = accept(listenfd, (struct sockaddr *)&cli_addr, &cli_size)) == -1){
		//	printf("accept error\n");
		//	exit(EXIT_FAILURE);
		//}

		// try reading from client
		while ((n = read(listenfd, recvBuff, sizeof(recvBuff)-1)) > 0){
			recvBuff[n] = 0;

			// if PING message, print client message and send PONG response
			if(strcmp(recvBuff, "[client]: PING\n") == 0){
				if (fputs(recvBuff, stdout) == EOF){
					printf("fputs error\n");
				}
				strcpy(sendBuff, "[server]: PONG\n");
				write(connfd, sendBuff, strlen(sendBuff));
			}
			// else, print local dropped packet message
			else{
				printf("[server]: Dropped packet.\n");
			}
		}

		if (n < 0){
			printf("read error\n");
		}

		// close connection and wait before accepting another
		close(connfd);    
		sleep(1);
	} 
 
	return 0;
}
