# Advanced 3.2: Ethereum and smart contract security. Checked against the Ethereum white paper (Buterin, 2013) and
# yellow paper (Wood), the mainnet launch (30 July 2015), EIP-1559 (London upgrade, 5 August 2021), the Solidity
# documentation (checked arithmetic from 0.8.0, December 2020, Panic(0x11), checks effects interactions pattern),
# the SWC registry and the OWASP Smart Contract Top 10, public post mortems of The DAO (17 June 2016, hard fork
# 20 July 2016), the Parity multisig thefts (19 July 2017) and freeze (6 November 2017, 513,774 ether), BeautyChain
# (CVE-2018-10299, April 2018), bZx (February 2020), Harvest Finance (October 2020), Poly Network (August 2021),
# Wormhole (February 2022), Ronin (March 2022, FBI attribution to Lazarus), Nomad (August 2022), Mango Markets
# (October 2022) and Euler Finance (March 2023, funds returned), and Daian et al., "Flash Boys 2.0" (IEEE S&P 2020).
from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show
from cykit import talk, attack, safe

chapter('cy-ethereum')
K = Kit()

K.code('gas_fee', r'''
# Ethereum fees after EIP-1559 (August 2021): gas used times (base fee + tip). The base fee is burned.
GWEI = 1e-9                                   # 1 gwei = one billionth of an ether

def fee(gas_used, base_gwei, tip_gwei, eth_price):
    eth = gas_used * (base_gwei + tip_gwei) * GWEI
    burned = gas_used * base_gwei * GWEI
    return eth, burned, eth * eth_price

for what, gas in [("send ether", 21_000), ("token transfer", 65_000), ("swap on a pool", 150_000)]:
    eth, burned, usd = fee(gas, base_gwei=20, tip_gwei=2, eth_price=3000)
    print(f"{what:15s} {gas:7,d} gas: {eth:.6f} ETH (${usd:6.2f}), burned {burned:.6f}")

# the base fee rises by up to 12.5% after a full block and falls by up to 12.5% after an empty one
base = 20.0
for fullness in (1.0, 1.0, 1.0, 0.5, 0.0):
    base *= 1 + 0.125 * (fullness - 0.5) / 0.5
    print(f"block {fullness:.0%} full -> next base fee {base:.2f} gwei")

# why gas exists: a contract stuck in a loop stops when its gas runs out, and the sender still pays
limit, per_loop = 100_000, 300
print("an endless loop stops after", limit // per_loop, "rounds when 100,000 gas runs out")
''')

K.code('reentrancy_sim', r'''
# Reentrancy in Python: a bank that sends money before updating its ledger
class Bank:
    def __init__(self, safe, locked_style=False):
        self.balance = {}
        self.vault = 0
        self.safe = safe
        self.locked_style = locked_style
        self.lock = False

    def deposit(self, who, amount):
        self.balance[who] = self.balance.get(who, 0) + amount
        self.vault += amount

    def withdraw(self, who):
        if self.locked_style:
            if self.lock:
                raise RuntimeError("reentrant call refused")
            self.lock = True
        try:
            amount = self.balance.get(who, 0)
            if amount <= 0 or self.vault < amount:
                raise RuntimeError("nothing to withdraw")
            if self.safe:
                self.balance[who] = 0            # effect first
            self.vault -= amount
            who.receive(self, amount)             # interaction: control passes to the receiver
            self.balance[who] = 0                 # the buggy bank updates only now
        finally:
            if self.locked_style:
                self.lock = False

class Attacker:
    def __init__(self):
        self.wallet = 0
        self.calls = 0
    def receive(self, bank, amount):
        self.wallet += amount
        self.calls += 1
        try:
            bank.withdraw(self)                   # call straight back in
        except RuntimeError as e:
            if self.calls == 1:
                print("   second call stopped:", e)

for name, bank in [("buggy", Bank(safe=False)), ("checks effects interactions", Bank(safe=True)),
                   ("reentrancy lock", Bank(safe=False, locked_style=True))]:
    for i in range(10):
        bank.deposit(f"customer{i}", 1)
    evil = Attacker()
    bank.deposit(evil, 1)
    print(name)
    bank.withdraw(evil)
    print(f"   attacker put in 1, now holds {evil.wallet}, bank vault left {bank.vault}")
''')

K.code('overflow', r'''
# Fixed width integers: what Solidity before 0.8 did silently, and what 0.8 does now
def unchecked(x, bits=256):
    return x % (2 ** bits)                         # wrap around, no error

def checked(x, bits=256):
    if not 0 <= x < 2 ** bits:
        raise OverflowError("Panic(0x11): arithmetic overflow or underflow")
    return x

print("uint8   0 - 1   unchecked =", unchecked(0 - 1, 8))
print("uint8 250 + 10  unchecked =", unchecked(250 + 10, 8))
try:
    checked(0 - 1, 8)
except OverflowError as e:
    print("uint8   0 - 1   checked   ->", e)

# BeautyChain batchTransfer (April 2018): total = count * value, then check sender balance >= total
count = 2
value = 2 ** 255                                   # chosen by the attacker
total = unchecked(count * value)                   # 2 * 2^255 = 2^256, which wraps to 0
print("\nBeautyChain total to deduct:", total)
print("balance check 'balance >= total' passes with any balance, yet each receiver gets", value)
print("that is about 5.8 x 10^76 tokens created from nothing")
''')

K.code('access_control', r'''
# Missing access control: the Parity multisig mistake in miniature (July 2017)
class Wallet:
    def __init__(self):
        self.owners = set()
        self.funds = 0

    def init_wallet(self, caller, owners):
        # BUG: anyone may call this, at any time, and it replaces the owners
        self.owners = set(owners)

    def init_wallet_fixed(self, caller, owners):
        if self.owners:
            raise PermissionError("already initialised")
        self.owners = set(owners)

    def withdraw(self, caller, amount):
        if caller not in self.owners:
            raise PermissionError(f"{caller} is not an owner")
        self.funds -= amount
        return amount

w = Wallet()
w.init_wallet("deployer", {"alice", "bob"})
w.funds = 1000
w.init_wallet("mallory", {"mallory"})              # the attacker simply re initialises
print("stolen:", w.withdraw("mallory", 1000), " funds left:", w.funds)

v = Wallet()
v.init_wallet_fixed("deployer", {"alice", "bob"})
try:
    v.init_wallet_fixed("mallory", {"mallory"})
except PermissionError as e:
    print("fixed wallet:", e)

# tx.origin is the person who started the transaction, msg.sender is whoever called this contract
def is_owner_bad(tx_origin, msg_sender, owner):
    return tx_origin == owner                       # a malicious contract the owner calls passes this

def is_owner_good(tx_origin, msg_sender, owner):
    return msg_sender == owner

print("tx.origin check fooled by a phishing contract:", is_owner_bad("alice", "evil_contract", "alice"))
print("msg.sender check:", is_owner_good("alice", "evil_contract", "alice"))
''')

