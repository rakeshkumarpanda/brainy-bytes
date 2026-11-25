// expect: 9: CS0122: 'Account.balance' is inaccessible due to its protection level
using System;
class Account {
    int balance = 100;
}
class Program {
    static void Main() {
        Account a = new Account();
        a.balance = 1000000;
    }
}
