// expect: 4: CS0266: Cannot implicitly convert type 'int' to 'short'. An explicit conversion exists (are you missing a cast?)
using System;
short a = 1, b = 2;
short c = a + b;
Console.WriteLine(c);
