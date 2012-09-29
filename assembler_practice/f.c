/*
exercise: Assembler practice

Simon Maurer
Lothar Rubusch
Yosafat Praquive Triana
*/

#include <stdlib.h>

/**
 * x != k
 */
int f_notEqual() {
    int x = 1;
    if (x != 2)
        x = 2;
    return x;
}

/**
 * x < k
 */
int f_smallerThan() {
    int x = 1;
    if (x < 2)
        x = 2;
    return x;
}

/**
 * x[k]
 */
int f_arr() {
    int x[2];
    x[0] = 1;
    x[1] = 2;
    return x[1];
}

/**
 * x^y
 */
int f_power() {
    int x = 3;
    int y = 2;
    return x^y;
}

/**
 * x<<k
 */
int f_leftshift()
{
	int x,k, res;
	x=16;
	k=2;

        /* x<<k */
	res = x<<k;

        return res;
}

/**
 *
 */
int f_while()
{
	/* while */
	while( 1 ){
		;
	};
        return 0;
}

int main( int argc, char** argv )
{
    f_notEqual();
    f_smallerThan();
    f_arr();
    f_power();
    f_leftshift();
    f_while();
    exit( EXIT_SUCCESS );
}