K.code('amm_oracle', r'''
# A flash loan pumps a constant product pool, and a lending app that trusts the spot price pays for it
def swap(r_in, r_out, amount, fee=0.003):
    amount_after_fee = amount * (1 - fee)
    return r_out - r_in * r_out / (r_in + amount_after_fee)

def attack(loan, oracle):
    usdc, eth = 200_000.0, 100.0                 # pool reserves, price 2,000
    got_eth = swap(usdc, eth, loan)
    usdc, eth = usdc + loan, eth - got_eth
    spot = usdc / eth
    price = spot if oracle == "spot" else 2000 * (1 - 12 / 1800) + spot * 12 / 1800
    borrowed = 0.75 * 10 * price                 # 10 ETH deposited as collateral, 75% loan to value
    usdc_back = swap(eth, usdc, got_eth)
    profit = borrowed + usdc_back - loan * 1.0009 - 10 * 2000
    return spot, price, borrowed, profit

for loan in (100_000, 200_000, 400_000):
    for oracle in ("spot", "twap"):
        spot, price, borrowed, profit = attack(loan, oracle)
        print(f"loan {loan:7,d} oracle {oracle:4s}: pool price {spot:8,.0f}, oracle {price:8,.0f}, "
              f"borrowed {borrowed:9,.0f}, attacker profit {profit:10,.0f}")
''')

K.code('sandwich', r'''
# A sandwich attack and how the victim's slippage limit caps it
def buy(usdc, eth, amount):
    return eth - usdc * eth / (usdc + amount * 0.997)

def sandwich(slippage, victim=20_000, gas=30):
    X, Y = 200_000.0, 100.0
    fair = buy(X, Y, victim)
    min_out = fair * (1 - slippage)
    lo, hi = 0.0, 400_000.0
    for _ in range(60):                             # the biggest front run that still lets the victim trade
        a = (lo + hi) / 2
        e = buy(X, Y, a)
        if buy(X + a, Y - e, victim) >= min_out:
            lo = a
        else:
            hi = a
    a = lo
    e = buy(X, Y, a)
    x1, y1 = X + a, Y - e
    got = buy(x1, y1, victim)
    x2, y2 = x1 + victim, y1 - got
    sold = x2 - x2 * y2 / (y2 + e * 0.997)
    return fair, got, sold - a - gas

for s in (0.005, 0.02, 0.05, 0.10):
    fair, got, profit = sandwich(s)
    verdict = "attack" if profit > 0 else "not worth it"
    print(f"slippage {s:5.1%}: victim gets {got:.3f} of {fair:.3f} ETH, bot profit {profit:9.2f} -> {verdict}")
''', long=True)

K.code('approvals', r'''
# Token approvals: why "unlimited" approvals turn one bad signature into a total loss
MAX = 2 ** 256 - 1

class Token:
    def __init__(self):
        self.balance = {"you": 5000}
        self.allowance = {}

    def approve(self, owner, spender, amount):
        self.allowance[(owner, spender)] = amount

    def transfer_from(self, spender, owner, to, amount):
        if self.allowance.get((owner, spender), 0) < amount:
            raise PermissionError("not approved")
        if self.allowance[(owner, spender)] != MAX:
            self.allowance[(owner, spender)] -= amount
        self.balance[owner] -= amount
        self.balance[to] = self.balance.get(to, 0) + amount

t = Token()
t.approve("you", "dex", MAX)                       # the app asked for unlimited spending
t.transfer_from("dex", "you", "pool", 100)         # your real trade
print("after trade:", t.balance)
# months later the app's contract is hacked, or you signed for a look alike phishing site
t.transfer_from("dex", "you", "attacker", t.balance["you"])
print("after the hack:", t.balance)

t2 = Token()
t2.approve("you", "dex", 100)                      # approve only what this trade needs
t2.transfer_from("dex", "you", "pool", 100)
try:
    t2.transfer_from("dex", "you", "attacker", 4900)
except PermissionError as e:
    print("exact approval:", e, "| your balance stays", t2.balance["you"])
''')

