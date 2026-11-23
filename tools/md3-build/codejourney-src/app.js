
gsap.registerPlugin(MotionPathPlugin);
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

/* ---------- Material 3 Expressive style wavy progress ---------- */
let wavyId=0;
function drawWavy(host,f){
  if(!host)return;
  if(!host.dataset.cid)host.dataset.cid='wv'+(wavyId++);
  const w=Math.max(60,host.clientWidth),h=16,wl=22,amp=3.4,mid=h/2;
  let d='M0 '+mid;
  for(let x=0;x<=w+wl;x+=2)d+=' L'+x+' '+(mid+Math.sin(x/wl*2*Math.PI)*amp).toFixed(2);
  const px=Math.max(0,Math.min(1,f))*w,id=host.dataset.cid;
  host.innerHTML=`<svg width="${w}" height="${h}"><defs><clipPath id="${id}"><rect x="-2" y="-4" width="${px+2}" height="${h+8}"/></clipPath></defs>`+
   (px<w-8?`<line x1="${Math.min(w,px+8)}" y1="${mid}" x2="${w-2}" y2="${mid}" class="wv-track"/>`:'')+
   `<g clip-path="url(#${id})"><path d="${d}" class="wv-wave"/></g><circle cx="${w-2}" cy="${mid}" r="3" class="wv-end"/></svg>`;
}

/* ---------- Generic step player: Play with speed, Step, Back, Reset ---------- */
class Player{
  constructor(root,opts){
    this.root=root;this.o=opts;this.k=0;this.speed=1;this.timer=null;this.playing=false;this.pf={f:0};
    root.querySelector('[data-act=play]').onclick=()=>this.toggle();
    root.querySelector('[data-act=step]').onclick=()=>{this.pause();this.step()};
    root.querySelector('[data-act=back]').onclick=()=>{this.pause();this.back()};
    root.querySelector('[data-act=reset]').onclick=()=>this.reset();
    root.querySelector('[data-act=speed]').onchange=e=>{this.speed=parseFloat(e.target.value)};
    this.countEl=root.querySelector('[data-role=count]');
    this.wavy=root.querySelector('[data-role=wavy]');
    this.dotsEl=opts.dots||null;
    window.addEventListener('resize',()=>drawWavy(this.wavy,this.pf.f));
  }
  total(){return this.o.total()}
  toggle(){this.playing?this.pause():this.play()}
  play(){
    if(this.k>=this.total()){this.k=0;this.o.render(0,false);this.ui()}
    this.playing=true;this.setBtn();this.step();this.schedule();
  }
  schedule(){
    clearTimeout(this.timer);
    if(!this.playing)return;
    if(this.k>=this.total()){this.pause();return}
    this.timer=setTimeout(()=>{this.step();this.schedule()},this.o.baseMs(this.k)/this.speed);
  }
  pause(){this.playing=false;clearTimeout(this.timer);this.setBtn()}
  setBtn(){const b=this.root.querySelector('[data-act=play]');b.textContent=this.playing?'❚❚ Pause':'▶ Play';b.classList.toggle('playing',this.playing)}
  step(){if(this.k<this.total()){this.k++;this.o.render(this.k,true);this.ui()}else this.pause()}
  back(){if(this.k>0){this.k--;this.o.render(this.k,false);this.ui()}}
  jump(k){this.pause();this.k=k;this.o.render(k,false);this.ui()}
  reset(){this.pause();this.k=0;this.o.render(0,false);this.ui()}
  ui(){
    const n=this.total();
    this.countEl.textContent=(this.o.unit||'Step')+' '+this.k+' / '+n;
    gsap.to(this.pf,{f:n?this.k/n:0,duration:.6,ease:'power2.out',overwrite:true,onUpdate:()=>drawWavy(this.wavy,this.pf.f)});
    if(this.dotsEl){
      if(this.dotsEl.children.length!==n){
        this.dotsEl.innerHTML='';
        for(let i=1;i<=n;i++){const d=document.createElement('button');d.className='dot';d.title='Go to step '+i;d.onclick=()=>this.jump(i);this.dotsEl.appendChild(d)}
      }
      [...this.dotsEl.children].forEach((d,i)=>{d.className='dot'+(i+1<this.k?' done':'')+(i+1===this.k?' cur':'')});
    }
  }
}

/* ---------- Small playful effects ---------- */
function confetti(host,x,y,n=30){
  const cols=['#ff6363','#f2a516','#16b97f','#4c7dff','#9a63ff','#ff8fc7'];
  for(let i=0;i<n;i++){
    const d=document.createElement('i');d.className='conf';d.style.background=cols[i%cols.length];d.style.left=x+'px';d.style.top=y+'px';host.appendChild(d);
    const a=Math.random()*Math.PI*2,r=50+Math.random()*100;
    gsap.fromTo(d,{x:0,y:0,rotation:0,opacity:1},{x:Math.cos(a)*r,y:Math.sin(a)*r-50,rotation:Math.random()*600-300,opacity:0,duration:1.1+Math.random()*.6,ease:'power3.out',onComplete:()=>d.remove()});
  }
}
function shake(elm){gsap.fromTo(elm,{x:0},{keyframes:{x:[0,-12,11,-8,7,-3,0]},duration:.55,ease:'none'})}
function pop(elm,delay=0){if(elm)gsap.fromTo(elm,{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:.6,delay,ease:'back.out(2.6)'})}
function relPos(elm,host){const a=elm.getBoundingClientRect(),b=host.getBoundingClientRect();return{x:a.left-b.left+a.width/2,y:a.top-b.top+a.height/2}}

/* ===================================================================
   TAB 1 DATA: one program per language, all print "Sum = 8"
   (content checked for technical accuracy)
   =================================================================== */
function outputTail(writer){
  return [
   {t:'The OS delivers the bytes to the terminal',who:'Operating System + Terminal application',
    d:'The OS passes the bytes from the program\'s standard output to the terminal application (Command Prompt, PowerShell, Windows Terminal, or a Linux or macOS terminal). At this moment the output is still only numbers, for example 83 117 109 for the letters S u m.',
    show:['term'],flow:['os','term','83 117 109 ...','bytes']},
   {t:'Bytes become human readable text on the monitor',who:'Terminal + Font renderer + Graphics card + Monitor',
    d:'The terminal decodes the bytes back into characters using the same encoding (UTF-8). For each character it finds the shape (glyph) in a font and draws it. The graphics card (GPU) sends the final pixels to the monitor, and now a human can read: Sum = 8.',
    show:['screen'],flow:['term','screen','S u m = 8','pixels'],out:'Sum = 8'}
  ];
}

