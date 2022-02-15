Console.Write("Press [Enter] to Exit...");

ConsoleKeyInfo keyInfo = Console.ReadKey(true);
while (keyInfo.Key != ConsoleKey.Enter)
{
    keyInfo = Console.ReadKey(true);
}

Console.WriteLine("");