SOL_BAD = '''
// Vulnerable: sends ether before updating the ledger
function withdraw() external {
    uint amount = balances[msg.sender];
    require(amount > 0, "nothing to withdraw");
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok, "send failed");
    balances[msg.sender] = 0;
}
'''
SOL_GOOD = '''
// Fixed: checks, then effects, then interactions, plus a lock
function withdraw() external nonReentrant {
    uint amount = balances[msg.sender];          // check
    require(amount > 0, "nothing to withdraw");
    balances[msg.sender] = 0;                    // effect
    (bool ok, ) = msg.sender.call{value: amount}("");   // interaction
    require(ok, "send failed");
}
'''

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('idea', 'Ethereum: a world computer whose programs hold money', f'''
{talk('Bitcoin made a shared notebook for payments. In 2013 a nineteen year old programmer, Vitalik Buterin, asked a bigger question: what if the notebook could also store small programs that anyone can call, and that move money by themselves according to their code? He described it in the Ethereum white paper, and the network went live on 30 July 2015. Those programs are called smart contracts. Think of a vending machine. You put in a coin, press a button, and the machine gives you a drink without a shopkeeper. A smart contract is a vending machine for money and digital things: a loan, an exchange, a game, a vote. Every node runs the same code on a virtual machine, the EVM, and gets the same result. Ethereum has two kinds of accounts. Externally owned accounts belong to people and are controlled by a private key. Contract accounts hold code and their own balance. Every step of a program costs gas, paid in ether, which stops endless loops and pays the validators. Two properties make contracts very different from normal software. First, the code is public, so attackers can study it for weeks. Second, once deployed it usually cannot be changed, and any money it loses is gone, because there is no bank to reverse a payment. People said code is law, but history shows that code is also bugs, and a bug in a contract holding hundreds of millions is an open safe on a busy street. This chapter walks through the main kinds of bugs, each with a real incident.')}
{src('Buterin (2013), Wood (yellow paper), EIP-1559, Solidity documentation, SWC registry, OWASP Smart Contract Top 10, Daian et al. (2020), public post mortems of The DAO, Parity, BeautyChain, bZx, Harvest, Poly Network, Wormhole, Ronin, Nomad, Mango Markets and Euler.')}
{wwh('A <b>smart contract</b> is a program stored on a blockchain such as Ethereum. Anyone can call it, every node runs it the same way, and it can hold and move cryptocurrency by itself.',
     'It replaces a trusted middleman (a bank, an exchange, an escrow agent) with public code. That removes one kind of trust but adds a new risk: a bug cannot be patched quietly, and stolen money cannot be recalled.',
     'Write small, well tested contracts in Solidity or Vyper, follow known safe patterns, use audited libraries, test with fuzzers and formal tools, get independent audits, and keep emergency controls such as a pause switch behind a time delay.')}
{run('gas_fee')}
{fxs(fx('Transaction fee after EIP-1559', 'fee = gas used &times; (base fee + priority tip)', '21,000 gas at 20 + 2 gwei: 462,000 gwei = 0.000462 ETH.', key=True),
     fx('Base fee update', 'base<sub>next</sub> = base &times; (1 + &frac18; &times; (used &minus; target) / target)', 'A full block (twice the target) raises it by 12.5%.', key=True),
     fx('Units', '1 ether = 10<sup>9</sup> gwei = 10<sup>18</sup> wei', 'Fees are quoted in gwei.'))}
{table(['Account type', 'Controlled by', 'Has code?', 'Can start a transaction?'], [
    ['Externally owned account (EOA)', 'A private key held by a person', 'No', 'Yes'],
    ['Contract account', 'Its own code', 'Yes', 'No, it only reacts when called']])}
{scene('Around you', '<p>A metro token gate is a simple smart machine: insert a valid token and the gate opens, with nobody checking. If its software had a bug that opened the gate for a bent coin, everyone would soon know. A smart contract is like that gate, except it guards money and the whole world can study its wiring.</p>')}
''', kw=['Ethereum', 'Vitalik Buterin', 'white paper', 'smart contract', 'EVM', 'externally owned account', 'contract account', 'gas', 'gwei', 'EIP-1559', 'base fee', 'priority fee', 'immutability', 'code is law', 'Solidity'])

K.lesson('reentrancy', 'Reentrancy: The DAO and calling back in', f'''
{talk('The most famous smart contract bug has a strange name: reentrancy. When a contract sends ether to another contract, the receiving contract’s code runs straight away, in the middle of the sender’s function. If the sender has not yet updated its own records, the receiver can call back in and ask again, and again, before the first call finishes. In the animation the buggy bank sends one ether and only then sets the attacker’s balance to zero, so the attacker re enters ten times and drains the bank. This is not a made up example. The DAO was a giant investment fund run by a smart contract, which raised about 150 million dollars in ether in 2016. On 17 June 2016 an attacker used exactly this pattern to move about 3.6 million ether, more than a quarter of its funds, into a child contract. The Ethereum community argued for weeks, and on 20 July 2016 most of it adopted a hard fork that moved the funds back. A minority refused, saying the chain must never be rewritten, and kept the original chain, which still runs today as Ethereum Classic. The fixes are simple once known. Follow the checks, effects, interactions order: check the conditions, update your own state, and only then call outside. Add a reentrancy lock, such as OpenZeppelin’s nonReentrant modifier, so a function cannot be entered while it is already running. Reentrancy still causes losses today in more subtle forms, such as reentering a different function that reads the half updated state, called cross function or read only reentrancy.')}
{viz('cyreentry')}
{show('The bug in Solidity', SOL_BAD, {5: 'Sending ether hands control to the receiver, whose code can call withdraw again.', 7: 'The balance is cleared only after the send, too late.'}, lang='solidity')}
{show('The fix', SOL_GOOD, {2: 'nonReentrant sets a lock for the whole call.', 5: 'The ledger is cleared before any outside call.'}, lang='solidity')}
{run('reentrancy_sim')}
{fxs(fx('What the attacker takes from a buggy bank', 'taken = min(vault, deposit &times; number of re entries)', 'Deposit 1 into a vault of 11: 11 re entries take everything.', key=True),
     fx('The DAO in numbers', 'about 3.6 million of about 12.7 million ether raised', 'Roughly 28% of the fund.'))}
''', kw=['reentrancy', 'The DAO', 'hard fork', 'Ethereum Classic', 'checks effects interactions', 'nonReentrant', 'reentrancy guard', 'fallback', 'receive function', 'cross function reentrancy', 'read only reentrancy', 'OpenZeppelin'])

K.lesson('overflow', 'Integer overflow and the danger of silent maths', f'''
{talk('Computers store numbers in a fixed number of bits. A uint8 can hold 0 to 255, and the usual Ethereum number, uint256, holds 0 to about 1.16 times 10 to the 77. Before Solidity version 0.8, going past the top silently wrapped around to zero, and going below zero wrapped to the top, just like an old car odometer rolling from 99999 back to 00000. The animation shows a dial of all 256 values. Wrap arounds turned into real thefts. In April 2018 the BeautyChain token had a function called batchTransfer that multiplied the number of receivers by the amount each should get, then checked the sender had that total. The attacker chose an amount of 2 to the 255 and two receivers. The product 2 to the 256 wrapped to exactly zero, the balance check passed, and each receiver was credited 2 to the 255 tokens, an unimaginably large number. Exchanges froze the token within hours. The fix came in December 2020, when Solidity 0.8 made every addition, subtraction and multiplication checked by default, so an overflow now cancels the transaction with an error called Panic 0x11. Before that, careful teams used the SafeMath library. Overflow bugs are not finished, though. Code inside an unchecked block, older contracts still holding money, and type conversions such as squeezing a uint256 into a uint8 can all still wrap.')}
{viz('cyoverflow')}
{run('overflow')}
{fxs(fx('Range of an n bit unsigned integer', '0 to 2<sup>n</sup> &minus; 1', 'uint8: 0 to 255. uint256: 0 to about 1.158 &times; 10<sup>77</sup>.', key=True),
     fx('Wrap around (unchecked)', 'result = (a op b) mod 2<sup>n</sup>', 'uint8 0 &minus; 1 = &minus;1 mod 256 = 255.', key=True),
     fx('The BeautyChain total', '2 &times; 2<sup>255</sup> = 2<sup>256</sup> &equiv; 0 (mod 2<sup>256</sup>)', 'A balance check against 0 always passes.'))}
{note('Checked maths stops wrap arounds, but it cannot stop logic mistakes such as rounding in the wrong direction. Rounding errors in share calculations caused large losses in 2023, so always round in favour of the contract.', 'warn')}
''', kw=['integer overflow', 'underflow', 'uint256', 'uint8', 'wrap around', 'BeautyChain', 'batchTransfer', 'CVE-2018-10299', 'SafeMath', 'Solidity 0.8', 'checked arithmetic', 'Panic 0x11', 'unchecked block', 'rounding'])