const LANGS={
/* ------------------------------ JAVA ------------------------------ */
java:{
 name:'Java',srcTitle:'Source code: Hello.java (human readable)',bcTitle:'Bytecode in Hello.class (javap -c, simplified)',
 vmTitle:'JVM (Java Virtual Machine) running inside the java process',
 code:['public class Hello {','    public static void main(String[] args) {','        int a = 5, b = 3;','        System.out.println("Sum = " + (a + b));','    }','}'],
 bc:['iconst_5','istore_1            // a = 5','iconst_3','istore_2            // b = 3','getstatic     System.out','iload_1','iload_2','iadd                // a + b','invokedynamic makeConcatWithConstants','invokevirtual PrintStream.println','return'],
 nodes:{dev:['👩‍💻','Programmer','writes code in an IDE'],src:['📄','Hello.java','source code (text)'],comp:['⚙️','javac','Java compiler (part of JDK)'],bc:['📦','Hello.class','Java bytecode'],
  n1:['📥','Class Loader','loads .class files'],n2:['🛡️','Bytecode Verifier','safety check + linking'],n3:['🧠','Runtime Data Areas','method area, heap, stacks'],n4:['🚀','Execution Engine','interpreter + JIT compiler'],
  cpu:['🔲','CPU','executes machine code'],os:['🛠️','Operating System','processes, system calls'],term:['⌨️','Terminal','console window'],screen:['🖥️','Monitor','pixels you can see']},
 steps:[
  {t:'The programmer writes the source code',who:'Programmer',d:'The programmer types Java code in an editor or IDE such as IntelliJ IDEA, Eclipse or VS Code. This is plain human readable text. The computer cannot execute it in this form.',show:['dev'],code:'type'},
  {t:'The code is saved as Hello.java',who:'Editor + Operating System (file system)',d:'The editor saves the text to disk as Hello.java. On disk the file is only a sequence of bytes that represent characters (for example in UTF-8). In Java the file name must match the public class name, Hello.',show:['src'],flow:['dev','src','save','text']},
  {t:'The programmer runs the compiler: javac Hello.java',who:'javac, the Java compiler (comes with the JDK)',d:'javac reads the complete source file before producing anything. This is called ahead of time compilation. javac is one program and the JVM is a different program.',show:['comp'],flow:['src','comp','Hello.java','text'],cmd:'$ javac Hello.java'},
  {t:'The compiler checks the whole program',who:'javac',d:'javac does lexical analysis (splits the text into tokens such as int, a, =, 5), parsing (builds a syntax tree) and semantic analysis (checks types and names). If there is any compile error, javac reports it here, no .class file is created, and the program never starts.',act:['comp'],detail:{comp:'tokens → syntax tree → type check ✓'}},
  {t:'javac writes bytecode into Hello.class',who:'javac',d:'The result is Java bytecode: compact instructions for the JVM, not for your CPU. The same Hello.class can run on Windows, Linux or macOS on any JVM. This is the meaning of "write once, run anywhere".',show:['bc'],flow:['comp','bc','bytecode','bc'],bcShow:true},
  {t:'The programmer starts the program: java Hello',who:'java launcher + Operating System',d:'The command java Hello asks the operating system to create a new process. Inside it the JVM starts. A common JVM is HotSpot, which is itself a native program written in C++, so the CPU can run it directly.',show:['os','vm'],act:['os','vm'],flow:['dev','os','java Hello','ctl'],cmd:'$ java Hello'},
  {t:'The Class Loader loads Hello.class',who:'Class Loader subsystem (inside the JVM)',d:'Class loaders find and load classes into memory. Core classes such as String and System come from the Bootstrap class loader. Your Hello class comes from the Application class loader, which searches the classpath.',show:['n1'],flow:['bc','n1','Hello.class','bc']},
  {t:'Verification and linking',who:'Bytecode Verifier (linking stage)',d:'Before any instruction runs, the verifier checks that the bytecode is valid and safe, for example that types on the operand stack match and no jump goes to an invalid place. Linking then prepares static fields and resolves references, and initialization runs static initializers.',show:['n2'],flow:['n1','n2','verify','bc']},
  {t:'The JVM creates the memory environment',who:'JVM Runtime Data Areas',d:'Method Area (Metaspace in HotSpot) stores class information and bytecode. The Heap stores objects such as the String "Sum = 8". Each thread gets a JVM Stack, and every method call pushes a frame holding local variables (a, b) and an operand stack. The PC register remembers the current instruction.',show:['n3'],flow:['n2','n3','prepare','bc'],detail:{n3:'Method area: Hello | Heap | Stack: main()'}},
  {t:'The Execution Engine starts executing main()',who:'Execution Engine: the bytecode interpreter',d:'The interpreter reads bytecode one instruction at a time. iconst_5 pushes 5 on the operand stack and istore_1 stores it in local variable a. Then iconst_3 and istore_2 store 3 in b.',show:['n4'],act:['n4'],flow:['n3','n4','main()','bc'],bc:[0,1,2,3],src:[2],detail:{n3:'main frame: a = 5, b = 3'}},
  {t:'Addition, and where the JIT fits',who:'Interpreter + JIT compiler',d:'iload_1 and iload_2 push a and b, then iadd adds them to give 8. When a method runs many times (a "hot" method), the JIT compiler (C1 and C2 in HotSpot) translates it into optimized native machine code and reuses it. Our main runs only once, so it is simply interpreted.',act:['n4'],bc:[4,5,6,7],src:[3],detail:{n4:'iadd → 8'}},
  {t:'The CPU does the real work',who:'CPU',d:'Only the CPU actually executes instructions, and it understands only native machine code (x86-64, ARM64 and so on). The JVM interpreter is native code, and JIT output is native code. Either way, the CPU runs real machine instructions that carry out each bytecode.',show:['cpu'],act:['cpu'],flow:['n4','cpu','machine code','native']},
  {t:'println asks the operating system to write',who:'System.out.println → JVM native code → OS system call',d:'invokedynamic builds the String "Sum = 8". println encodes it into bytes using a character encoding (such as UTF-8) and the JVM makes a system call, write() on Linux and macOS or WriteFile on Windows, to standard output (stdout). A program cannot put text on the screen by itself. It must ask the operating system.',act:['cpu','os'],flow:['cpu','os','write(stdout, bytes)','bytes'],bc:[8,9],src:[3]},
  ...outputTail(),
  {t:'The program finishes',who:'JVM + Operating System',d:'The return instruction ends main. The JVM shuts down, its memory is released, and the OS ends the process with exit code 0, which means success.',act:['os'],bc:[10],src:[4],cmd:'(process exited with code 0)',info:true}
 ],
 notes:`<ul>
  <li><b>Who compiles:</b> <code>javac</code> (part of the JDK) compiles <code>.java</code> source into <code>.class</code> bytecode. <b>Who runs it:</b> the JVM, started by the <code>java</code> command.</li>
  <li>The JDK is for developers (compiler plus tools plus runtime). The JVM is the part that actually runs bytecode.</li>
  <li>The JVM does both interpreting and JIT compiling. Saying "Java is only compiled" or "only interpreted" is incomplete.</li>
  <li>Since Java 11 you can type <code>java Hello.java</code> directly. It still compiles the source first, only in memory.</li>
  <li><span class="fix">Correction:</span> the JVM does not translate output into "human language". <code>println</code> produces bytes, the OS delivers them, and the terminal with a font draws them as pixels.</li>
 </ul>`
},
/* ------------------------------ PYTHON ------------------------------ */
python:{
 name:'Python',srcTitle:'Source code: hello.py (human readable)',bcTitle:'Bytecode code object (dis module, CPython 3.12, simplified)',
 vmTitle:'python process: CPython, which contains the PVM',
 code:['a = 5','b = 3','print("Sum =", a + b)'],
 bc:['RESUME         0','LOAD_CONST     5','STORE_NAME     a','LOAD_CONST     3','STORE_NAME     b','PUSH_NULL','LOAD_NAME      print','LOAD_CONST     \'Sum =\'','LOAD_NAME      a','LOAD_NAME      b','BINARY_OP      +','CALL           2','POP_TOP','RETURN_CONST   None'],
 nodes:{dev:['👩‍💻','Programmer','writes code in an editor'],src:['📄','hello.py','source code (text)'],comp:['⚙️','CPython compiler','built into the python program'],bc:['📦','Code object','bytecode in memory (.pyc for imports)'],
  n1:['📚','Runtime setup','builtins, sys, stdout'],n2:['🗂️','__main__ namespace','globals dict + frame'],n3:['🧠','Private heap','objects, ref counting, GC'],n4:['🔁','PVM evaluation loop','executes bytecode'],
  cpu:['🔲','CPU','executes machine code'],os:['🛠️','Operating System','processes, system calls'],term:['⌨️','Terminal','console window'],screen:['🖥️','Monitor','pixels you can see']},
 steps:[
  {t:'The programmer writes the source code',who:'Programmer',d:'The programmer types Python code in an editor such as VS Code, PyCharm or IDLE. It is plain human readable text.',show:['dev'],code:'type'},
  {t:'The code is saved as hello.py',who:'Editor + Operating System (file system)',d:'The editor saves the text to disk as hello.py, a sequence of bytes that represent characters (Python expects UTF-8 by default).',show:['src'],flow:['dev','src','save','text']},
  {t:'The programmer runs: python hello.py',who:'Operating System',d:'Python has no separate compile command. The OS starts the Python interpreter program. The standard one is CPython, written in C and already compiled to native machine code. Everything that follows happens inside this one process.',show:['os'],act:['os'],flow:['dev','os','python hello.py','ctl'],cmd:'$ python hello.py'},
  {t:'CPython reads the whole file and compiles it',who:'CPython compiler (inside the python program)',d:'Python is often called "interpreted", but CPython compiles first. It tokenizes the whole file, parses it into an AST (abstract syntax tree) and compiles that into bytecode. A SyntaxError anywhere in the file is reported now, before even line 1 runs.',show:['comp'],flow:['src','comp','hello.py','text'],detail:{comp:'tokens → AST → bytecode'}},
  {t:'The bytecode is ready',who:'CPython compiler',d:'The bytecode is stored in memory as a code object. For the script you run directly it is usually not saved to disk. For modules you import, CPython caches the bytecode in a __pycache__ folder as .pyc files so the next run can skip compiling. You can view bytecode with the dis module.',show:['bc'],flow:['comp','bc','bytecode','bc'],bcShow:true},
  {t:'The PVM prepares the runtime',who:'PVM (Python Virtual Machine) inside CPython',d:'The PVM is not a separate program you install, unlike the JVM. It is the part of CPython that executes bytecode. During startup CPython initializes the builtins module (which contains print), the sys module and sys.stdout.',show:['vm','n1'],act:['vm','n1'],flow:['bc','n1','code object','bc']},
  {t:'The namespace and frame are created',who:'PVM',d:'The script runs as the module named __main__. CPython creates its global namespace, a dictionary that will hold a and b, and a frame object that tracks the current instruction and a value stack.',show:['n2'],flow:['n1','n2','setup','bc']},
  {t:'The private heap holds every object',who:'CPython memory manager',d:'In Python every value is an object on CPython\'s private heap, including 5, 3 and the string "Sum =". Memory is freed by reference counting plus a garbage collector that finds reference cycles.',show:['n3'],flow:['n2','n3','objects','bc'],detail:{n3:'int 5, int 3, str "Sum ="'}},
  {t:'The evaluation loop executes bytecode',who:'PVM evaluation loop (the interpreter)',d:'The evaluation loop (in the CPython source file ceval.c) takes one bytecode instruction at a time. LOAD_CONST 5 then STORE_NAME a. LOAD_CONST 3 then STORE_NAME b.',show:['n4'],act:['n4'],flow:['n3','n4','execute','bc'],bc:[1,2,3,4],src:[0,1],detail:{n2:'globals: a = 5, b = 3'}},
  {t:'Addition and the call to print',who:'PVM evaluation loop',d:'LOAD_NAME finds print in builtins and finds a and b in the globals. BINARY_OP adds 5 and 3 and creates a new int object 8. CALL calls print with two arguments. Standard CPython has no JIT by default. Python 3.13 added an experimental JIT that is switched off unless you build or enable it.',act:['n4'],bc:[5,6,7,8,9,10,11],src:[2],detail:{n4:'BINARY_OP + → 8'}},
  {t:'The CPU executes CPython\'s machine code',who:'CPU',d:'The CPU never sees Python bytecode. For every bytecode instruction, CPython runs its own pre compiled C code, which is native machine code. That is the real work the CPU performs.',show:['cpu'],act:['cpu'],flow:['n4','cpu','machine code','native']},
  {t:'print writes to standard output',who:'print() → sys.stdout → OS system call',d:'print converts each argument to text, joins them with a space and adds a newline, giving "Sum = 8\\n". sys.stdout encodes this into bytes (usually UTF-8) and CPython makes a write() system call to the operating system.',act:['cpu','os'],flow:['cpu','os','write(stdout, bytes)','bytes'],src:[2]},
  ...outputTail(),
  {t:'The program finishes',who:'CPython + Operating System',d:'POP_TOP discards the return value of print (None), and RETURN_CONST None ends the module. CPython cleans up its objects and the OS ends the process with exit code 0.',act:['os'],bc:[12,13],cmd:'(process exited with code 0)',info:true}
 ],
 notes:`<ul>
  <li><span class="fix">Correction:</span> Python is not "only interpreted line by line". CPython <b>compiles the whole file to bytecode</b> first, then the PVM <b>interprets that bytecode</b>. Both happen automatically when you type <code>python hello.py</code>.</li>
  <li><b>Who compiles:</b> the compiler built into CPython. <b>Who runs it:</b> the PVM, which is the evaluation loop of CPython, not a separate program.</li>
  <li><code>.pyc</code> files appear in <code>__pycache__</code> for imported modules, not normally for the main script.</li>
  <li>Python bytecode is specific to the Python version and is <b>not</b> the same as Java bytecode.</li>
  <li>Other implementations exist: PyPy uses a JIT compiler, Jython compiles Python to Java bytecode and runs on the JVM.</li>
 </ul>`
},
/* ------------------------------ JAVASCRIPT ------------------------------ */
js:{
 name:'JavaScript',srcTitle:'Source code: app.js (human readable)',bcTitle:'V8 Ignition bytecode (node --print-bytecode, simplified)',
 vmTitle:'node process: V8 JavaScript engine + Node.js runtime',
 code:['let a = 5;','let b = 3;','console.log("Sum =", a + b);'],
 bc:['LdaSmi [5]','Star r0             // a = 5','LdaSmi [3]','Star r1             // b = 3','LdaGlobal [console]','Star r3','GetNamedProperty r3, [log]','Star r2','LdaConstant ["Sum ="]','Star r4','Ldar r1','Add r0              // a + b','Star r5','CallProperty2 r2, r3, r4, r5','LdaUndefined','Return'],
 nodes:{dev:['👩‍💻','Programmer','writes code in an editor'],src:['📄','app.js','source code (text)'],comp:['⚙️','V8 parser + Ignition','tokens → AST → bytecode'],bc:['📦','Ignition bytecode','in memory only (no file)'],
  n1:['🌐','Execution context','global object, console'],n2:['🧠','Heap + call stack','objects and frames'],n3:['🔁','Ignition','bytecode interpreter'],n4:['🚀','JIT tiers','Sparkplug, Maglev, TurboFan'],
  cpu:['🔲','CPU','executes machine code'],os:['🛠️','Operating System','processes, system calls'],term:['⌨️','Terminal','console window'],screen:['🖥️','Monitor','pixels you can see']},
 steps:[
  {t:'The programmer writes the source code',who:'Programmer',d:'The programmer types JavaScript in an editor such as VS Code. It is plain human readable text.',show:['dev'],code:'type'},
  {t:'The code is saved as app.js',who:'Editor + Operating System (file system)',d:'The editor saves the text to disk as app.js, a sequence of bytes representing characters (UTF-8).',show:['src'],flow:['dev','src','save','text']},
  {t:'The programmer runs: node app.js',who:'Operating System',d:'JavaScript has no separate compile command and produces no bytecode file. The OS starts Node.js, which is a runtime made of the V8 engine (the same engine as in Google Chrome) plus libraries for files, network and the console. In a browser the same job is done by the browser\'s engine: V8 in Chrome and Edge, SpiderMonkey in Firefox, JavaScriptCore in Safari.',show:['os'],act:['os'],flow:['dev','os','node app.js','ctl'],cmd:'$ node app.js'},
  {t:'V8 parses the source code',who:'V8 parser',d:'V8 scans the text into tokens and parses it into an AST (abstract syntax tree). A SyntaxError is reported now, before any line runs. To start faster, V8 parses function bodies lazily, only when they are first needed.',show:['comp'],flow:['src','comp','app.js','text'],detail:{comp:'tokens → AST'}},
  {t:'The AST becomes bytecode in memory',who:'Ignition bytecode generator (V8)',d:'Ignition, V8\'s interpreter, generates bytecode from the AST. This bytecode exists only in memory and is thrown away when the program ends. You can print it with node --print-bytecode.',show:['bc'],flow:['comp','bc','bytecode','bc'],bcShow:true,detail:{comp:'tokens → AST → bytecode ✓'}},
  {t:'The execution context is created',who:'V8 + Node.js (the host)',d:'V8 creates the global object and the global execution context. Node.js adds host objects such as console and process. In a browser the host adds window and document instead. Note: console is provided by the host, not by the JavaScript language specification itself.',show:['vm','n1'],act:['vm','n1'],flow:['bc','n1','bytecode','bc']},
  {t:'Heap and call stack',who:'V8 memory management',d:'V8 allocates a heap for objects, cleaned automatically by its garbage collector (Orinoco), and a call stack where each function call pushes a frame. The script itself runs as the first frame.',show:['n2'],flow:['n1','n2','setup','bc'],detail:{n2:'call stack: [script]'}},
  {t:'Ignition executes the bytecode',who:'Ignition interpreter (V8)',d:'Ignition executes bytecode using an accumulator register. LdaSmi [5] loads 5 into the accumulator and Star r0 stores it in register r0, which holds a. The same happens for 3 into r1, which holds b.',show:['n3'],act:['n3'],flow:['n2','n3','execute','bc'],bc:[0,1,2,3],src:[0,1],detail:{n2:'a = 5, b = 3'}},
  {t:'Addition and the console.log call',who:'Ignition interpreter (V8)',d:'Ignition loads console, reads its log property, loads the string "Sum =", adds r0 and r1 to get 8, and calls log with two arguments.',act:['n3'],bc:[4,5,6,7,8,9,10,11,12,13],src:[2],detail:{n3:'Add → 8'}},
  {t:'JIT compilation is only for hot code',who:'V8 JIT compilers',d:'V8 watches which functions run often. Hot code is compiled to machine code by faster tiers (Sparkplug and Maglev) and by the optimizing compiler TurboFan. Our three line program runs only once, so Ignition simply interprets it. That is why the JIT is shown with a dashed line.',show:['n4'],flow:['n3','n4','only if hot','native',true]},
  {t:'The CPU executes the machine instructions',who:'CPU',d:'Ignition itself is native machine code built into V8, so the CPU runs Ignition\'s instructions to carry out each bytecode. JIT compiled code runs directly on the CPU.',show:['cpu'],act:['cpu'],flow:['n3','cpu','machine code','native']},
  {t:'console.log writes to standard output',who:'console.log → process.stdout → libuv → OS',d:'console.log formats its arguments as "Sum = 8" followed by a newline. Node writes this to process.stdout as UTF-8 bytes, and Node\'s I/O library libuv performs the write() system call to the operating system.',act:['cpu','os'],flow:['cpu','os','write(stdout, bytes)','bytes'],src:[2]},
  ...outputTail(),
  {t:'The program finishes',who:'Node.js + Operating System',d:'The script returns undefined. The event loop finds no timers or pending I/O, so Node exits and the OS ends the process with exit code 0.',act:['os'],bc:[14,15],cmd:'(process exited with code 0)',info:true}
 ],
 notes:`<ul>
  <li><span class="fix">Correction:</span> JavaScript has <b>no JVM and no PVM</b>. It runs on a <b>JavaScript engine</b>: V8 (Chrome, Edge, Node.js), SpiderMonkey (Firefox) or JavaScriptCore (Safari).</li>
  <li><b>Who compiles:</b> the engine itself, at run time (parser plus bytecode generator). <b>Who runs it:</b> the engine's interpreter (Ignition in V8), with JIT compilers for hot code.</li>
  <li>No bytecode file is created. The programmer only ships the source <code>.js</code> file.</li>
  <li>"JavaScript is purely interpreted" is outdated. Every major engine uses JIT compilation.</li>
  <li><code>console</code>, <code>window</code> and <code>document</code> are provided by the host environment (browser or Node.js), not by the language standard ECMAScript.</li>
 </ul>`
},
/* ------------------------------ C# ------------------------------ */
cs:{
 name:'C#',srcTitle:'Source code: Program.cs (human readable)',bcTitle:'CIL (Intermediate Language) in Hello.dll (simplified)',
 vmTitle:'dotnet process: CLR (Common Language Runtime)',
 code:['using System;','class Hello {','    static void Main() {','        int a = 5, b = 3;','        Console.WriteLine("Sum = " + (a + b));','    }','}'],
 bc:['ldc.i4.5','stloc.0             // a = 5','ldc.i4.3','stloc.1             // b = 3','ldstr    "Sum = "','ldloc.0','ldloc.1','add                 // a + b','box      System.Int32','call     String::Concat(object, object)','call     Console::WriteLine(string)','ret'],
 nodes:{dev:['👩‍💻','Programmer','writes code in an IDE'],src:['📄','Program.cs','source code (text)'],comp:['⚙️','Roslyn (csc)','C# compiler (.NET SDK)'],bc:['📦','Hello.dll','CIL + metadata (assembly)'],
  n1:['📥','Assembly loader','loads .dll files'],n2:['🧾','Type loader','metadata, method tables'],n3:['🧠','Managed memory','stack + GC heap'],n4:['🚀','RyuJIT','IL → native code'],
  cpu:['🔲','CPU','executes machine code'],os:['🛠️','Operating System','processes, system calls'],term:['⌨️','Terminal','console window'],screen:['🖥️','Monitor','pixels you can see']},
 steps:[
  {t:'The programmer writes the source code',who:'Programmer',d:'The programmer types C# code in an IDE such as Visual Studio, Rider or VS Code. It is plain human readable text.',show:['dev'],code:'type'},
  {t:'The code is saved as Program.cs',who:'Editor + Operating System (file system)',d:'The editor saves the text as Program.cs inside a project (Hello.csproj). On disk it is a sequence of bytes representing characters.',show:['src'],flow:['dev','src','save','text']},
  {t:'dotnet build runs the C# compiler',who:'Roslyn, the C# compiler (csc), part of the .NET SDK',d:'Roslyn reads all source files of the project, tokenizes, parses and type checks them. If there is any compile error the build stops here and no program is produced.',show:['comp'],flow:['src','comp','Program.cs','text'],cmd:'$ dotnet build',detail:{comp:'tokens → syntax tree → type check ✓'}},
  {t:'The output is CIL inside Hello.dll',who:'Roslyn',d:'The result is an assembly, Hello.dll, which contains CIL (Common Intermediate Language, also called MSIL or simply IL) plus metadata that describes every type and method. CIL is the .NET equivalent of Java bytecode and is independent of the CPU.',show:['bc'],flow:['comp','bc','CIL','bc'],bcShow:true},
  {t:'dotnet run starts the CLR',who:'.NET host + Operating System',d:'The OS starts the .NET host process, which loads the CLR (Common Language Runtime). C# does not use the JVM. The CLR plays that role for all .NET languages such as C#, F# and VB.NET.',show:['os','vm'],act:['os','vm'],flow:['dev','os','dotnet run','ctl'],cmd:'$ dotnet run'},
  {t:'The assembly is loaded',who:'Assembly loader (CLR)',d:'The CLR loads Hello.dll and the framework assemblies it needs, such as System.Console.dll and System.Private.CoreLib.dll.',show:['n1'],flow:['bc','n1','Hello.dll','bc']},
  {t:'Types and metadata are prepared',who:'CLR type loader',d:'Using the metadata, the CLR builds internal structures (method tables) for the class Hello and its method Main, and checks that references between assemblies resolve correctly.',show:['n2'],flow:['n1','n2','metadata','bc']},
  {t:'The memory environment is created',who:'CLR memory manager + Garbage Collector',d:'Each thread gets a stack for method frames and local variables such as a and b. Objects such as strings live on the managed heap, which the garbage collector cleans automatically.',show:['n3'],flow:['n2','n3','prepare','bc'],detail:{n3:'stack: Main() | GC heap'}},
  {t:'The JIT compiles Main into native code',who:'RyuJIT, the Just In Time compiler',d:'The standard CoreCLR runtime does not interpret IL. Just before Main runs for the first time, RyuJIT compiles its IL into native machine code. With tiered compilation it first makes quick code, then recompiles hot methods with full optimization. Ahead of time options such as ReadyToRun and Native AOT also exist.',show:['n4'],act:['n4'],flow:['n3','n4','Main IL','bc'],detail:{n4:'Main: IL → x64 / ARM64 code'}},
  {t:'The CPU runs the native code for Main',who:'CPU',d:'The CPU now executes the native instructions that RyuJIT produced from ldc.i4.5, stloc.0 and the rest. The values 5 and 3 are stored for a and b, usually in CPU registers.',show:['cpu'],act:['cpu'],flow:['n4','cpu','machine code','native'],bc:[0,1,2,3],src:[3],detail:{n3:'Main frame: a = 5, b = 3'}},
  {t:'Addition and building the string',who:'CPU running JIT compiled code',d:'add computes 8. box wraps the int as an object so that String.Concat can join "Sum = " and 8 into a new string "Sum = 8" on the managed heap.',act:['cpu'],bc:[4,5,6,7,8,9],src:[4]},
  {t:'Console.WriteLine writes to standard output',who:'Console.WriteLine → OS system call',d:'Console.WriteLine encodes the string into bytes (UTF-8 by default on Linux and macOS, the console code page on Windows) and calls the operating system: write() on Linux and macOS, WriteFile on Windows.',act:['cpu','os'],flow:['cpu','os','write(stdout, bytes)','bytes'],bc:[10],src:[4]},
  ...outputTail(),
  {t:'The program finishes',who:'CLR + Operating System',d:'ret ends Main. The CLR shuts down and the OS ends the process with exit code 0.',act:['os'],bc:[11],src:[5],cmd:'(process exited with code 0)',info:true}
 ],
 notes:`<ul>
  <li><span class="fix">Correction:</span> C# does <b>not</b> use the JVM. It uses the <b>CLR</b> (Common Language Runtime) of .NET.</li>
  <li><b>Who compiles:</b> Roslyn (<code>csc</code>) turns <code>.cs</code> into CIL inside a <code>.dll</code> or <code>.exe</code> assembly. <b>Who runs it:</b> the CLR, whose JIT compiler (RyuJIT) turns each method into native code the first time it is called.</li>
  <li>So C# is compiled twice: source to IL at build time, then IL to machine code at run time.</li>
  <li>The same IL runs on Windows, Linux and macOS with the matching .NET runtime.</li>
  <li>Native AOT can compile everything to machine code in advance, so no JIT is needed at run time.</li>
 </ul>`
}
};

