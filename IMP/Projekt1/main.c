/*
 * Copyright (c) 2015, Freescale Semiconductor, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * o Redistributions of source code must retain the above copyright notice, this list
 *   of conditions and the following disclaimer.
 *
 * o Redistributions in binary form must reproduce the above copyright notice, this
 *   list of conditions and the following disclaimer in the documentation and/or
 *   other materials provided with the distribution.
 *
 * o Neither the name of Freescale Semiconductor, Inc. nor the names of its
 *   contributors may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "MK60D10.h"
#include <stdio.h>

#define    DWT_CTRL       *(volatile uint32_t *)0xE0001000     //control register
#define    DWT_CYCCNT     *(volatile uint32_t *)0xE0001004     //cycle count register
#define    DWT_SLEEPCNT   *(volatile uint32_t *)0xE0001010	   //sleep count register
#define    DWT_EXCCNT     *(volatile uint32_t *)0xE000100C	   //exception count register
#define    DWT_LSUCNT     *(volatile uint32_t *)0xE0001014	   //LSU count register
#define    DWT_FOLDCNT    *(volatile uint32_t *)0xE0001018	   //folded instruction count register
#define    DWT_CPICNT     *(volatile uint32_t *)0xE0001018	   //folded instruction count register

uint32_t  startCycle = 0; //start number of cycles
uint32_t  stopCycle; //stop number of cycles
uint32_t  cycles; //number of cycles
uint32_t minCycle; //minimum
uint32_t maxCycle; //maximum
uint32_t avgCycle; //average
uint32_t avgCycleSum; //sum for average

uint32_t  startSleep = 0; //start number of sleep cycles
uint32_t  stopSleep; //stop number of sleep cycles
uint32_t  sleeps; //number of sleep cycles
uint32_t minSleep; //minimum
uint32_t maxSleep; //maximum
uint32_t avgSleep; //average
uint32_t avgSleepSum; //sum for average

uint32_t  startExcep = 0; //start number of exception cycles
uint32_t  stopExcep; //stop number of exception cycles
uint32_t  exceptions; //number of exception cycles
uint32_t minExcep; //minimum
uint32_t maxExcep; //maximum
uint32_t avgExcep; //average
uint32_t avgExcepSum; //sum for average

uint32_t  startLSU = 0; //start number of LSU cycles
uint32_t  stopLSU; //stop number of LSU cycles
uint32_t  LSUs; //number of LSU cycles
uint32_t minLSU; //minimum
uint32_t maxLSU; //maximum
uint32_t avgLSU; //average
uint32_t avgLSUSum; //sum for average

uint32_t  startFold = 0; //start number of fold cycles
uint32_t  stopFold; //stop number of fold cycles
uint32_t  Folds; //number of fold cycles
uint32_t minFold; //minimum
uint32_t maxFold; //maximum
uint32_t avgFold; //average
uint32_t avgFoldSum; //sum for average

uint32_t  startInstr = 0; //start number of Instruction cycles
uint32_t  stopInstr; //stop number of Instruction cycles
uint32_t  Instrs; //number of Instruction cycles
uint32_t minInstr; //minimum
uint32_t maxInstr; //maximum
uint32_t avgInstr; //average
uint32_t avgInstrSum; //sum for average

uint32_t maxRepetitions = 10; //for counter


void initMCU()
{
	MCG->C4 |= ( MCG_C4_DMX32_MASK | MCG_C4_DRST_DRS(0x01) );
	SIM->CLKDIV1 |= SIM_CLKDIV1_OUTDIV1(0x00);
	WDOG_STCTRLH &= ~WDOG_STCTRLH_WDOGEN_MASK;

}


/**
 * Initialization of DWT
 */
void initDWT()
{
	//enable cycle counter
	//CYCCNTENA, bit[0]
	DWT_CTRL |= 1;

	//check if cycle counter is supported
	//NOCYCCNT, bit[25]
	if ((DWT_CTRL & (1 << 25)) != 0)
	{
		printf("Cycle counter is not supported\n");
	}

	//check if profiling counter is supported
	//NOPRFCNT, bit[24]
	if ((DWT_CTRL & (1 << 24)) != 0)
	{
		printf("Profiling counter is not supported\n");
	}

	DWT_CYCCNT = 0; //reset cycle counter
	DWT_CTRL |= 1 << 21;//reset fold counter FOLDEVTENA, bit[21]
	DWT_CTRL |= 1 << 20;//reset LSU counter LSUEVTENA, bit[20]
	DWT_CTRL |= 1 << 19;//reset sleep counter SLEEPEVTENA, bit[19]
	DWT_CTRL |= 1 << 18;//reset exception counter EXCEVTENA, bit[18]
	DWT_CTRL |= 1 << 17;//reset instruction counter CPIEVTENA, bit[17]
}


/**
 * Start of counting
 */