K.lesson('access', 'Access control: who is allowed to call this function', f'''
{talk('Many of the most expensive contract bugs are the simplest: a function that should be locked was left open. In July 2017 the Parity multisig wallet, a popular wallet that needed several owners to approve a payment, had a function called initWallet that set the owners. It was meant to run once, at creation, but anyone could call it again later. On 19 July an attacker called it on three wallets, made themselves the only owner, and took about 153,000 ether, around 30 million dollars at the time. Parity fixed it with a new shared library contract. Then on 6 November 2017 a user who called themselves devops199 found that the new library itself had never been initialised. They called its init function, became its owner, and then, they said by accident, called its kill function. The library deleted itself, and every wallet that depended on it was frozen forever with about 513,774 ether inside, worth over 150 million dollars then. Nobody stole it, and nobody can ever spend it. Other access mistakes include checking tx dot origin instead of msg dot sender. tx dot origin is the person who started the whole transaction, so if an owner is tricked into calling a malicious contract, that contract can call the wallet and pass a tx dot origin check. Use msg dot sender, the direct caller, and use tested role libraries such as OpenZeppelin’s Ownable and AccessControl.')}
{run('access_control')}
{table(['Access mistake', 'Real example', 'Fix'], [
    ['Initialiser that anyone can call again', 'Parity multisig, July 2017, about 153,000 ether stolen', 'An initializer modifier that runs only once, set during deployment'],
    ['Uninitialised library with a self destruct', 'Parity library, November 2017, about 513,774 ether frozen', 'Initialise and lock library contracts, avoid self destruct'],
    ['Checking tx.origin for ownership', 'Phishing contracts that ride on the owner’s call', 'Check msg.sender'],
    ['Missing onlyOwner on an admin function', 'Many token contracts that let anyone mint', 'Role based access control, tests for every privileged function'],
    ['Unsafe delegatecall to user supplied code', 'Code runs with the caller’s storage and funds', 'Only delegatecall to fixed, trusted implementations']])}
''', kw=['access control', 'Parity multisig', 'initWallet', 'devops199', 'self destruct', 'frozen funds', 'tx.origin', 'msg.sender', 'onlyOwner', 'Ownable', 'AccessControl', 'delegatecall', 'initializer'])

K.lesson('oracle', 'Oracles and flash loans: bending prices for one transaction', f'''
{talk('A smart contract cannot look at the outside world. If a lending app needs the price of ether, it must ask an oracle, some source that reports a price on chain. Many early apps simply asked a trading pool on chain, because it was easy. A common kind of pool, an automated market maker, holds two tokens and keeps their product constant, x times y equals k. Its price is just the ratio of the two piles, so a big enough trade moves it a lot. Now add flash loans. A flash loan lends any amount, millions of dollars, with no deposit at all, on one condition: it must be repaid before the same transaction ends, or the whole transaction is undone as if it never happened. So an attacker can borrow a fortune, buy heavily from a pool to push its price up, use that inflated price to borrow far more than their deposit is worth from a lending app, sell back, repay the flash loan, and keep the difference, all within one block of about twelve seconds. The animation does exactly this with made up numbers. The bZx attacks of February 2020 were the first famous examples. Harvest Finance lost about 34 million dollars in October 2020, and Mango Markets lost about 110 million in October 2022 when a trader pumped the price of its own token. The defences are better oracles. Use a time weighted average price over many blocks, so a one block pump barely moves it, use several independent price feeds such as Chainlink, set limits on how fast a price may change, and do not treat a thin, easily moved market as the truth.')}
{viz('cyflash')}
{run('amm_oracle')}
{fxs(fx('Constant product pool', 'x &times; y = k, price = x / y', '200,000 USDC and 100 ETH: price 2,000, k = 20,000,000.', key=True),
     fx('Output of a swap (0.3% fee)', '&Delta;y = y &minus; x y / (x + 0.997 &Delta;x)', 'Buying with 200,000 USDC: 100 &minus; 20,000,000 / 399,400 &asymp; 49.92 ETH.', key=True),
     fx('Time weighted average price', 'TWAP = &Sigma; price<sub>t</sub> &times; &Delta;t / &Sigma; &Delta;t', 'A 12 second pump in a 30 minute window has weight 12 / 1800 &asymp; 0.0067.', key=True),
     fx('Flash loan fee', 'repay = loan &times; (1 + fee)', 'Aave version 2 charged 0.09%: 200,000 &times; 1.0009 = 200,180.'))}
''', kw=['oracle', 'price oracle', 'automated market maker', 'AMM', 'constant product', 'x y = k', 'flash loan', 'price manipulation', 'bZx', 'Harvest Finance', 'Mango Markets', 'TWAP', 'time weighted average price', 'Chainlink'])