/* ===================================================================
   TAB 1 RENDERING (GSAP)
   =================================================================== */
const stage=document.getElementById('stage');
const IDS=['dev','src','comp','bc','n1','n2','n3','n4','cpu','os','term','screen'];
const INTRO='This animation follows one tiny program from the moment a programmer types it until its result appears on the monitor. You will see who is responsible at every stage: the programmer, the compiler, the virtual machine or engine, the CPU, the operating system, the terminal and the monitor.';
let L=LANGS.java,typeTok=0,prevVis=new Set(),prevDec='none',cpuTimer=null,lastEdges=[];

function el(id){return document.getElementById('n-'+id)}
function setLang(key){
  L=LANGS[key];
  document.querySelectorAll('#langChips .chip').forEach(c=>c.classList.toggle('on',c.dataset.lang===key));
  IDS.forEach(id=>{const [ic,t,s]=L.nodes[id];el(id).innerHTML=`<div class="ic">${ic}</div><div class="nt">${esc(t)}</div><div class="ns">${esc(s)}</div><div class="nd"></div>`});
  $('#vmTitle').textContent=L.vmTitle;$('#srcTitle').textContent=L.srcTitle;$('#bcTitle').textContent=L.bcTitle;
  $('#noteLang').textContent=L.name;$('#notesBody').innerHTML=L.notes;
  prevVis=new Set();p1.reset();
}
function boxOf(e){let x=0,y=0,n=e;while(n&&n!==stage){x+=n.offsetLeft;y+=n.offsetTop;n=n.offsetParent}return{x,y,w:e.offsetWidth,h:e.offsetHeight}}
function edgePoint(b,tx,ty){
  const cx=b.x+b.w/2,cy=b.y+b.h/2,dx=tx-cx,dy=ty-cy;
  if(!dx&&!dy)return{x:cx,y:cy};
  const s=Math.min(Math.abs((b.w/2+6)/(dx||1e-9)),Math.abs((b.h/2+6)/(dy||1e-9)));
  return{x:cx+dx*s,y:cy+dy*s};
}
function edgeGeom(f,t){
  const a=boxOf(el(f)),b=boxOf(el(t));
  const p=edgePoint(a,b.x+b.w/2,b.y+b.h/2),q=edgePoint(b,a.x+a.w/2,a.y+a.h/2);
  const dx=q.x-p.x,dy=q.y-p.y,len=Math.hypot(dx,dy)||1,nx=-dy/len,ny=dx/len,bend=Math.min(34,len*.14);
  const c1={x:p.x+dx*.3+nx*bend,y:p.y+dy*.3+ny*bend},c2={x:p.x+dx*.7+nx*bend,y:p.y+dy*.7+ny*bend};
  return{p,q,c1,c2};
}
const pathD=(g,ox=0,oy=0)=>`M${g.p.x-ox} ${g.p.y-oy} C${g.c1.x-ox} ${g.c1.y-oy} ${g.c2.x-ox} ${g.c2.y-oy} ${g.q.x-ox} ${g.q.y-oy}`;

