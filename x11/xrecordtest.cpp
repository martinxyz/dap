#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>
#include <X11/extensions/record.h>

static void
callback(XPointer p, XRecordInterceptData* data)
{
   printf("x\n");
   fflush(stdout);
   XRecordFreeData(data);
}

int
main()
{
   Display* display = XOpenDisplay(0);
   if (display == 0) {
     fprintf(stderr, "unable to open display\n");
     exit(-1);
   }
   
   XRecordClientSpec clients = XRecordAllClients;
   XRecordRange* range = XRecordAllocRange();
   if (range == 0) {
     fprintf(stderr, "unable to allocate XRecordRange\n");
     exit(-1);
   }

   range->device_events.first = KeyPress;
   range->device_events.last = MotionNotify;
   XRecordContext context = XRecordCreateContext
     (display, 0, &clients, 1, &range, 1);
   if (context == 0) {
     fprintf(stderr, "unable to create XRecordContext\n");
     exit(-1);
   }

   XFree(range);

   XRecordEnableContextAsync(display, context, callback, 0);

   // might be nonsense:
   XRecordDisableContext(display, context);
   XRecordFreeContext(display, context);
   XCloseDisplay(display);
   return 0;
}