K.lesson('mev', 'Front running, sandwiches and MEV: the public waiting room', f'''
{talk('Before a transaction goes into a block it sits in a public waiting room called the mempool, where anyone can read it. Block builders choose the order of transactions, usually putting the highest tips first. That opens a door that does not exist in a normal stock market, where front running a customer is a crime. A bot can see your trade before it happens and act first. The classic case is the sandwich attack in the animation. Priya wants to buy ether with 20,000 USDC. A bot sees her trade, buys just before her with a higher tip, which pushes the price up, lets her buy at the worse price, then sells straight after her at the price she pushed up. The bot’s profit comes out of Priya’s pocket. Her protection is the slippage limit she set, the least she is willing to accept. A tight limit leaves the bot almost no room. In 2020 Philip Daian and colleagues named this whole world MEV, now called maximal extractable value, in a paper titled Flash Boys 2.0, after a book about high speed trading. Since then MEV bots have taken hundreds of millions of dollars. Users can protect themselves with tight slippage limits, by sending trades through private routes that skip the public mempool, and by using apps that batch trades or use commit and reveal schemes, where you first publish a sealed hash of your choice and reveal it later, so nobody can copy it in time.')}
{viz('cysandwich')}
{run('sandwich')}
{fxs(fx('Victim’s minimum output', 'min out = fair output &times; (1 &minus; slippage)', 'Fair 9.066 ETH with 5%: at least about 8.613 ETH.', key=True),
     fx('Bot profit', 'profit = sell proceeds &minus; front run cost &minus; gas', 'If this is not positive, the bot does not attack.', key=True),
     fx('Commit and reveal', 'commit c = H(choice &#8214; random salt), reveal later', 'Nobody can read the choice from the hash in time to copy it.'))}
''', kw=['mempool', 'front running', 'back running', 'sandwich attack', 'MEV', 'maximal extractable value', 'Flash Boys 2.0', 'slippage', 'private transaction', 'commit reveal', 'block builder', 'priority tip'])

K.lesson('bridges', 'Bridges, signatures and approvals: the biggest thefts', f'''
{talk('The largest thefts in this field did not come from clever maths inside one contract. They came from the systems that join chains together and from the permissions users hand out. A bridge moves tokens between blockchains. You lock coins in a contract on one chain, and a group of validators confirms it so that matching tokens are created on the other chain. Whoever controls those validators controls everything locked in the bridge. In March 2022 the Ronin bridge, used by the game Axie Infinity, needed five of nine validator signatures. Attackers obtained five keys, partly through a fake job offer sent to an engineer, and took about 625 million dollars. The FBI attributed it to North Korea’s Lazarus Group. In February 2022 the Wormhole bridge lost about 326 million dollars because a signature checking function could be fooled into accepting fake approvals. In August 2022 an upgrade to the Nomad bridge accidentally marked an empty message as valid, so anyone could copy the first attacker’s transaction and change the address to their own, and hundreds of people did, taking about 190 million dollars. Ordinary users face a smaller version of the same problem through token approvals. When you use a trading app it asks permission to spend your tokens, often an unlimited amount. If that app is later hacked, or you sign an approval on a look alike phishing site, the attacker can take everything you hold of that token. Approve only what you need and review old approvals with a revoke tool.')}
{run('approvals')}
{table(['Incident', 'Year', 'Amount (approx.)', 'Root cause'], [
    ['Poly Network', '2021', '611 million dollars, later returned', 'A cross chain message could change who the keepers were'],
    ['Wormhole', '2022', '326 million dollars', 'Signature verification could be bypassed'],
    ['Ronin', '2022', '625 million dollars', '5 of 9 validator keys stolen, social engineering'],
    ['Nomad', '2022', '190 million dollars', 'An upgrade made unproven messages valid, copied by hundreds'],
    ['Euler Finance', '2023', '197 million dollars, later returned', 'A donation function skipped a health check']])}
{attack([
    ('Steal a threshold of bridge validator keys', 'Many independent validators in different organisations, hardware keys, a higher threshold, withdrawal limits and delays'),
    ('Replay a valid signature on another chain or a second time', 'Include the chain id and a nonce in every signed message (EIP-712)'),
    ('Phishing site asks for an unlimited token approval', 'Approve exact amounts, read what the wallet shows, revoke old approvals'),
    ('Malicious upgrade of a proxy contract', 'Upgrades behind a multisig and a timelock, so users can see and react')])}
''', kw=['bridge', 'cross chain', 'Ronin', 'Axie Infinity', 'Lazarus', 'Wormhole', 'Nomad', 'Poly Network', 'Euler Finance', 'signature replay', 'EIP-712', 'chain id', 'token approval', 'unlimited approval', 'revoke', 'proxy upgrade', 'timelock'])