function arrowHead(g,color){
  const ang=Math.atan2(g.q.y-g.c2.y,g.q.x-g.c2.x),s=11;
  const pts=[[g.q.x,g.q.y],[g.q.x-s*Math.cos(ang-0.45),g.q.y-s*Math.sin(ang-0.45)],[g.q.x-s*Math.cos(ang+0.45),g.q.y-s*Math.sin(ang+0.45)]];
  const pg=document.createElementNS('http://www.w3.org/2000/svg','polygon');
  pg.setAttribute('points',pts.map(p=>p.join(',')).join(' '));pg.setAttribute('style',`fill:${color}`);return pg;
}
function drawEdges(edges,animateLast,speed=1){
  const gEl=document.getElementById('edgeG');gEl.innerHTML='';
  edges.forEach((e,i)=>{
    const [f,t,label,kind,dashed]=e,g=edgeGeom(f,t),color=`var(--k-${kind})`;
    const grp=document.createElementNS('http://www.w3.org/2000/svg','g');
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d',pathD(g));path.setAttribute('class','edge');path.setAttribute('style',`stroke:${color}`);
    grp.appendChild(path);const head=arrowHead(g,color);grp.appendChild(head);gEl.appendChild(grp);
    if(animateLast&&i===edges.length-1){
      const len=path.getTotalLength();
      gsap.fromTo(path,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:1.3/speed,ease:'power2.inOut',onComplete:()=>{path.style.strokeDasharray=dashed?'7 7':'none'}});
      gsap.fromTo(head,{autoAlpha:0,scale:0,transformOrigin:'50% 50%'},{autoAlpha:1,scale:1,duration:.4,delay:1.2/speed,ease:'back.out(3)'});
    }else if(dashed)path.style.strokeDasharray='7 7';
  });
}
function animatePacket(f,t,label,kind,speed){
  const g=edgeGeom(f,t);
  const pk=document.createElement('div');pk.className='packet';pk.textContent=label;pk.style.background=`var(--k-${kind})`;
  stage.appendChild(pk);
  const pw=pk.offsetWidth,ph=pk.offsetHeight;
  gsap.set(pk,{x:g.p.x-pw/2,y:g.p.y-ph/2,scale:.3,autoAlpha:0});
  const tl=gsap.timeline({onComplete:()=>pk.remove()});
  tl.to(pk,{scale:1,autoAlpha:1,duration:.25/speed,ease:'back.out(3)'})
    .to(pk,{motionPath:{path:pathD(g,pw/2,ph/2)},duration:1.3/speed,ease:'power1.inOut'})
    .add(()=>{
      const sp=document.createElement('div');sp.className='spark';sp.style.left=g.q.x+'px';sp.style.top=g.q.y+'px';sp.style.borderColor=`var(--k-${kind})`;stage.appendChild(sp);
      gsap.fromTo(sp,{scale:.3,opacity:1},{scale:2.6,opacity:0,duration:.6,ease:'power2.out',onComplete:()=>sp.remove()});
      const tgt=el(t);gsap.fromTo(tgt,{scale:1},{scale:1.06,duration:.14,yoyo:true,repeat:1,ease:'power1.out'});
    })
    .to(pk,{scale:.3,autoAlpha:0,duration:.2/speed});
}
function renderCode(visibleChars,hl){
  const body=$('#srcBody');
  if(visibleChars===0){body.innerHTML='<div class="empty">Empty editor. The programmer has not typed anything yet.</div>';return}
  const full=L.code.join('\n'),lines=full.slice(0,visibleChars).split('\n');
  body.innerHTML=lines.map((l,i)=>`<div class="ln${hl&&hl.includes(i)?' hl':''}"><span class="no">${i+1}</span><span>${esc(l)}${(visibleChars<full.length&&i===lines.length-1)?'<span class="cursor">&nbsp;</span>':''}</span></div>`).join('');
}
function renderBC(show,hl,animate){
  const body=$('#bcBody');
  if(!show){body.innerHTML='<div class="empty">No bytecode yet. It appears after the compiler runs.</div>';return}
  const isNew=!body.querySelector('.ln');
  body.innerHTML=L.bc.map((l,i)=>`<div class="ln${hl&&hl.includes(i)?' hl':''}"><span class="no">${i}</span><span>${esc(l)}</span></div>`).join('');
  if(animate&&isNew)gsap.from(body.querySelectorAll('.ln'),{x:-24,autoAlpha:0,duration:.35,stagger:.06,ease:'power2.out'});
  const h=body.querySelector('.hl');if(h){h.scrollIntoView({block:'nearest'});if(animate)gsap.from(body.querySelectorAll('.hl'),{backgroundColor:'rgba(242,165,22,.6)',duration:.8,stagger:.08})}
}
function renderConsole(lines,animate,newOut){
  const body=$('#conBody');
  if(!lines.length){body.innerHTML='<div class="empty">The screen is blank.</div>';return}
  body.innerHTML=lines.map(l=>`<div class="ln"><span class="${l.c}">${esc(l.s)}</span></div>`).join('');
  if(animate&&newOut){const last=body.lastElementChild;gsap.fromTo(last,{autoAlpha:0,x:-10,scale:1.3,transformOrigin:'0 50%'},{autoAlpha:1,x:0,scale:1,duration:.6,ease:'back.out(2)'})}
}

