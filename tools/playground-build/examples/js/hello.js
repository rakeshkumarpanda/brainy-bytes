// prompt() reads one line from the Input box
const name = prompt("What is your name? ");
const age = Number(prompt("How old are you? "));
console.log("Hello, " + name + "!");
console.log("In 5 years you will be", age + 5);
if (age >= 13) {
  console.log("You are a teenager or older.");
} else {
  console.log("You are a kid. Have fun!");
}
