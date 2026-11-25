interface CartRow {
  item: string;
  price: number;
  qty: number;
}

function lineTotal(price: number, qty: number): number {
  return price * qty;
}

const cart: CartRow[] = [
  { item: "Notebook", price: 45, qty: 3 },
  { item: "Pencil", price: 10, qty: 5 },
  { item: "Water bottle", price: 120, qty: 1 },
];

let bill: number = 0;
for (const row of cart) {
  const cost = lineTotal(row.price, row.qty);
  console.log(`${row.item} x ${row.qty} = ${cost}`);
  bill += cost;
}
if (bill > 200) {
  bill = bill - Math.floor(bill / 10); // 10% off on big bills
}
console.log("You pay:", bill, "rupees");