/* ---------- Byte decoder: numbers become characters ---------- */
const DEC=[['S',83],['u',117],['m',109],['␣',32,'space'],['=',61],['␣',32,'space'],['8',56],['↵',10,'newline']];
function cellHTML(d,mode){return mode==='b'?`<div class="num">${d[1]}</div><div class="sub">byte</div>`:`<div class="ch">${esc(d[0])}</div><div class="sub">${d[2]||d[1]}</div>`}
function renderDecoder(state,animate){
  const host=$('#decCells'),label=$('#decLabel');
  if(state==='none'){host.innerHTML='<div class="dec-empty">Nothing yet. Bytes appear here when the program writes its output.</div>';label.textContent='';prevDec=state;return}
  label.textContent=state==='bytes'?'The OS and terminal receive only numbers (UTF-8 bytes). The computer never stores the letter S, it stores 83.':'The terminal looks up each number in a font and draws its glyph. Now a human can read it. (On Windows a newline is usually sent as 13 10.)';
  const changed=state!==prevDec;prevDec=state;
  if(state==='bytes'){
    host.innerHTML=DEC.map(d=>`<div class="cell b">${cellHTML(d,'b')}</div>`).join('');
    if(animate&&changed)gsap.fromTo(host.children,{y:30,scale:0,autoAlpha:0},{y:0,scale:1,autoAlpha:1,duration:.55,stagger:.08,ease:'back.out(2.4)'});
  }else{
    if(animate&&changed){
      host.innerHTML=DEC.map(d=>`<div class="cell b">${cellHTML(d,'b')}</div>`).join('');
      [...host.children].forEach((c,i)=>{
        gsap.timeline({delay:.15+i*.13})
          .to(c,{rotationY:90,duration:.18,ease:'power1.in'})
          .add(()=>{c.className='cell c';c.innerHTML=cellHTML(DEC[i],'c')})
          .to(c,{rotationY:0,duration:.35,ease:'back.out(2.5)'});
      });
    }else host.innerHTML=DEC.map(d=>`<div class="cell c">${cellHTML(d,'c')}</div>`).join('');
  }
}

