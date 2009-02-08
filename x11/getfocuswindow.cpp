#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <X11/Xlib.h>

Display* dpy;

static void
Display_Window_Id(Window window)
{
    char *win_name;
    
    printf("0x%lx", window);         /* print id # in hex/dec */

    if (!window) {
	printf(" (none)");
    } else {
	if (window == DefaultRootWindow(dpy)) {
	    printf(" (the root window)");
	}
	if (!XFetchName(dpy, window, &win_name)) { /* Get window name if any */
	    printf(" (has no name)");
	} else if (win_name) {
	    printf(" \"%s\"", win_name);
	    XFree(win_name);
	}
	else
	    printf(" (has no name)");
    }
    printf("\n");
    fflush(stdout);

    return;
}
int
main()
{
   dpy = XOpenDisplay(0);
   if (dpy == 0) {
     fprintf(stderr, "unable to open display\n");
     exit(-1);
   }

   Window focus_window = 0;
   while (1) {
     usleep(50000);

     Window win;
     int trash;
     XGetInputFocus(dpy, &win, &trash);
     if (win != focus_window) {
       focus_window = win;
       Display_Window_Id(focus_window);
     }
   }


   XCloseDisplay(dpy);
   return 0;
}
