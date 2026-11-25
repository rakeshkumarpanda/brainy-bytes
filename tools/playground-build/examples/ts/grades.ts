class Student {
  constructor(public name: string, private marks: number[]) {}

  average(): number {
    const sum = this.marks.reduce((a, b) => a + b, 0);
    return sum / this.marks.length;
  }
}

const students: Student[] = [
  new Student("Asha", [88, 92, 79]),
  new Student("Ravi", [65, 70, 81]),
  new Student("Meera", [95, 89, 99]),
];
students.sort((a, b) => b.average() - a.average());
students.forEach((s, i) => {
  console.log(i + 1, s.name, s.average().toFixed(1));
});
console.log("Top student:", students[0].name);