function render1(k,animate){
  typeTok++;clearInterval(cpuTimer);
  stage.querySelectorAll('.packet,.spark').forEach(p=>{gsap.killTweensOf(p);p.remove()});
  const steps=L.steps,vis=new Set(),edges=[],detail={},con=[];let bcShow=false,typed=false,dec='none';
  for(let i=0;i<k;i++){
    const s=steps[i];
    (s.show||[]).forEach(x=>vis.add(x));
    if(s.flow){edges.push(s.flow);if(s.flow[3]==='bytes')dec='bytes';if(s.flow[3]==='pixels')dec='chars'}
    Object.assign(detail,s.detail||{});
    if(s.bcShow)bcShow=true;
    if(s.code==='type')typed=true;
    if(s.cmd)con.push({s:s.cmd,c:s.info?'cinfo':'cmd'});
    if(s.out)con.push({s:s.out,c:'cout'});
  }
  const cur=k>0?steps[k-1]:null,spd=p1.speed;
  gsap.to('#blank',{autoAlpha:k===0?1:0,duration:.35});
  IDS.forEach((id,idx)=>{
    const e=el(id),v=vis.has(id);
    e.classList.remove('act');e.querySelector('.nd').textContent=detail[id]||'';
    gsap.killTweensOf(e);
    if(v&&!prevVis.has(id)&&animate)gsap.fromTo(e,{autoAlpha:0,scale:.35,y:36,rotation:-8},{autoAlpha:1,scale:1,y:0,rotation:0,duration:.85,delay:.05,ease:'back.out(2.2)'});
    else gsap.set(e,{autoAlpha:v?1:0,scale:1,y:0,rotation:0});
  });
  const vm=$('#n-vm');vm.classList.remove('act');
  if(vis.has('vm')&&!prevVis.has('vm')&&animate)gsap.fromTo(vm,{autoAlpha:0,scale:.9},{autoAlpha:1,scale:1,duration:.7,ease:'back.out(1.6)'});
  else gsap.set(vm,{autoAlpha:vis.has('vm')?1:0,scale:1});
  prevVis=vis;
  if(cur){
    const act=cur.act||cur.show||(cur.flow?[cur.flow[1]]:[]);
    act.forEach(id=>{if(id==='vm')vm.classList.add('act');else if(el(id))el(id).classList.add('act')});
    if(act.includes('cpu')){const nd=el('cpu').querySelector('.nd'),bits=()=>Array.from({length:8},()=>Math.random()<.5?0:1).join('');cpuTimer=setInterval(()=>{nd.textContent=bits()+' '+bits()},110)}
  }
  // narration
  $('#nNo').textContent=k;$('#nShape').className='nshape shape-'+(k%4);
  $('#nWho').textContent=cur?'Responsible: '+cur.who:'Ready';
  $('#nTitle').textContent=cur?cur.t:'Choose a language and press Play';
  $('#nText').textContent=cur?cur.d:INTRO;
  if(animate){
    gsap.fromTo('#nShape',{rotation:-140,scale:.4},{rotation:0,scale:1,duration:1,ease:'elastic.out(1,.55)'});
    gsap.fromTo(['#nWho','#nTitle','#nText'],{y:16,autoAlpha:0},{y:0,autoAlpha:1,duration:.5,stagger:.08,ease:'power3.out'});
  }
  // panels
  const full=L.code.join('\n').length;
  if(cur&&cur.code==='type'&&animate){
    const tok=typeTok,dur=2400/spd,t0=performance.now();
    const tick=()=>{if(tok!==typeTok)return;const f=Math.min(1,(performance.now()-t0)/dur);renderCode(Math.floor(full*f),null);if(f<1)requestAnimationFrame(tick)};
    tick();
  }else renderCode(typed?full:0,cur?cur.src:null);
  renderBC(bcShow,cur?cur.bc:null,animate);
  renderConsole(con,animate,!!(cur&&(cur.out||cur.cmd)));
  renderDecoder(dec,animate);
  // edges and travelling packet
  if(animate&&cur&&cur.flow){
    drawEdges(edges,true,spd);
    const [f,t,label,kind]=cur.flow;animatePacket(f,t,label,kind,spd);
  }else drawEdges(edges,false);
  lastEdges=edges;
}
window.addEventListener('resize',()=>drawEdges(lastEdges,false));
const p1=new Player($('#c1'),{total:()=>L.steps.length,render:render1,baseMs:()=>6500,dots:$('#dots1')});
document.querySelectorAll('#langChips .chip').forEach(c=>c.onclick=()=>{if(L!==LANGS[c.dataset.lang])setLang(c.dataset.lang)});

/* ===================================================================
   TAB 2 PART A: Butter chicken kitchen
   =================================================================== */
const ING=[
  {e:'🍗',n:'Chicken',s:'Marinate and cook the chicken pieces'},
  {e:'🧈',n:'Butter',s:'Melt butter in the pan'},
  {e:'🍅',n:'Tomato puree',s:'Add tomato puree and simmer'},
  {e:'🌶️',n:'Garam masala',s:'Add garam masala'},
  {e:'🥛',n:'Fresh cream',s:'Finish with fresh cream'}
];
function ingList(mistake){return ING.map((x,i)=>(mistake&&i===3)?{e:'❓',n:'Garam masaala',s:'Add garam masaala (misspelled)',bad:true}:x)}

