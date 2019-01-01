/* 
* @ debug.h 
* Include this file for debugging purposes.
*/

#ifndef __DEBUG_H__
#define __DEBUG_H__

#define DEBUG

#ifdef DEBUG
Serial pc(USBTX, USBRX); 
#endif

#endif /* #ifndef __DEBUG_H__ */