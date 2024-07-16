/* Uses producer-consumer paradigm to show threading and mutex locks. */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NITEMS 10		// number of items in shared buffer

// shared variables
char shared_buffer[NITEMS];	// echo buffer
int shared_count;		// item count

pthread_mutex_t mutex;		// pthread mutex
pthread_cond_t cfull, cempt;	// pthread conditional var, full & empty buffer
unsigned int prod_index = 0; 	// producer index into shared buffer
unsigned int cons_index = 0; 	// consumer index into shard buffer

// function prototypes
void * producer(void *arg);
void * consumer(void *arg);

int main() 
{ 
	pthread_t prod_tid, cons_tid1, cons_tid2;

	// initialize pthread variables
	pthread_mutex_init(&mutex, NULL);
	pthread_cond_init(&cfull, NULL);
	pthread_cond_init(&cempt, NULL);
	
	// start producer thread
	pthread_create(&prod_tid, NULL, producer, NULL);

	// start consumer threads
	pthread_create(&cons_tid1, NULL, consumer, NULL);
	pthread_create(&cons_tid2, NULL, consumer, NULL);
	
	// wait for threads to finish
	pthread_join(prod_tid, NULL);
	pthread_join(cons_tid1, NULL);
	pthread_join(cons_tid2, NULL);
			
	// clean up
	pthread_mutex_destroy(&mutex);
	pthread_cond_destroy(&cfull);
	pthread_cond_destroy(&cempt);
	
	return 0;
}

// producer thread executes this function
void * producer(void *arg)
{
	char key;

	printf("Enter text for producer to read and consumer to print, use Ctrl-C to exit.\n\n");

	// this loop has the producer read data in from stdin and place the read data on the shared buffer
	while (1)
	{
		// read input key
		scanf("%c", &key);

		// this loop is used to poll the shared buffer to see if it is full:
		// -- if full, unlock and loop again to keep polling
		// -- if not full, keep locked and proceed to place character on shared buffer

		// acquire mutex lock
		pthread_mutex_lock(&mutex);

		// if buffer is full or at \n, signal and wait
		if ((shared_count == NITEMS) || (key == '\n')){
			pthread_cond_signal(&cempt);
			pthread_cond_wait(&cfull, &mutex);
		}
		else{
			// store key in shared buffer
			shared_buffer[prod_index] = key;

			// update shared count variable
			shared_count++;

			// update producer index
			if (prod_index == NITEMS - 1)
				prod_index = 0;
			else
				prod_index++;
		}

		// release mutex lock
		pthread_mutex_unlock(&mutex);
	}

	return NULL;
}

// consumer thread executes this function
void * consumer(void *arg)
{
	char key;

	long unsigned int id = (long unsigned int)pthread_self();

	// this loop has the consumer get data from the shared buffer and print to stdout
	while (1)
	{
		// this loop is used to poll the shared buffer to see if it is empty:
		// -- if empty, unlock and loop again to keep polling
		// -- if not empty, keep locked and proceed to get character from shared buffer

		// acquire mutex lock
		pthread_mutex_lock(&mutex);

		// if buffer is empty, signal and wait
		if (shared_count == 0){
			pthread_cond_signal(&cfull);
			pthread_cond_wait(&cempt, &mutex);
		}
		else{
			// read key from shared buffer
			key = shared_buffer[cons_index];
		
			// echo key
			printf("consumer %lu: %c\n", (long unsigned int) id, key);

			// update shared count variable
			shared_count--;

			// update consumer index
			if (cons_index == NITEMS - 1)
				cons_index = 0;
			else
				cons_index++;
		}

		// release mutex lock
		pthread_mutex_unlock(&mutex);
	}

	return NULL;
}