function kitchenEvents(type,mistake){
  const R=ingList(mistake),ev=[];
  if(type==='int'){
    for(let i=0;i<5;i++){
      const g=R[i];
      ev.push({fx:'read',log:`Reads only step ${i+1}: "${g.s}".`,fn:s=>{s.hl=i;s.pos='k'}});
      ev.push({fx:'walk',log:`Walks to the market to buy ${g.n}. (trip ${i+1})`,fn:s=>{s.pos='m';s.trips++}});
      if(g.bad){
        ev.push({fx:'err',err:true,log:'Shopkeeper: "Garam masaala? No such item!" Cooking stops at step 4. Steps 1 to 3 are already in the pot, so the dish is half cooked and the effort is wasted.',fn:s=>{s.bad=i;s.err=true;s.status='Error at step 4 (found while cooking)'}});
        return ev;
      }
      ev.push({fx:'buy',log:`Buys ${g.n} ${g.e}.`,fn:s=>{s.carry=[g.e]}});
      ev.push({fx:'walk',log:'Walks back to the kitchen.',fn:s=>{s.pos='k'}});
      ev.push({fx:'cook',log:`Cooks step ${i+1} with ${g.n}.`,fn:(s,t)=>{s.pot.push(g.e);s.carry=[];s.done.push(i);if(!s.first)s.first=t}});
    }
    ev.push({fx:'ready',ok:true,log:'Butter chicken is ready! It needed 5 separate market trips.',fn:s=>{s.status='Dish ready';s.hl=-1;s.ready=true}});
  }else{
    ev.push({fx:'readall',log:'Reads the WHOLE recipe from start to end before doing anything else.',fn:s=>{s.hl='all'}});
    for(let i=0;i<5;i++){
      const g=R[i];
      if(g.bad){
        ev.push({fx:'err',err:true,log:'While writing the list, the chef checks the shop catalogue: "Garam masaala" does not exist. The error is reported BEFORE any cooking starts. Nothing is wasted. Fix the recipe and start again.',fn:s=>{s.list.push({...g,x:true});s.err=true;s.status='Error at step 4 (found before cooking)'}});
        return ev;
      }
      ev.push({fx:'list',log:`Writes "${g.n}" on the shopping list (checked against the shop catalogue).`,fn:s=>{s.list.push(g)}});
    }
    ev.push({fx:'walk',log:'Walks to the market ONCE with the complete list. (trip 1)',fn:s=>{s.pos='m';s.trips=1}});
    ev.push({fx:'buy',log:'Buys all 5 items in one go.',fn:s=>{s.carry=R.map(x=>x.e)}});
    ev.push({fx:'walk',log:'Walks back with everything needed.',fn:s=>{s.pos='k'}});
    for(let i=0;i<5;i++){
      const g=R[i];
      ev.push({fx:'cook',log:`Cooks step ${i+1} immediately, the ${g.n} is already at hand.`,fn:(s,t)=>{s.hl=i;s.pot.push(g.e);s.carry=s.carry.filter(c=>c!==g.e);s.done.push(i);if(!s.first)s.first=t}});
    }
    ev.push({fx:'ready',ok:true,log:'Butter chicken is ready! Only 1 market trip, and cooking never had to stop.',fn:s=>{s.status='Dish ready';s.hl=-1;s.ready=true}});
  }
  return ev;
}
function kitchenState(ev,n){
  const s={pos:'k',trips:0,carry:[],pot:[],done:[],hl:-1,list:[],bad:-1,first:0,status:'Waiting',log:'Waiting to start.',cls:'',err:false,ready:false,fx:null};
  const m=Math.min(n,ev.length);
  for(let j=0;j<m;j++)ev[j].fn(s,j+1);
  if(m>0){s.log=ev[m-1].log;s.cls=ev[m-1].err?'err':(ev[m-1].ok?'ok':'');if(s.status==='Waiting')s.status='Working'}
  s.fx=(n>0&&n<=ev.length)?ev[n-1].fx:null;
  s.time=m;return s;
}
function buildKLane(root,type){
  const chef=type==='int'?'👨‍🍳':'👩‍🍳';
  root.className='lane '+type;
  root.innerHTML=`
   <div class="lane-head"><div class="bshape ${type}">${chef}</div><div><b>${type==='int'?'Interpreter style chef':'Compiler style chef'}</b><small>${type==='int'?'Read one step, fetch one item, cook, repeat':'Read everything, full list, one trip, cook all'}</small></div></div>
   <div class="track">
     <div class="place kitchen"><span class="big">🍳</span>Kitchen<div class="pot"></div></div>
     <div class="road"></div>
     <div class="place market"><span class="big">🏪</span>Market</div>
     <div class="chef"><div class="face">${chef}</div><div class="carry"></div></div>
     <div class="ready">🍛 Dish ready!</div><div class="stamp">✖ Error!</div>
   </div>
   <div class="cards"><div class="card"><h5>📜 Recipe (the "source code")</h5><ol class="recipe"></ol></div><div class="card"><h5>🧾 Shopping list</h5><div class="list"></div></div></div>
   <div class="log"></div>
   <div class="stats">
     <div class="stat"><b class="s-trips">0</b><span>Market trips</span></div>
     <div class="stat"><b class="s-time">0</b><span>Time ticks used</span></div>
     <div class="stat"><b class="s-first">-</b><span>First cooking at tick</span></div>
     <div class="stat"><b class="s-status" style="font-size:13px">Waiting</b><span>Status</span></div>
   </div>`;
  const q=c=>root.querySelector(c);
  root._r={track:q('.track'),chef:q('.chef'),face:q('.face'),carry:q('.carry'),pot:q('.pot'),recipe:q('.recipe'),list:q('.list'),log:q('.log'),ready:q('.ready'),stamp:q('.stamp'),
    trips:q('.s-trips'),time:q('.s-time'),first:q('.s-first'),status:q('.s-status')};
}
function updKLane(root,type,s,R,animate,spd){
  if(!root._r)buildKLane(root,type);
  const r=root._r;
  r.track.querySelectorAll('.fly,.steam,.conf').forEach(x=>x.remove());
  r.recipe.innerHTML=R.map((g,i)=>{let c='';if(s.hl==='all')c='all';else if(s.hl===i)c='hl';if(s.done.includes(i))c+=' ok';if(type==='int'&&s.bad===i)c='x';return`<li class="${c}">${g.e} ${esc(g.s)}</li>`}).join('');
  r.pot.innerHTML=s.pot.length?s.pot.map(e=>`<span>${e}</span>`).join(''):'<span class="e">empty pot</span>';
  r.carry.innerHTML=s.carry.map(e=>`<span>${e}</span>`).join('');
  r.list.innerHTML=type==='cmp'
    ?(s.list.length?'<ul>'+s.list.map(g=>`<li class="${g.x?'x':'ok'}">${g.e} ${esc(g.n)}${g.x?' ✗ not in shop':' ✓'}</li>`).join('')+'</ul>':'<span class="muted mono">(empty)</span>')
    :'<span class="muted">No list. This chef decides what to buy one step at a time, so there is never a complete view of the recipe.</span>';
  r.log.textContent=s.log;r.log.className='log '+s.cls;
  r.trips.textContent=s.trips;r.time.textContent=s.time;r.first.textContent=s.first||'-';r.status.textContent=s.status;
  const left=s.pos==='k'?'39%':'61%';
  gsap.killTweensOf([r.chef,r.face]);
  if(animate&&s.fx==='walk'){
    gsap.to(r.chef,{left,duration:1/spd,ease:'power2.inOut'});
    gsap.fromTo(r.face,{y:0,rotation:0},{keyframes:{y:[0,-12,0,-12,0,-12,0],rotation:[0,-8,0,8,0,-8,0]},duration:1/spd,ease:'none'});
  }else gsap.set(r.chef,{left});
  gsap.set(r.ready,{autoAlpha:s.ready?1:0,scale:1});gsap.set(r.stamp,{autoAlpha:s.err?1:0,scale:1});
  if(!animate)return;
  const fx=s.fx;
  if(fx==='read'){const li=r.recipe.querySelector('.hl');if(li)gsap.fromTo(li,{scale:.9,x:-10},{scale:1,x:0,duration:.5,ease:'back.out(3)'})}
  if(fx==='readall')gsap.fromTo(r.recipe.children,{x:-14,autoAlpha:.2},{x:0,autoAlpha:1,stagger:.08,duration:.4,ease:'power2.out'});
  if(fx==='list'){const items=r.list.querySelectorAll('li');pop(items[items.length-1])}
  if(fx==='buy')gsap.fromTo(r.carry.children,{scale:0,y:-20},{scale:1,y:0,stagger:.07,duration:.5,ease:'back.out(3)'});
  if(fx==='cook'){
    const spans=r.pot.querySelectorAll('span'),last=spans[spans.length-1];
    const from=relPos(r.chef,r.track),to=relPos(last,r.track);
    gsap.set(last,{autoAlpha:0});
    const f=document.createElement('div');f.className='fly';f.textContent=s.pot[s.pot.length-1];r.track.appendChild(f);
    gsap.set(f,{x:from.x-12,y:from.y-30});
    gsap.to(f,{motionPath:{path:[{x:from.x-12,y:from.y-30},{x:(from.x+to.x)/2-12,y:Math.min(from.y,to.y)-70},{x:to.x-12,y:to.y-14}],curviness:1.3},rotation:360,duration:.8/spd,ease:'power1.inOut',onComplete:()=>{
      f.remove();gsap.fromTo(last,{autoAlpha:0,scale:2},{autoAlpha:1,scale:1,duration:.45,ease:'back.out(3)'});
      for(let i=0;i<3;i++){const st=document.createElement('div');st.className='steam';st.textContent='💨';st.style.left=(to.x-10+i*10-10)+'px';st.style.top=(to.y-20)+'px';r.track.appendChild(st);
        gsap.fromTo(st,{y:0,autoAlpha:.9,scale:.5},{y:-46,autoAlpha:0,scale:1.2,duration:1,delay:i*.12,ease:'power1.out',onComplete:()=>st.remove()})}
    }});
  }
  if(fx==='err'){shake(root);pop(r.stamp)}
  if(fx==='ready'){pop(r.ready);const p=relPos(r.pot,r.track);confetti(r.track,p.x,p.y)}
}
const kMistake=$('#kMistake');
function kEv(){return{int:kitchenEvents('int',kMistake.checked),cmp:kitchenEvents('cmp',kMistake.checked)}}
function renderKitchen(k,animate){
  const E=kEv(),R=ingList(kMistake.checked);
  updKLane($('#kInt'),'int',kitchenState(E.int,k),R,animate,p2.speed);
  updKLane($('#kCmp'),'cmp',kitchenState(E.cmp,k),R,animate,p2.speed);
}
const p2=new Player($('#c2'),{unit:'Tick',total:()=>{const E=kEv();return Math.max(E.int.length,E.cmp.length)},render:renderKitchen,baseMs:()=>1700});
kMistake.onchange=()=>p2.reset();

/* ===================================================================
   TAB 2 PART B: Code version
   =================================================================== */