void startCounter()
{
	DWT_CYCCNT = 0; //reset cycle counter
	startCycle = DWT_CYCCNT; //number of cycles at the start of counting

	DWT_CTRL |= 1 << 21;//reset fold counter FOLDEVTENA, bit[21]
	startExcep = DWT_FOLDCNT;//number of folds at the start of counting

	DWT_CTRL |= 1 << 20;//reset LSU  counter LSUEVTENA, bit[20]
	startExcep = DWT_LSUCNT;//number of LSUs at the start of counting

	DWT_CTRL |= 1 << 19;//reset sleep counter SLEEPEVTENA, bit[19]
	startSleep = DWT_SLEEPCNT;//number of sleeps at the start of counting

	DWT_CTRL |= 1 << 18;//reset exception counter EXCEVTENA, bit[18]
	startExcep = DWT_EXCCNT;//number of exceptions at the start of counting

	DWT_CTRL |= 1 << 17;//reset instruction counter CPIEVTENA, bit[17]
	startExcep = DWT_CPICNT;//number of instructions at the start of counting

}


/**
 * End of counting
 */
void stopCounter()
{
	//stop counters
	stopCycle = DWT_CYCCNT; //number of cycles at the end of counting
	stopSleep = DWT_SLEEPCNT; //number of sleeps at the end of counting
	stopExcep = DWT_EXCCNT; //number of exceptions at the end of counting
	stopLSU = DWT_LSUCNT; //number of LSUs at the end of counting
	stopFold = DWT_FOLDCNT; //number of folds at the end of counting
	stopInstr = DWT_CPICNT; //number of instructions at the end of counting

	//CYCLES----------------------------------------------------------------
	cycles = stopCycle - startCycle;

	//minimum
	if (maxCycle < cycles) {
	    maxCycle = cycles;
	}
	//maximum
	if (minCycle > cycles) {
	    minCycle = cycles;
	}
	//average sum
	avgCycleSum = avgCycleSum + cycles;
	//-----------------------------------------------------------------------

	//EXCEPS----------------------------------------------------------------
	exceptions = stopExcep - startExcep;

	//minimum
	if (maxExcep < exceptions) {
		maxExcep = exceptions;
	}
	//maximum
	if (minExcep > exceptions) {
		minExcep = exceptions;
	}
	//average sum
	avgExcepSum = avgExcepSum + exceptions;
	//-----------------------------------------------------------------------

	//SLEEPS----------------------------------------------------------------
	sleeps = stopSleep - startSleep;

	//minimum
	if (maxSleep < sleeps) {
		maxSleep = sleeps;
	}
	//maximum
	if (minSleep > sleeps) {
		minSleep = sleeps;
	}
	//average sum
	avgSleepSum = avgSleepSum + sleeps;
	//-----------------------------------------------------------------------

	//LSUs----------------------------------------------------------------
	LSUs = stopLSU - startLSU;

	//minimum
	if (maxLSU < LSUs) {
		maxLSU = LSUs;
	}
	//maximum
	if (minLSU > LSUs) {
		minLSU = LSUs;
	}
	//average sum
	avgLSUSum = avgLSUSum + LSUs;
	//-----------------------------------------------------------------------

	//Folds----------------------------------------------------------------
	Folds = stopFold - startFold;

	//minimum
	if (maxFold < Folds) {
		maxFold = Folds;
	}
	//maximum
	if (minFold > Folds) {
		minFold = Folds;
	}
	//average sum
	avgFoldSum = avgFoldSum + Folds;
	//-----------------------------------------------------------------------

	//Instructions----------------------------------------------------------------
	Instrs = stopInstr - startInstr;

	//minimum
	if (maxInstr < Instrs) {
		maxInstr = Instrs;
	}
	//maximum
	if (minInstr > Instrs) {
		minInstr = Instrs;
	}
	//average sum
	avgInstrSum = avgInstrSum + Instrs;
	//-----------------------------------------------------------------------


}

void printCounter()
{
	avgCycle = avgCycleSum / maxRepetitions ;
	//cycles
	printf("Number of cycles : %d\n", cycles);
	printf("Maximum of cycles : %d\n", maxCycle);
	printf("Minimum of cycles : %d\n", minCycle);
	printf("Average of cycles : %d\n", avgCycle);

	avgSleep = avgSleepSum / maxRepetitions ;
	//sleeps
	printf("Number of sleeps : %d\n", sleeps);
	printf("Maximum of sleeps : %d\n", maxSleep);
	printf("Minimum of sleeps : %d\n", minSleep);
	printf("Average of sleeps : %d\n", avgSleep);

	avgExcep = avgExcepSum / maxRepetitions ;
	//exceptions
	printf("Number of exceptions : %d\n", exceptions);
	printf("Maximum of exceptions : %d\n", maxExcep);
	printf("Minimum of exceptions : %d\n", minExcep);
	printf("Average of exceptions : %d\n", avgExcep);

	avgLSU = avgLSUSum / maxRepetitions ;
	//LSUs
	printf("Number of LSUs : %d\n", LSUs);
	printf("Maximum of LSUs : %d\n", maxLSU);
	printf("Minimum of LSUs : %d\n", minLSU);
	printf("Average of LSUs : %d\n", avgLSU);

	avgFold = avgFoldSum / maxRepetitions ;
	//Folds
	printf("Number of Folds : %d\n", Folds);
	printf("Maximum of Folds : %d\n", maxFold);
	printf("Minimum of Folds : %d\n", minFold);
	printf("Average of Folds : %d\n", avgFold);

	avgInstr = avgInstrSum / maxRepetitions ;
	//Folds
	printf("Number of Instructions : %d\n", Instrs);
	printf("Maximum of Instructions : %d\n", maxInstr);
	printf("Minimum of Instructions : %d\n", minInstr);
	printf("Average of Instructions : %d\n", avgInstr);
}


