// TypeScript checks types before the program runs.
// Fix the mistake on line 6 and press Run again.
function addTax(price: number): number {
  return price * 1.18;
}
const total: number = addTax("250");
console.log("Total with tax:", total);
