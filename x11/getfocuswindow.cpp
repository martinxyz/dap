#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>

Display* dpy;

static void
Display_Window_Id(Window window)
{
  //printf("0x%lx ", window);
  if (!window) {
	printf("(none)");
  } else {
	if (window == DefaultRootWindow(dpy)) {
      printf("(the root window)");
	} else {
      /*
        char *name;
        if (!XFetchName(dpy, window, &name)) {
        printf(" (has no name)");
        } else if (name) {
        printf(" \"%s\"", name);
        XFree(name);
        } else {
        printf(" (has no name)");
        }
      */
      XClassHint class_hint;
      if (!XGetClassHint(dpy, window, &class_hint)) { /* Get window name if any */
        Window parent_window;
        Window root_window;
        Window *children;
        unsigned int nchildren;
        XQueryTree(dpy, window, &root_window, &parent_window, &children, &nchildren);
        if (parent_window == root_window) {
          printf("(window without class hint)");
        } else {
          Display_Window_Id(parent_window);
          return;
        }
      } else {
        if (class_hint.res_name) {
          XFree(class_hint.res_name);
        }
        if (class_hint.res_class) {
          printf("%s", class_hint.res_class);
          XFree(class_hint.res_class);
        }
      }
    }
  }
  printf("\n");
  fflush(stdout);

  return;
}

int
main()
{
  _Xdebug = 1;
  dpy = XOpenDisplay(0);
  if (!dpy) {
    fprintf(stderr, "unable to open display\n");
    exit(-1);
  }

/*
  int (*XSetErrorHandler(handler))()
    int (*handler)(Display *, XErrorEvent *)
*/

  Window focus_window = 0;
  while (1) {
    usleep(50000);

    Window win;
    int trash;
    int result = XGetInputFocus(dpy, &win, &trash);
    if (!result) {
      printf("Error returned!\n");
    } else {
      if (win != focus_window) {
        focus_window = win;
        Display_Window_Id(focus_window);
      }
    }
  }


  XCloseDisplay(dpy);
  return 0;
}
