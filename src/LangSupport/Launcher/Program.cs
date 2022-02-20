/*  +========== Launcher For PyPlus ==========+
    | A launcher that runs PyPlus in a sub-   |
    | process.                                |
    +=========================================+
*/

using System.Diagnostics;
using System;
using static System.Environment;

OperatingSystem os  = Environment.OSVersion;
bool isMac = os.Platform == PlatformID.MacOSX;

#if (isMac)
    Console.WriteLine("Launcher is useless on Mac.");
    Console.WriteLine("Use `open` or double-click the compiled Mac App to run PyPlus.");
    Console.WriteLine("Launching anyway.");
    Process.Start("open PyPlus.app");
#endif

Process.Start("main/main");