K.lesson('audit', 'Building contracts safely: patterns, tools and audits', f'''
{talk('Because a deployed contract is public and hard to change, smart contract teams test far more heavily than most software teams. A good process looks like this. Keep contracts small and reuse audited building blocks such as the OpenZeppelin library instead of writing your own token or access control. Write unit tests for every function and every failure. Run a static analyser such as Slither, which knows hundreds of bug patterns. Run property based fuzzers such as Echidna or Foundry, which hammer the contract with random calls while checking rules that must always hold, called invariants, for example that the sum of all balances equals the total supply. For valuable contracts, use formal verification, which proves mathematically that certain rules always hold. Then hire independent auditors, and after launch run a bug bounty, where ethical hackers are paid to report bugs privately. Platforms for this have paid single rewards of millions of dollars. Plan for failure too: a pause switch, limits on how much can leave per hour, and upgrades that wait behind a timelock so users can see changes coming. The SWC registry and the OWASP Smart Contract Top 10 list the known weaknesses, and they are a good checklist for any review.')}
{steps('A secure release process for a smart contract', ['Write a short specification and the invariants that must always hold.',
       'Build on audited libraries and the checks effects interactions pattern.',
       'Unit test every function, including every way it should fail.',
       'Run a static analyser (Slither) and a fuzzer with invariants (Echidna or Foundry).',
       'Formally verify the most valuable rules.',
       'Get at least one independent audit and fix every finding.',
       'Launch with deposit caps, a pause switch, a timelock on upgrades and a bug bounty.',
       'Monitor transactions live and keep an incident plan ready.'])}
{versus('Ways to find contract bugs', ['', 'Unit tests', 'Static analysis', 'Fuzzing', 'Formal verification', 'Audit'], [
    ['Finds', 'Bugs you thought of', 'Known patterns', 'Surprising sequences of calls', 'Every violation of a stated rule', 'Design and logic flaws'],
    ['Misses', 'What you did not imagine', 'New kinds of bugs', 'Rare deep paths', 'Rules nobody wrote down', 'Anything outside the scope and time'],
    ['Example tools', 'Foundry, Hardhat', 'Slither', 'Echidna, Foundry', 'Certora, SMTChecker', 'Independent firms, contests']],
    'No single method is enough. The large losses usually came from issues that one method could have caught and nobody ran.')}
{safe('Practise on deliberately vulnerable training games such as Ethernaut or Damn Vulnerable DeFi, on a local test chain or a public test network with free test ether. Never test an attack on a contract that holds real people’s money. Report real bugs through the project’s bug bounty.')}
''', kw=['smart contract audit', 'OpenZeppelin', 'Slither', 'Echidna', 'Foundry', 'fuzzing', 'invariant', 'formal verification', 'bug bounty', 'pause switch', 'timelock', 'SWC registry', 'OWASP Smart Contract Top 10', 'Ethernaut'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that smart contracts are public programs that hold money and cannot easily be fixed. A student can spot reentrancy, overflow, missing access checks and price oracle problems in small examples. A professional writes, tests and audits contracts with standard tools. Experts research new attack classes, formal methods and MEV.')}
{ladder(
    '<p>A smart contract is a vending machine for money that lives on the blockchain. Everyone can read its code, and if it has a bug, the money can be taken and nobody can give it back.</p>',
    '<p>Gas and EIP-1559 fees, checks effects interactions, uint wrap (a op b) mod 2<sup>n</sup>, x y = k pools and TWAP, slippage limits and sandwiches, the main incidents.</p>',
    '<p>Write Solidity with OpenZeppelin, test with Foundry, fuzz invariants, run Slither, review against the SWC registry, design oracles, timelocks and pause switches, respond to live incidents.</p>',
    '<p>Research formal verification of DeFi protocols, MEV and fair ordering, cross chain bridge security, and new compiler and EVM level bugs.</p>')}
{grow('Explain how smart contracts can lose money.',
      'Find the classic bugs in small contracts and explain the fixes.',
      'Build and review contracts with professional tools and processes.')}
''', kw=['beginner', 'expert', 'Solidity developer', 'smart contract auditor', 'MEV research'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Ethereum</b>: public programs (smart contracts) on the EVM, EOAs and contract accounts, gas, fee = gas &times; (base + tip). Code is public and hard to change.',
    '<b>Reentrancy</b>: sending ether hands over control. The DAO (June 2016, about 3.6 million ether, Ethereum Classic split). Fix: checks effects interactions plus nonReentrant.',
    '<b>Overflow</b>: (a op b) mod 2<sup>n</sup> before Solidity 0.8. BeautyChain 2018. Now checked by default (Panic 0x11), beware unchecked blocks and casts.',
    '<b>Access control</b>: Parity July 2017 (initWallet, about 153,000 ether stolen) and November 2017 (library killed, about 513,774 ether frozen). Use msg.sender, not tx.origin.',
    '<b>Oracles and flash loans</b>: x y = k pools are easy to move. bZx, Harvest, Mango. Use TWAP and independent feeds.',
    '<b>MEV</b>: public mempool, sandwich attacks, slippage limits, private routes, commit and reveal.',
    '<b>Bridges and approvals</b>: Ronin, Wormhole, Nomad. Signatures need chain id and nonce, approve exact amounts.',
    '<b>Process</b>: audited libraries, tests, Slither, fuzzing invariants, formal verification, audits, bug bounties, timelocks.'],
    'Advanced 4.1: social engineering and phishing, because many of the thefts in this chapter began with a person being tricked.')}
{files('Three tasks: a safe withdraw, a checked add for uint8, and a constant product swap.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'What is a smart contract?', ['A paper contract signed online', 'A program stored on a blockchain that anyone can call and that can move money by itself', 'An insurance policy', 'A private database'], 1, 'A vending machine for money.', 'It runs the same way on every node.')
K.quiz('e', 'Why is a bug in a deployed smart contract so serious?', ['Contracts are slow', 'The code is public and usually cannot be changed, and lost funds cannot be recalled', 'Gas is expensive', 'It is not serious'], 1, 'Public and permanent.', 'Attackers can study it, and there is no bank to reverse payments.')
K.quiz('e', 'What does gas do on Ethereum?', ['Makes blocks bigger', 'Charges for every step of computation, which stops endless loops', 'Encrypts transactions', 'Picks miners'], 1, 'A meter.', 'A loop stops when its gas runs out.')
K.quiz('e', 'A website you found in an advert asks you to approve unlimited spending of your tokens. What is safest?', ['Approve unlimited, it saves fees', 'Approve only the amount you need, or leave the site', 'Share your seed phrase instead', 'Approve twice'], 1, 'Approvals are permissions.', 'An unlimited approval lets the spender take everything later.')
K.quiz('m', 'What made The DAO attack possible?', ['A weak password', 'The contract sent ether before updating the balance, so the attacker could re enter', 'A 51% attack', 'Integer overflow'], 1, 'Order of operations.', 'This is reentrancy.')
K.quiz('m', 'In Solidity 0.7, a uint8 holding 0 has 1 subtracted. The result is', ['&minus;1', '0', '255', 'An error'], 2, 'Wrap around.', '&minus;1 mod 256 = 255.')
K.quiz('m', 'Why is checking tx.origin for ownership dangerous?', ['It is slow', 'A malicious contract called by the owner passes the check', 'It costs more gas', 'It is not available'], 1, 'Who started versus who called.', 'Use msg.sender, the direct caller.')
K.quiz('m', 'What must happen to a flash loan?', ['Repaid within a year', 'Repaid in the same transaction, or everything is undone', 'Repaid by the lender', 'Nothing'], 1, 'Atomic.', 'That is why it needs no deposit.')
K.quiz('m', 'What protects a lending app from one block price pumps?', ['A bigger pool only', 'A time weighted average price and independent price feeds', 'Higher gas', 'A longer password'], 1, 'Averages.', 'A 12 second pump barely moves a 30 minute average.')
K.quiz('h', 'In a sandwich attack, what limits how much the bot can take?', ['The gas limit', 'The victim’s slippage limit', 'The block size', 'The bot’s balance only'], 1, 'Minimum output.', 'The bot can only push the price until the victim’s trade would fail.')
K.quiz('h', 'Why did the Parity library freeze of November 2017 lock funds forever?', ['The keys were lost', 'The shared library contract was killed, so wallets depending on it could no longer run', 'A 51% attack', 'A court order'], 1, 'Self destruct.', 'About 513,774 ether stayed in wallets that can no longer execute.')
K.quiz('h', 'How did attackers take about 625 million dollars from the Ronin bridge?', ['Breaking SHA-256', 'Gaining control of 5 of the 9 validator keys', 'A sandwich attack', 'Integer overflow'], 1, 'Threshold signatures.', 'Social engineering helped them reach the threshold.')
K.quiz('h', 'Which signed message field stops a signature being replayed on another chain?', ['The gas price', 'The chain id', 'The block number', 'The token name'], 1, 'EIP-712 domain.', 'A nonce stops replay on the same chain.')
K.quiz('x', 'In the style of a UC Berkeley DeFi course question: a pool holds 200,000 USDC and 100 ETH with no fee. How much ETH does 200,000 USDC buy?', ['100', '50', '66.7', '25'], 1, 'x y = k.', '100 &minus; 20,000,000 / 400,000 = 50.')
K.quiz('x', 'In the style of an IIT Madras blockchain exam: which property must hold after any sequence of calls to a token contract?', ['Gas is constant', 'The sum of all balances equals the total supply', 'Every balance is equal', 'The owner holds half'], 1, 'An invariant.', 'Fuzzers and formal tools check rules like this.')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', 'A transfer uses 21,000 gas at a base fee of 20 gwei and a tip of 2 gwei. Fee in gwei?', '462000', 'gas &times; (base + tip).', ['20 + 2 = 22 gwei.', '21,000 &times; 22.', eq('462,000 gwei')], check=21000 * 22)
K.calc('e', 'That fee in ether? (1 ether = 10<sup>9</sup> gwei)', '0.000462', 'Divide by 10<sup>9</sup>.', ['462,000 / 1,000,000,000.', 'Move the decimal 9 places.', eq('0.000462 ETH')], check=462000 / 1e9)
K.calc('e', 'uint8 250 + 10 without checks. Result?', '4', '(a + b) mod 256.', ['260.', '260 &minus; 256.', eq('4')], check=(250 + 10) % 256)
K.calc('m', 'Largest value of a uint16?', '65535', '2<sup>16</sup> &minus; 1.', ['2<sup>16</sup> = 65,536.', 'Minus 1.', eq('65,535')], check=2 ** 16 - 1)
K.calc('m', 'A full block (twice the target). Base fee 20 gwei. Next base fee?', '22.5', '+12.5%.', ['20 &times; 0.125 = 2.5.', '20 + 2.5.', eq('22.5 gwei')], check=20 * 1.125)
K.calc('m', 'Pool 200,000 USDC and 100 ETH, no fee. ETH bought with 200,000 USDC?', '50', 'y &minus; k / (x + &Delta;x).', ['k = 20,000,000.', '20,000,000 / 400,000 = 50.', eq('100 &minus; 50 = 50 ETH')], check=100 - 200000 * 100 / 400000)
K.calc('m', 'After that trade the pool holds 400,000 USDC and 50 ETH. New price?', '8000', 'x / y.', ['400,000 / 50.', 'Price was 2,000.', eq('8,000 USDC per ETH')], check=400000 / 50)
K.calc('h', 'A lending app lends 75% of collateral value. 10 ETH valued at the pumped price of 8,000. Loan?', '60000', '0.75 &times; 10 &times; price.', ['Collateral 80,000.', 'Times 0.75.', eq('60,000 USDC')], check=0.75 * 10 * 8000)
K.calc('h', 'A 30 minute TWAP. Price 2,000 for 1,788 s and 8,000 for 12 s. TWAP?', '2040', 'Time weighted mean.', ['2,000 &times; 1,788 = 3,576,000.', '8,000 &times; 12 = 96,000. Sum 3,672,000.', eq('3,672,000 / 1,800 = 2,040')], check=(2000 * 1788 + 8000 * 12) / 1800)
K.calc('h', 'A flash loan of 200,000 with a 0.09% fee. Amount to repay?', '200180', 'loan &times; 1.0009.', ['0.09% of 200,000 = 180.', 'Add it.', eq('200,180')], check=round(200000 * 1.0009))
K.calc('h', 'Fair output 9.066 ETH and a 5% slippage limit. Minimum accepted? Round to 3 decimals.', '8.613', 'fair &times; 0.95.', ['9.066 &times; 0.95.', 'Round.', eq('&asymp; 8.613 ETH')], check=round(9.066 * 0.95, 3))
K.calc('x', 'BeautyChain: 2 receivers, value 2<sup>255</sup>, total computed mod 2<sup>256</sup>. Total?', '0', '2 &times; 2<sup>255</sup>.', ['= 2<sup>256</sup>.', '2<sup>256</sup> mod 2<sup>256</sup>.', eq('0')], check=(2 * 2 ** 255) % 2 ** 256)

# ------------------------------------------------------------------------------------------------ assignments
K.assign('safe_withdraw', 'e', 'A withdraw that cannot be re entered',
         '<p>Complete <code>withdraw(self, who)</code> in the class. It must follow checks, effects, interactions: raise <code>ValueError</code> if the balance is 0, set the balance to 0 <b>before</b> calling <code>who.receive(self, amount)</code>, and reduce <code>vault</code>. The test attacker calls withdraw again from receive and should get nothing extra.</p>',
         '''
class Bank:
    def __init__(self):
        self.balance = {}
        self.vault = 0

    def deposit(self, who, amount):
        self.balance[who] = self.balance.get(who, 0) + amount
        self.vault += amount

    def withdraw(self, who):
        # your code here
        pass

class Evil:
    def __init__(self):
        self.got = 0
    def receive(self, bank, amount):
        self.got += amount
        try:
            bank.withdraw(self)
        except ValueError:
            pass

def run_attack():
    b = Bank()
    b.deposit("honest", 10)
    e = Evil()
    b.deposit(e, 1)
    b.withdraw(e)
    return e.got, b.vault
''', [('run_attack()', (1, 10))],
         '''
class Bank:
    def __init__(self):
        self.balance = {}
        self.vault = 0

    def deposit(self, who, amount):
        self.balance[who] = self.balance.get(who, 0) + amount
        self.vault += amount

    def withdraw(self, who):
        amount = self.balance.get(who, 0)
        if amount <= 0:
            raise ValueError("nothing to withdraw")
        self.balance[who] = 0
        self.vault -= amount
        who.receive(self, amount)

class Evil:
    def __init__(self):
        self.got = 0
    def receive(self, bank, amount):
        self.got += amount
        try:
            bank.withdraw(self)
        except ValueError:
            pass

def run_attack():
    b = Bank()
    b.deposit("honest", 10)
    e = Evil()
    b.deposit(e, 1)
    b.withdraw(e)
    return e.got, b.vault
''', 'Read the amount, check it, set the balance to 0, reduce the vault, and only then call receive.', '<p>Moving one line, the balance update, above the outside call is the whole fix. That is why auditors read the order of every function that sends value.</p>')
K.assign('checked_add', 'm', 'Checked and unchecked uint8 maths',
         '<p>Write <code>add_u8(a, b, checked)</code>. With <code>checked=False</code> return the sum wrapped into 0 to 255. With <code>checked=True</code> raise <code>OverflowError</code> if the true sum is outside 0 to 255, otherwise return it. b may be negative.</p>',
         '''
def add_u8(a, b, checked):
    # your code here
    pass
''', [('add_u8(250, 10, False)', 4), ('add_u8(0, -1, False)', 255), ('add_u8(7, -3, True)', 4), ('add_u8(200, 55, True)', 255)],
         '''
def add_u8(a, b, checked):
    s = a + b
    if checked:
        if s < 0 or s > 255:
            raise OverflowError("Panic(0x11)")
        return s
    return s % 256
''', 'Compute the true sum first. Python’s % already gives 255 for -1 % 256.', '<p>This is exactly the change Solidity 0.8 made: the same sum, plus one range check that turns a silent wrap into a cancelled transaction.</p>')
K.assign('cp_swap', 'h', 'A constant product swap',
         '<p>Write <code>swap_out(x, y, dx, fee)</code> for a pool with reserves x (token in) and y (token out). Apply the fee to the input, then return the output y &minus; x y / (x + dx (1 &minus; fee)) rounded to 4 decimals.</p>',
         '''
def swap_out(x, y, dx, fee):
    # your code here
    pass
''', [('swap_out(200000, 100, 200000, 0)', 50.0), ('swap_out(200000, 100, 20000, 0)', 9.0909), ('swap_out(100, 100, 100, 0)', 50.0), ('swap_out(200000, 100, 200000, 0.003)', 49.9249)],
         '''
def swap_out(x, y, dx, fee):
    dx_after = dx * (1 - fee)
    k = x * y
    return round(y - k / (x + dx_after), 4)
''', 'k = x * y stays fixed. The new y is k divided by the new x.', '<p>Notice how the output shrinks as the trade grows: half the pool’s USDC buys only half its ETH, at an average price of 4,000. That steep curve is what flash loan attackers and sandwich bots exploit.</p>')

K.must('Smart contracts', 'Public programs on the EVM that hold money. EOAs (keys) and contract accounts (code). Gas meters computation. EIP-1559: fee = gas &times; (base + tip), base burned, &plusmn;12.5% per block.')
K.must('Reentrancy', 'Sending value hands over control. The DAO, 17 June 2016, about 3.6 million ether, hard fork 20 July 2016, Ethereum Classic. Fix: checks, effects, interactions plus nonReentrant.')
K.must('Integer overflow', '(a op b) mod 2<sup>n</sup>. BeautyChain batchTransfer 2018 (2 &times; 2<sup>255</sup> = 0). Solidity 0.8 checked maths (December 2020), Panic 0x11. Watch unchecked blocks, casts, rounding.')
K.must('Access control', 'Parity July 2017 (open initWallet, about 153,000 ether) and November 2017 (library killed, 513,774 ether frozen). msg.sender not tx.origin. Ownable, AccessControl, initializer.')
K.must('Oracles and flash loans', 'x y = k, price x/y, output y &minus; k/(x + 0.997&Delta;x). Flash loans repaid in one transaction. bZx 2020, Harvest 2020, Mango 2022. TWAP and independent feeds.')
K.must('MEV', 'Public mempool, ordering by tip, sandwich attacks, slippage limits, private routes, commit and reveal. Daian et al. 2020.')
K.must('Bridges and process', 'Ronin (625 million, 5 of 9 keys), Wormhole, Nomad, Poly Network. Chain id and nonce in signatures, exact approvals. Audited libraries, tests, Slither, fuzzing invariants, formal verification, audits, bounties, timelocks.')

T = K.topic(
    slug='cy-ethereum', topic='cy-ethereum', step=(3, 'Blockchain and emerging systems', 'cy-a3', 'How blockchains, cryptocurrencies and smart contracts are secured, and how they are attacked.', 'Advanced'),
    title='Ethereum and smart contract security: reentrancy, overflow, oracles and MEV', short='Smart contract security', badge='3.2', minutes=90,
    lead='How programs that hold money on a blockchain get robbed and how to stop it: gas and fees, reentrancy and The DAO, integer overflow, access control and the Parity wallets, flash loans and price oracles, front running and sandwich attacks, bridge thefts and approvals, and a safe release process.',
    desc='Ethereum, smart contract, EVM, Solidity, gas, EIP-1559, reentrancy, The DAO, Ethereum Classic, checks effects interactions, nonReentrant, integer overflow, BeautyChain, SafeMath, Solidity 0.8, access control, Parity multisig, tx.origin, delegatecall, oracle, automated market maker, constant product, flash loan, price manipulation, TWAP, Chainlink, MEV, front running, sandwich attack, slippage, commit reveal, bridge, Ronin, Wormhole, Nomad, token approval, signature replay, audit, Slither, Echidna, Foundry, formal verification, bug bounty',
    summary='Smart contracts and gas, reentrancy and The DAO, integer overflow, access control and Parity, flash loans and oracles, MEV and sandwiches, bridges and approvals, and secure contract development.',
    keywords=['smart contract', 'Ethereum', 'reentrancy', 'The DAO', 'integer overflow', 'access control', 'flash loan', 'oracle', 'MEV', 'sandwich attack'],
    recap='<p>Update state before calling out, let the compiler check your maths, lock every privileged function, never trust a price one trade can move, and assume everyone can see your transaction before it lands.</p>',
    added='2026-11-22')
