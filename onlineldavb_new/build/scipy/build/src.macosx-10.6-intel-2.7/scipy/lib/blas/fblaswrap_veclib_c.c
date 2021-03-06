#line 1 "scipy/lib/blas/fblaswrap_veclib_c.c.src"

/*
 *****************************************************************************
 **       This file was autogenerated from a template  DO NOT EDIT!!!!      **
 **       Changes should be made to the original source (.src) file         **
 *****************************************************************************
 */

#line 1
#include <complex.h>
#include <vecLib/vecLib.h>

//#define WRAP_F77(a) wcblas_##a##_
#define WRAP_F77(a) w##a##_

#line 12

void WRAP_F77(cdotu)(complex *dotu, const int *N, const complex *X, const int *incX, const complex *Y, const int *incY)
{
    cblas_cdotu_sub(*N, X, *incX, Y, *incY, dotu);
}


#line 12

void WRAP_F77(zdotu)(double complex *dotu, const int *N, const double complex *X, const int *incX, const double complex *Y, const int *incY)
{
    cblas_zdotu_sub(*N, X, *incX, Y, *incY, dotu);
}


#line 12

void WRAP_F77(cdotc)(complex *dotc, const int *N, const complex *X, const int *incX, const complex *Y, const int *incY)
{
    cblas_cdotc_sub(*N, X, *incX, Y, *incY, dotc);
}


#line 12

void WRAP_F77(zdotc)(double complex *dotc, const int *N, const double complex *X, const int *incX, const double complex *Y, const int *incY)
{
    cblas_zdotc_sub(*N, X, *incX, Y, *incY, dotc);
}




