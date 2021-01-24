/**
 * Tomas Hruz, xhruzt00@stud.fit.vutbr.cz
 * Projekt 2, predmet IOS
 * Implementácia "Faneuil Hall Problem"
 **/
#include <stdio.h>
#include <stdlib.h>
#include<string.h>
#include<time.h>
#include <ctype.h>
#include <fcntl.h>
#include<signal.h>
#include <unistd.h>
#include<sys/sem.h>
#include<sys/shm.h>
#include<sys/wait.h>
#include<sys/ipc.h>
#include<sys/stat.h>
#include<sys/time.h>
#include<sys/types.h>
#include <sys/mman.h>
#include <semaphore.h>

//mapovanie premennych
#define MMAP(ptr) {(ptr) = mmap(NULL, sizeof(*(ptr)), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);}
#define MUNMAP(ptr) {munmap((ptr), sizeof((ptr)));}

int pid_immigrant = 0; //id imigranta
int pid_judge = 0; //id sudcu
FILE *output; //vystupny subor

//zdielane premenne
int *entered = NULL; //vstupeny imigranti
int *checked = NULL; //zaregistrovany imigranti
int *allofthem = NULL; //vsetci imigranti v budove
int *instructions = NULL; //pocitadlo vystupnych sprav
int *judgee = NULL; //pomocna premenna pre to ci je sudca v budove
int *tempcounter = NULL; //pomocna premenna na pocitanie imigrantov aby sudca vedel ci ma ist este do budovy
int *checkedhelp = NULL;//pomocna premenna zaregistrovanych imigrantov

//semafory
sem_t *noJudge = NULL; //semafor "je sudca v budove"
sem_t *mutex = NULL; //semafor "imigranti ktory sa zaregistrovali"
sem_t *confirmed = NULL;//semafor "sudca vykonal confirm"
sem_t *all = NULL;//semafor "vsetci zapisany"

//funkcia pre kontrolu argumentov
int argumentcheck(int PI, int IG, int JG, int IT, int JT) 
{ 
    if (PI < 1)
    {
        fprintf (stderr, "PI must be greater or equal 1 \n");
        exit(1);
    }

    if (IG < 0 || IG > 2000)
    {
        fprintf (stderr, "IG must be greater or equal 0 and lesser or equal 2000 \n");
        exit(1);
    }

    if (JG < 0 || JG > 2000)
    {
        fprintf (stderr, "JG must be greater or equal 0 and lesser or equal 2000 \n");
        exit(1);
    }

    if (IT < 0 || IT > 2000)
    {
        fprintf (stderr, "IT must be greater or equal 0 and lesser or equal 2000 \n");
        exit(1);
    }

    if (JT < 0 || JT > 2000)
    {
        fprintf (stderr, "JT must be greater or equal 0 and lesser or equal 2000 \n");
        exit(1);
    }
    return 0;
} 

//funkcia sudcu
void judge(int JT, int PI, int JG)
{
    
    while((*tempcounter) < PI)
    {
        usleep (rand () % (JG * 1000));
        //judge chce vojst
        *instructions = *instructions + 1;
        setbuf (output, NULL);
        fprintf(output,"%d        : JUDGE :        wants to enter\n",*instructions);
        //judge vosiel
        sem_wait(noJudge);
        sem_wait(mutex);
        *instructions = *instructions + 1;
        setbuf (output, NULL);
        fprintf(output,"%d        : JUDGE :        enters : %d : %d : %d\n",*instructions, *entered, *checked, *allofthem);
        *judgee = 1;

        //judge chce potvrdzovat
        if (*entered != *checked)
        {
            *instructions = *instructions + 1;
            setbuf (output, NULL);
            fprintf(output,"%d        : JUDGE :        waits for imm : %d : %d : %d\n",*instructions, *entered, *checked, *allofthem); 
            sem_post(mutex);
            sem_wait(all);
        }

        *instructions = *instructions + 1;
        setbuf (output, NULL);
        fprintf(output,"%d        : JUDGE :        starts confirmation : %d : %d : %d\n",*instructions, *entered, *checked, *allofthem);
        usleep (rand () % (JT * 1000));
        *instructions = *instructions + 1;
        *entered = 0;
        *checked = 0;
        setbuf (output, NULL);
        fprintf(output,"%d        : JUDGE :        ends confirmation : %d : %d : %d\n",*instructions, *entered, *checked, *allofthem);
        for (int j = 0; j < *checkedhelp; j++)
        {
            sem_post(confirmed);
        }
        usleep (rand () % (JT * 1000));
        //judge odchadza
        *instructions = *instructions + 1;
        setbuf (output, NULL);
        fprintf(output,"%d        : JUDGE :        leaves : %d : %d : %d\n",*instructions, *entered, *checked, *allofthem);
        *judgee = 0;

        sem_post(mutex);    
        sem_post(noJudge); 
    }
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : JUDGE :        finishes\n",*instructions);
}

