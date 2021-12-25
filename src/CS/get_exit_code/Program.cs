using System.Diagnostics;

void RunCmdWithExitCodeWin(string cmd)
{
    Process proc = Process.Start("CMD.exe", "/C " + cmd);

    proc.WaitForExit();
    Console.WriteLine(proc.ExitCode);
}

void RunCmdWithExitCodeUnix(string cmd) {
    Process proc = Process.Start("sh", "-c " + cmd);

    proc.WaitForExit();
    Console.WriteLine(proc.ExitCode);

}

string ver = Environment.OSVersion.Platform.ToString();
Console.WriteLine(args);

if (ver == "Unix") {
    RunCmdWithExitCodeUnix("'python3 -c \\'areghqd\\''"); // Won't work with the default exit command.
}
else {
    RunCmdWithExitCodeWin("exit 12");
}