/**
 * Clear all variables before next use
 */
void clearCounter()
{
	//cycles
	startCycle = 0;
	stopCycle = 0;
	cycles = 0;
	minCycle = 0;
	maxCycle = 0;
	avgCycle = 0;
	avgCycleSum = 0;

	//sleeps
	startSleep = 0;
	stopSleep= 0;
	sleeps = 0;
	minSleep = 0;
	maxSleep = 0;
	avgSleep = 0;
	avgSleepSum = 0;

	//exceptions
	startExcep = 0;
	stopExcep = 0;
	cycles = 0;
	minExcep = 0;
	maxExcep = 0;
	avgExcep = 0;
	avgExcepSum = 0;

	//LSUs
	startLSU = 0;
	stopLSU = 0;
	LSUs = 0;
	minLSU = 0;
	maxLSU = 0;
	avgLSU = 0;
	avgLSUSum = 0;

	//Folds
	startFold = 0;
	stopFold = 0;
	Folds = 0;
	minFold = 0;
	maxFold = 0;
	avgFold = 0;
	avgFoldSum = 0;

	//Instructions
	startInstr = 0;
	stopInstr = 0;
	Instrs = 0;
	minInstr = 0;
	maxInstr = 0;
	avgInstr = 0;
	avgInstrSum = 0;
}

//sequence
void testSequence()
{
	printf("Hello, World!\n");
	int number1 = 5;
	int number2 = 6;
	printf("This is number %d\n", number1);
	number1 = number1 + number2;
	number2 = number1 + number2;
	number2 = number1 * number2;
	printf("Number is bigger\n");
	printf("Bye, World!\n");
}

//selection
void testSelection()
{
	int number = 5;
	if (number < 0)
	{
		printf("Number %d is smaller than 0.\n", number);
	}
	else
	{
		printf("Number %d is bigger than 0.\n", number);
	}
}

//iteration
void testIteration()
{
	int i = 1;

	while (i <= 5)
	{
		printf("%d\n", i);
		++i;
	}

}

//bubble sort
void swap(int *xp, int *yp)
{
    int temp = *xp;
    *xp = *yp;
    *yp = temp;
}
void bubbleSort(int arr[], int n)
{
   int i, j;
   for (i = 0; i < n-1; i++)
       for (j = 0; j < n-i-1; j++)
           if (arr[j] > arr[j+1])
              swap(&arr[j], &arr[j+1]);
}
void printArray(int arr[], int size)
{
    int i;
    for (i=0; i < size; i++)
    	printf("%d ", arr[i]);
    printf("\n");
}
void testBubbleSort()
{
	int arr[] = {64, 34, 25, 12, 22, 11, 90};
	    int n = sizeof(arr)/sizeof(arr[0]);
	    bubbleSort(arr, n);
	    printf("Sorted array: \n");
	    printArray(arr, n);
}

//quick sort
int partition (int arr[], int low, int high)
{
    int pivot = arr[high];    // pivot
    int i = (low - 1);  // Index of smaller element

    for (int j = low; j <= high- 1; j++)
    {
        // If current element is smaller than the pivot
        if (arr[j] < pivot)
        {
            i++;    // increment index of smaller element
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}
void quickSort(int arr[], int low, int high)
{
    if (low < high)
    {
        /* pi is partitioning index, arr[p] is now
           at right place */
        int pi = partition(arr, low, high);

        // Separately sort elements before
        // partition and after partition
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
void testQuickSort()
{
	int arr[] = {10, 7, 8, 9, 1, 5};
	int n = sizeof(arr)/sizeof(arr[0]);
	quickSort(arr, 0, n-1);
	printf("Sorted array: \n");
	printArray(arr, n);
}




int main(void)
{
	//initialization
		initMCU();
		initDWT();

    //counting sequence---------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testSequence();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//--------------------------------------------


    //counting selection---------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testSelection();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//-------------------------------------------


    //counting iteration--------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testIteration();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//-------------------------------------------


    //without interrupts
		//counting Bubble sort------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testBubbleSort();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//---------------------------------------------


		//counting Quick sort----------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testQuickSort();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//---------------------------------------------


    //with interrupts
		//counting Bubble sort------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testBubbleSort();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//---------------------------------------------


		//counting Quick sort----------------------------
		for(int i = 0; i < maxRepetitions; i++)
		{
			startCounter();
			testQuickSort();
			stopCounter();
		}
		//printing
		printCounter();
		clearCounter();
		//---------------------------------------------


    /* This for loop should be replaced. By default this loop allows a single stepping. */
    while (1) {
    }
    /* Never leave main */
    return 0;
}
////////////////////////////////////////////////////////////////////////////////
// EOF
////////////////////////////////////////////////////////////////////////////////