//funkcia imigranta
void immigrant(int IT, int immcounter)
{
    //imigrant zacal
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : IMM %d :        starts\n",*instructions, immcounter);
    //imigrant chce vojst
    sem_wait(noJudge);
    *entered = *entered + 1;
    *allofthem = *allofthem + 1;
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : IMM %d :        enters : %d : %d : %d\n",*instructions, immcounter, *entered, *checked, *allofthem);
    sem_post(noJudge);
    //imigrant sa chce checknut
    *tempcounter = *tempcounter +1;
    sem_wait(mutex);
    *instructions = *instructions + 1;
    *checked = *checked + 1;
    *checkedhelp = *checkedhelp + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : IMM %d :        checks : %d : %d : %d\n",*instructions, immcounter, *entered, *checked, *allofthem);
    //cakanie
    if ((*judgee == 1) && (*entered == *checked))
    {
        sem_post(all);
    }
    else
    {
        sem_post(mutex);
    }
    //rozdavanie certifikatov
    sem_wait(confirmed);
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : IMM %d :        wants certificate : %d : %d : %d\n",*instructions, immcounter, *entered, *checked, *allofthem);
    usleep (rand () % (IT * 1000));
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    fprintf(output,"%d        : IMM %d :        got certificate : %d : %d : %d\n",*instructions, immcounter, *entered, *checked, *allofthem);
    sem_wait(noJudge);
    //odchod z budovy
    *instructions = *instructions + 1;
    setbuf (output, NULL);
    *allofthem = *allofthem - 1;
    fprintf(output,"%d        : IMM %d :        leaves : %d : %d : %d\n",*instructions, immcounter, *entered, *checked, *allofthem);
    sem_post(noJudge);
}
 
int main(int argc, char *argv[])
{
    if (argc != 6)
    {
        fprintf (stderr,"Wrong number of arguments\n");
        return 1;
    }
    //ziskanie argumentov
    int PI = atoi(argv[1]);
    int IG = atoi(argv[2]);
    int JG = atoi(argv[3]);
    int IT = atoi(argv[4]);
    int JT = atoi(argv[5]);

    //inicializacia zdielanych premennych a semaforov
    MMAP(entered);
    MMAP(checked);
    MMAP(allofthem);
    MMAP(instructions);
    MMAP(judgee);
    MMAP(tempcounter);
    MMAP(checkedhelp);
    *entered = 0;
    *checked = 0;
    *allofthem = 0;
    *instructions = 0;
    *judgee = 0;
    *tempcounter = 0;
    *checkedhelp = 0;

    //inicializacia semaforov
    if ((noJudge = sem_open("/xhruzt00.noJudge", O_CREAT | O_EXCL, 0666, 1)) == SEM_FAILED) {
        fprintf(stderr,"Opening \"noJudge\" semaphore failed.\n");
        return 1;
    }
    if ((mutex = sem_open("/xhruzt00.mutex", O_CREAT | O_EXCL, 0666, 1)) == SEM_FAILED) {
        fprintf(stderr,"Opening \"mutex\" semaphore failed.\n");
        return 1;
    }
    if ((confirmed = sem_open("/xhruzt00.confirmed", O_CREAT | O_EXCL, 0666, 0)) == SEM_FAILED) {
        fprintf(stderr,"Opening \"confirmed\" semaphore failed.\n");
        return 1;
    }
    if ((all = sem_open("/xhruzt00.all", O_CREAT | O_EXCL, 0666, 0)) == SEM_FAILED) {
        fprintf(stderr,"Opening \"all\" semaphore failed.\n");
        return 1;
    }

    //kontrola argumentov
    argumentcheck(PI, IG, JG, IT, JT);
    //funkcia na nahodny cas
    srand (time (NULL));
    //otvorenie suboru
    output = fopen ("proj2.out", "w");
    if(output == NULL)
    {
        fprintf(stderr,"Error with opening output file!");   
        exit(1);             
    }
    //forkovanie
    pid_judge = fork();
    if (pid_judge==0) 
    {
        judge(JT, PI, JG);
    } 
    else 
    {
        for(int i=0;i<PI;i++)
        {
            usleep (rand () % (IG * 1000));
            pid_immigrant = fork();
            if (pid_immigrant==0) 
            {
                immigrant(IT, i+1);
                return 0;
            } 
            else 
            {
                // k´od pro rodiˇce, pid = PID potomka
                // pid2 = wait(&stav);
            }
        }
    }
    //poriadky so semaformi a varmi
    sem_close(noJudge);
    sem_unlink("/xhruzt00.noJudge");
    sem_close(mutex);
    sem_unlink("/xhruzt00.mutex");
    sem_close(confirmed);
    sem_unlink("/xhruzt00.confirmed");
    sem_close(all);
    sem_unlink("/xhruzt00.all");
    MUNMAP(entered);
    MUNMAP(checked);
    MUNMAP(allofthem);
    MUNMAP(instructions);
    MUNMAP(judgee);
    MUNMAP(tempcounter);
    MUNMAP(checkedhelp);
    //zatvorenie vystupneho suboru
    fclose(output);
    return 0;
}
 
/*------------------------------------------------*/
//kontrola argumentov by sa mala zlepsit
//neukoncuju sa procesy?
//zabalit vystupy do dalsieho semaforu