function program(mistake){
  return [
   {src:'print("Order received")',tr:['PUSH "Order received"','CALL print'],out:'Order received'},
   {src:'price = 250',tr:['MOV  [price], 250'],v:['price',250]},
   {src:'print("Price:", price)',tr:['PUSH "Price:"','PUSH [price]','CALL print'],out:'Price: 250'},
   mistake?{src:'total = price * qtty',tr:['MOV  R1, [price]','MUL  R1, [qtty]   ✗ unknown name'],bad:true}
          :{src:'total = price * 2',tr:['MOV  R1, [price]','MUL  R1, 2','MOV  [total], R1'],v:['total',500]},
   {src:'print("Total:", total)',tr:['PUSH "Total:"','PUSH [total]','CALL print'],out:'Total: 500'}
  ];
}
function codeEvents(type,mistake){
  const P=program(mistake),ev=[];
  const exec=(s,i,t)=>{const p=P[i];if(p.out){s.out.push({t:p.out});if(!s.first)s.first=t}if(p.v)s.vars[p.v[0]]=p.v[1];s.ls[i]='ok'};
  if(type==='int'){
    for(let i=0;i<5;i++){
      const p=P[i];
      ev.push({fx:'trans',n:p.tr.length,log:`Translates line ${i+1} only: ${p.src}`,fn:s=>{s.hl=i;s.trans=p.tr;s.count++}});
      if(p.bad){
        ev.push({fx:'err',err:true,log:"Executes line 4 and fails: NameError, name 'qtty' is not defined. Lines 1 to 3 have ALREADY run and printed output. Line 5 never runs.",fn:s=>{s.ls[i]='x';s.out.push({t:"NameError: name 'qtty' is not defined (line 4)",e:true});s.err=true;s.status='Stopped at line 4 (runtime error)'}});
        return ev;
      }
      ev.push({fx:'exec',out:!!p.out,log:`Executes line ${i+1} immediately${p.out?' and prints output':''}.`,fn:(s,t)=>exec(s,i,t)});
    }
    ev.push({fx:'done',ok:true,log:'Program finished. Nothing was saved, so the next run must translate every line again.',fn:s=>{s.hl=-1;s.trans=[];s.status='Finished'}});
  }else{
    for(let i=0;i<5;i++){
      const p=P[i];
      if(p.bad){
        ev.push({fx:'err',err:true,log:"Checks line 4: 'qtty' is not declared. COMPILE ERROR. No executable is created and not a single line runs, so no output appears at all.",fn:s=>{s.hl=i;s.target.push(...p.tr);s.ls[i]='x';s.count++;s.err=true;s.status='Compile error at line 4 (nothing ran)'}});
        return ev;
      }
      ev.push({fx:'trans',n:p.tr.length,log:`Translates and checks line ${i+1}: ${p.src}`,fn:s=>{s.hl=i;s.target.push(...p.tr);s.ls[i]='t';s.count++}});
    }
    ev.push({fx:'exe',log:'All lines translated without errors. The complete translation is saved as program.exe.',fn:s=>{s.hl=-1;s.exe=true}});
    ev.push({fx:'run',log:'Runs program.exe: the CPU executes the ready made machine code. All output appears quickly because no translation is needed now.',fn:(s,t)=>{for(let i=0;i<5;i++)exec(s,i,t)}});
    ev.push({fx:'done',ok:true,log:'Program finished. program.exe can be run again and again without translating.',fn:s=>{s.status='Finished'}});
  }
  return ev;
}
function codeState(ev,n){
  const s={hl:-1,trans:[],target:[],out:[],vars:{},ls:{},count:0,exe:false,first:0,status:'Waiting',log:'Waiting to start.',cls:'',err:false,ev:null};
  const m=Math.min(n,ev.length);
  for(let j=0;j<m;j++)ev[j].fn(s,j+1);
  if(m>0){s.log=ev[m-1].log;s.cls=ev[m-1].err?'err':(ev[m-1].ok?'ok':'');if(s.status==='Waiting')s.status='Working'}
  s.ev=(n>0&&n<=ev.length)?ev[n-1]:null;
  s.time=m;return s;
}
function renderCodeLane(root,type,s,mistake,animate){
  const P=program(mistake);
  root.className='lane '+type;
  const src=P.map((p,i)=>{let c='';if(s.hl===i)c='hl';if(s.ls[i]==='x')c='x';const mark=s.ls[i]==='ok'?'▶ ran':s.ls[i]==='t'?'✓':s.ls[i]==='x'?'✗':'';return`<div class="ln ${c} ${s.ls[i]==='ok'?'ok':''}"><span class="no">${i+1}</span><span>${esc(p.src)}</span><span style="margin-left:auto;padding-left:10px;color:${s.ls[i]==='x'?'#ff6363':'#34d399'}">${mark}</span></div>`}).join('');
  const midTitle=type==='int'?'Current translation (thrown away after use)':'Translated target code (kept)';
  const midLines=type==='int'?s.trans:s.target;
  const mid=midLines.length?midLines.map(l=>`<div class="ln${/✗/.test(l)?' x':''}"><span>${esc(l)}</span></div>`).join(''):'<div class="empty">(nothing)</div>';
  const out=s.out.length?s.out.map(o=>`<div style="color:${o.e?'#ff9b9b':'#fff'}">${esc(o.t)}</div>`).join(''):'<span style="color:#5b6180">(no output yet)</span>';
  const vars=Object.keys(s.vars).length?Object.entries(s.vars).map(([k,v])=>`${k} = ${v}`).join('    '):'(none)';
  root.innerHTML=`
   <div class="lane-head"><div class="bshape ${type}">${type==='int'?'🔁':'🏭'}</div><div><b>${type==='int'?'Interpreter':'Compiler'}</b><small>${type==='int'?'Translate one line, execute it, next line':'Translate ALL lines, save program.exe, then run'}</small></div></div>
   <div class="cards">
     <div class="card"><h5>Source code</h5><div class="codebox src">${src}</div></div>
     <div class="card"><h5>${midTitle}</h5><div class="codebox mid">${mid}</div>${type==='cmp'&&s.exe?'<span class="exe">💾 program.exe created</span>':''}</div>
   </div>
   <div class="cards">
     <div class="card"><h5>Screen output</h5><div class="outbox">${out}</div></div>
     <div class="card"><h5>Variables in memory</h5><div class="mono vars">${esc(vars)}</div></div>
   </div>
   <div class="log ${s.cls}">${esc(s.log)}</div>
   <div class="stats">
     <div class="stat"><b>${s.count}</b><span>Lines translated</span></div>
     <div class="stat"><b>${s.time}</b><span>Time ticks used</span></div>
     <div class="stat"><b>${s.first||'-'}</b><span>First output at tick</span></div>
     <div class="stat"><b style="font-size:13px">${esc(s.status)}</b><span>Status</span></div>
   </div>`;
  if(!animate||!s.ev)return;
  const e=s.ev,q=c=>root.querySelector(c);
  const hl=q('.src .hl, .src .x');if(hl)gsap.fromTo(hl,{x:-8},{x:0,duration:.4,ease:'back.out(3)'});
  if(e.fx==='trans'){const ls=[...q('.mid').children].slice(-e.n);gsap.fromTo(ls,{x:40,autoAlpha:0},{x:0,autoAlpha:1,stagger:.1,duration:.45,ease:'back.out(2)'})}
  if(e.fx==='exec'){
    if(e.out){const o=q('.outbox').lastElementChild;gsap.fromTo(o,{autoAlpha:0,scale:1.4,transformOrigin:'0 50%'},{autoAlpha:1,scale:1,duration:.55,ease:'back.out(2)'})}
    else gsap.fromTo(q('.vars'),{scale:1.25,color:'#16b97f'},{scale:1,color:'inherit',duration:.7,ease:'back.out(2)',transformOrigin:'0 50%'});
  }
  if(e.fx==='err'){shake(root);const t=type==='int'?q('.outbox').lastElementChild:q('.mid').lastElementChild;pop(t)}
  if(e.fx==='exe')gsap.fromTo(q('.exe'),{scale:0,rotation:-25},{scale:1,rotation:0,duration:.8,ease:'elastic.out(1,.5)'});
  if(e.fx==='run'){gsap.fromTo(q('.outbox').children,{autoAlpha:0,y:12},{autoAlpha:1,y:0,stagger:.1,duration:.35,ease:'power2.out'});gsap.fromTo(root,{boxShadow:'0 0 0 0 rgba(22,185,127,.7)'},{boxShadow:'0 0 0 18px rgba(22,185,127,0)',duration:.9})}
  if(e.fx==='done'){const p=relPos(q('.outbox'),root);confetti(root,p.x,p.y,22)}
}
const cMistake=$('#cMistake');
function cEv(){return{int:codeEvents('int',cMistake.checked),cmp:codeEvents('cmp',cMistake.checked)}}
function renderCodeDemo(k,animate){
  const E=cEv();
  renderCodeLane($('#cInt'),'int',codeState(E.int,k),cMistake.checked,animate);
  renderCodeLane($('#cCmp'),'cmp',codeState(E.cmp,k),cMistake.checked,animate);
}
const p3=new Player($('#c3'),{unit:'Tick',total:()=>{const E=cEv();return Math.max(E.int.length,E.cmp.length)},render:renderCodeDemo,baseMs:()=>2300});
cMistake.onchange=()=>p3.reset();

/* ===================================================================
   Tabs, theme, full screen, keyboard
   =================================================================== */
let activeTab='p1';
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x===b));
  document.querySelectorAll('.page').forEach(p=>p.classList.toggle('on',p.id===b.dataset.tab));
  activeTab=b.dataset.tab;
  gsap.fromTo('#'+activeTab,{y:18,autoAlpha:0},{y:0,autoAlpha:1,duration:.5,ease:'power3.out'});
  setTimeout(()=>{drawEdges(lastEdges,false);[p1,p2,p3].forEach(p=>drawWavy(p.wavy,p.pf.f))},40);
});
$('#themeBtn').onclick=()=>{const h=document.documentElement,d=h.dataset.theme==='dark';h.dataset.theme=d?'light':'dark';$('#themeBtn').textContent=d?'🌙':'☀️'};
$('#fsBtn').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();else document.exitFullscreen()};
document.addEventListener('keydown',e=>{
  if(['SELECT','INPUT'].includes(e.target.tagName)&&e.key!==' ')return;
  const target=activeTab==='p1'?p1:(window.scrollY>$('#c3').offsetTop-300?p3:p2);
  if(e.key===' '){e.preventDefault();target.toggle()}
  else if(e.key==='ArrowRight'){target.pause();target.step()}
  else if(e.key==='ArrowLeft'){target.pause();target.back()}
  else if(e.key==='r'||e.key==='R'){target.reset()}
});

setLang('java');p2.reset();p3.reset();
