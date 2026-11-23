# System administration 1.2: software packages. What a package and a repository are, apt update, upgrade, install,
# remove, purge, autoremove, search, show and list, manual and automatic packages, apt-mark hold, dpkg -l, -L, -S
# and -i, .deb files with dpkg-deb, sources files and signing keys, the RPM family (dnf, rpm), pacman and zypper,
# snap and flatpak, installing from source into /usr/local, unattended upgrades. Sources: apt(8), apt-get(8),
# apt-cache(8), apt-mark(8), sources.list(5), dpkg(1), dpkg-query(1), dpkg-deb(1), dnf(8), rpm(8), the Debian
# Policy Manual on maintainer scripts, the Ubuntu Server guide on unattended-upgrades.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('what', 'Packages, repositories and dependencies', f'''
<p>On Linux you rarely download programs from websites. A <b>package</b> is an archive with a program’s files plus facts about it: its name, version, the other packages it needs (its <b>dependencies</b>), and scripts to run when it is installed. Packages come from <b>repositories</b>, servers run by the distribution, and a <b>package manager</b> fetches, checks, installs, upgrades and removes them.</p>
{table(['Family', 'Package file', 'Low-level tool', 'Everyday tool', 'Used by'], [
    ['Debian', '<code>.deb</code>', 'dpkg', 'apt', 'Debian, Ubuntu, Linux Mint, Raspberry Pi OS'],
    ['Red Hat', '<code>.rpm</code>', 'rpm', 'dnf (yum on old systems)', 'Fedora, RHEL, Rocky Linux, AlmaLinux'],
    ['Arch', '<code>.pkg.tar.zst</code>', 'pacman', 'pacman', 'Arch Linux, Manjaro'],
    ['SUSE', '<code>.rpm</code>', 'rpm', 'zypper', 'openSUSE, SUSE Linux Enterprise']])}
{play('lx-apt')}
{run('Where packages come from on Ubuntu 24.04', """grep -v '^#' /etc/apt/sources.list.d/ubuntu.sources | grep .
dpkg -S /usr/bin/ls /usr/bin/sudo /usr/sbin/useradd
dpkg -l bash coreutils
apt-cache policy cowsay""", note='The sources file names the servers, the releases (noble is the code name of Ubuntu 24.04) and the components: main and restricted are supported by Canonical, universe and multiverse by the community. dpkg -S tells which package owns a file. In dpkg -l, ii means desired install and actually installed. apt-cache policy shows the version that is installed and the version apt would install, with the repository it comes from.')}
{note('The Signed-By key in the sources file is how apt knows that the package lists are genuine. Only add a third-party repository when you trust its owner, because its packages run their scripts as root.', 'warn')}
{talk('On Linux you seldom download programs from websites. Instead, the distribution keeps huge collections of ready made software, called repositories, and a package manager installs it for you. A package is an archive that holds the program’s files together with facts about it, such as its version and the other packages it depends on. Debian and Ubuntu use dot deb packages with the tools dpkg and apt. Fedora and Red Hat use dot r p m packages with rpm and dnf. Arch uses pacman. The ideas are the same everywhere. The list of repositories is in slash etc slash apt on Ubuntu, and each one is signed with a key, so apt can detect a fake. Every installed file belongs to exactly one package, and dpkg dash capital S tells you which. In the animation, watch apt find the dependencies of a package, download them, unpack them and set them up in the right order.')}
''', kw=['package', 'package manager', 'repository', 'dependencies', '.deb', '.rpm', 'dpkg -S', 'dpkg -l', 'sources.list', 'ubuntu.sources', 'main universe', 'apt-cache policy'])

K.lesson('apt', 'Installing, upgrading and removing with apt', f'''
{cmdtable([
    ('sudo apt update', 'Download fresh package lists from every repository. Run it before installing or upgrading', 'sudo apt update'),
    ('sudo apt upgrade', 'Install newer versions of installed packages', 'sudo apt update && sudo apt upgrade'),
    ('sudo apt full-upgrade', 'Upgrade even when packages must be added or removed to do it', 'sudo apt full-upgrade'),
    ('sudo apt install PKG...', 'Install packages and their dependencies', 'sudo apt install -y nginx'),
    ('sudo apt remove PKG', 'Remove the package, keep its configuration files', 'sudo apt remove nginx'),
    ('sudo apt purge PKG', 'Remove the package and its configuration files', 'sudo apt purge nginx'),
    ('sudo apt autoremove', 'Remove automatic dependencies that nothing needs any more', 'sudo apt autoremove'),
    ('apt search WORD, apt show PKG', 'Find packages, show details', 'apt show jq'),
    ('apt list --installed, --upgradable', 'List installed packages, or ones with updates', 'apt list --upgradable'),
    ('apt-mark hold PKG, apt-mark unhold PKG', 'Keep a package at its current version', 'sudo apt-mark hold postgresql-16')])}
{run('Install, use and remove a package, run as root', """apt-get install -y -q cowsay 2>&1 | grep -v -e 'Reading database' -e '^debconf'
dpkg -L cowsay | grep games/
/usr/games/cowsay "installed by apt"
apt-mark showauto | grep -x libtext-charwidth-perl
apt-get remove -y -q cowsay 2>&1 | grep -v 'Reading database'
apt-get autoremove -y -q 2>&1 | grep -v 'Reading database'""", root=True, note='apt pulled in libtext-charwidth-perl because cowsay depends on it, and marked it as automatic. The program went to /usr/games, which is not in the PATH of root or sudo, so it needs the full path. Removing cowsay left the automatic package behind until autoremove cleaned it up. Scripts use apt-get, because apt itself warns that its output may change between versions.')}
{note('Read the plan before you answer Y. Upgrades and removals can list far more packages than you expect, for example when a library change removes a desktop or a database server.', 'warn')}
{talk('Apt is the everyday tool on Debian and Ubuntu. Start with sudo apt update, which downloads the latest lists of packages from the repositories. It does not install anything. Then sudo apt upgrade installs newer versions of what you already have, and this is how a server gets its security fixes. Sudo apt install followed by a name installs a program together with everything it needs, and apt marks those extra packages as automatic. Remove takes a program away but keeps its settings, purge also deletes the settings, and autoremove cleans up automatic packages that nothing needs any more. Apt search and apt show help you find the right package. When you write scripts, use apt get instead of apt, because apt’s screen output may change between versions. And always read the summary before you say yes, especially before removals.')}
''', kw=['apt update', 'apt upgrade', 'apt full-upgrade', 'apt install', 'apt remove', 'apt purge', 'apt autoremove', 'apt search', 'apt show', 'apt list --installed', 'apt-mark hold', 'apt-get', 'automatic packages'])

K.lesson('deb', 'Inside a .deb file, and dpkg', f'''
<p>apt finds and downloads packages, then calls <b>dpkg</b> to do the actual installing. A .deb file is an archive with two parts: <b>control</b> (the facts and the maintainer scripts) and <b>data</b> (the files that go into the file tree).</p>
{cmdtable([
    ('dpkg -l [PKG]', 'List installed packages, with their state', 'dpkg -l | grep nginx'),
    ('dpkg -L PKG', 'Every file a package installed', 'dpkg -L openssh-server'),
    ('dpkg -S FILE', 'Which package owns a file', 'dpkg -S /usr/bin/ssh'),
    ('dpkg-deb -I FILE.deb, dpkg-deb -c FILE.deb', 'Show the control facts, list the files inside', 'dpkg-deb -c tool.deb'),
    ('sudo dpkg -i FILE.deb', 'Install a .deb file. It does not fetch dependencies', 'sudo dpkg -i ./tool.deb'),
    ('sudo apt install ./FILE.deb', 'Install a local .deb and fetch its dependencies from the repositories', 'sudo apt install ./tool_1.0_amd64.deb')])}
{run('Look inside a .deb file', """apt-get download figlet 2>/dev/null
ls *.deb
dpkg-deb -I figlet_*.deb | sed -n '1,8p'
dpkg-deb -I figlet_*.deb | grep -E '^ (Package|Version|Depends|Installed-Size):'
dpkg-deb -c figlet_*.deb | grep -E 'bin/'""", note='apt-get download fetched the file without installing it, so it worked as a normal user. The control part has the package facts and maintainer scripts such as postinst, which runs after the files are unpacked, and prerm, which runs before removal. The data part puts the programs in /usr/bin, the main one under the name figlet-figlet.')}
{run('Install and remove it with dpkg, run as root', """dpkg -i /home/learner/figlet_*.deb 2>&1 | grep -v -e 'Reading database' -e 'warning:'
figlet Hi
dpkg -r figlet 2>&1 | grep -v 'Reading database'""", root=True, keep=True, note='figlet only needs libc6, which every system has, so dpkg could install it alone. With a missing dependency dpkg would stop and leave the package half configured, and sudo apt install -f would then fetch what is missing. The postinst script registered /usr/bin/figlet through update-alternatives.')}
{talk('Under apt sits dpkg, the tool that really unpacks packages and keeps the database of every installed file in slash var slash lib slash dpkg. A dot deb file has two parts. The control part holds the facts, such as the name, version and dependencies, plus small maintainer scripts that run before and after installing or removing, for example to create a service user. The data part holds the files that go into the file tree. You can look inside without installing, using dpkg deb dash capital I for the facts and dash c for the file list. Dpkg dash i installs a downloaded dot deb file, but it does not fetch dependencies, so the better way is sudo apt install with a dot slash in front of the file name, which lets apt fetch whatever is missing. Dpkg dash capital L lists a package’s files, and dpkg dash capital S finds which package owns a file.')}
''', kw=['dpkg', 'dpkg -i', 'dpkg -L', 'dpkg -r', 'dpkg-deb', '.deb file', 'control archive', 'maintainer scripts', 'postinst', 'apt install ./file.deb', 'apt-get download', 'apt install -f'])

K.lesson('other', 'Other package managers, universal packages and source builds', f'''
{table(['Task', 'Debian, Ubuntu (apt)', 'Fedora, RHEL (dnf)', 'Arch (pacman)', 'openSUSE (zypper)'], [
    ['refresh lists', '<code>apt update</code>', '<code>dnf makecache</code> (also automatic)', 'part of <code>pacman -Syu</code>', '<code>zypper refresh</code>'],
    ['upgrade all', '<code>apt upgrade</code>', '<code>dnf upgrade</code>', '<code>pacman -Syu</code>', '<code>zypper update</code>'],
    ['install', '<code>apt install PKG</code>', '<code>dnf install PKG</code>', '<code>pacman -S PKG</code>', '<code>zypper install PKG</code>'],
    ['remove', '<code>apt remove PKG</code>', '<code>dnf remove PKG</code>', '<code>pacman -R PKG</code>', '<code>zypper remove PKG</code>'],
    ['search', '<code>apt search WORD</code>', '<code>dnf search WORD</code>', '<code>pacman -Ss WORD</code>', '<code>zypper search WORD</code>'],
    ['which package owns a file', '<code>dpkg -S FILE</code>', '<code>rpm -qf FILE</code>', '<code>pacman -Qo FILE</code>', '<code>rpm -qf FILE</code>'],
    ['files of a package', '<code>dpkg -L PKG</code>', '<code>rpm -ql PKG</code>', '<code>pacman -Ql PKG</code>', '<code>rpm -ql PKG</code>'],
    ['history', '<code>/var/log/apt/history.log</code>', '<code>dnf history</code>', '<code>/var/log/pacman.log</code>', '<code>/var/log/zypp/history</code>']])}
{table(['Way', 'Example', 'Good for', 'Watch out for'], [
    ['snap', '<code>sudo snap install code --classic</code>', 'apps bundled with their libraries, updated automatically', 'larger downloads, mainly Ubuntu'],
    ['Flatpak', '<code>flatpak install flathub org.gimp.GIMP</code>', 'desktop apps from Flathub, run in a sandbox', 'desktop use, not servers'],
    ['AppImage', '<code>chmod +x Tool.AppImage && ./Tool.AppImage</code>', 'one file that runs without installing', 'no automatic updates'],
    ['Language managers', '<code>pip</code>, <code>npm</code>, <code>cargo</code>', 'libraries for your own projects', 'use virtual environments, never sudo pip'],
    ['From source', '<code>./configure && make && sudo make install</code>', 'newest versions, custom builds', 'apt does not know these files, so no updates or clean removal']])}
{shape('Building from source (the GNU convention)', """tar xf tool-2.1.tar.gz && cd tool-2.1
./configure --prefix=/usr/local     # check the system, write the Makefile
make                                # compile
sudo make install                   # copy into /usr/local/bin, /usr/local/lib ...""", note='/usr/local is kept for software that the package manager does not manage, so the two never overwrite each other. /usr/local/bin comes before /usr/bin in PATH.')}
{talk('Other distributions use other tools, but they do the same jobs. On Fedora and Red Hat you type dnf install, on Arch pacman dash capital S, and on openSUSE zypper install. The table lets you translate between them. There are also universal formats that work across distributions. Snap and Flatpak bundle an application with its libraries and keep it updated, and Flatpak runs desktop apps in a sandbox. An AppImage is a single file you make executable and run. Programming languages have their own managers, such as pip and npm, which are for project libraries and should not be run with sudo. And when you need a version that no package offers, you can build from source with configure, make and make install, which by convention goes into slash usr slash local so it never collides with packaged files.')}
''', kw=['dnf', 'rpm -qf', 'yum', 'pacman', 'zypper', 'snap', 'flatpak', 'AppImage', 'build from source', './configure make make install', '/usr/local', 'apt vs dnf'])

K.lesson('practice', 'Practice: install a tool in the practice shell', f'''
<p>The practice shell has a small apt and dpkg with real Ubuntu 24.04 package data, so versions, sizes and dependencies match a real system. Downloads are pretend.</p>
{lab('Find, install, use and remove jq', [
    ('Try to run jq, which is not installed yet.', 'jq --version', [{'cmd': r'^\s*jq\b'}, {'code': 127}]),
    ('Refresh the package lists.', 'sudo apt update', [{'cmd': r'sudo\s+apt(-get)?\s+update'}, {'out': 'Reading package lists'}]),
    ('Search for packages about JSON.', 'apt search json', [{'cmd': r'apt(-cache)?\s+search'}, {'out': '^jq/'}]),
    ('Install jq without being asked to confirm.', 'sudo apt install -y jq', [{'exists': '/usr/bin/jq'}]),
    ('Print the version of jq.', 'jq --version', [{'out': '^jq-1\\.7\\.1$'}]),
    ('Use jq to print the name from the JSON {"name": "web1"}.', """echo '{"name": "web1"}' | jq -r .name""", [{'out': '^web1$'}]),
    ('Find which package owns /usr/bin/jq.', 'dpkg -S /usr/bin/jq', [{'out': '^jq: /usr/bin/jq$'}]),
    ('Remove jq without confirming.', 'sudo apt remove -y jq', [{'gone': '/usr/bin/jq'}]),
    ('Remove the libraries that came with it.', 'sudo apt autoremove -y', [{'gone': '/usr/lib/x86_64-linux-gnu/libjq.so.1'}])])}
{talk('Now try it yourself. The practice shell has a small version of apt that uses real Ubuntu twenty four point zero four package data, so the versions and sizes are the true ones. First check that jq, a popular tool for reading JSON, is missing. Then refresh the lists with sudo apt update, search for JSON, and install jq with dash y. Run it, print a value from a small JSON text, and ask dpkg which package owns its file. Finally remove jq and use autoremove to clean up the two libraries that came with it.')}
''', kw=['apt practice', 'install jq', 'apt lab', 'dpkg -S practice', 'autoremove practice'])

K.lesson('levels', 'Software management from school to research', f'''
{ladder(
    '<p>Install software from the distribution’s repositories with the package manager. Run sudo apt update and sudo apt upgrade often, because most updates are security fixes.</p>',
    '<p>Servers install security updates automatically with unattended-upgrades on Debian and Ubuntu, or dnf-automatic on Fedora and RHEL, and reboot in a planned window when the kernel changes (needrestart and /var/run/reboot-required tell you). Pin important versions with apt-mark hold, and read /var/log/apt/history.log to see what changed and when.</p>',
    '<p>Companies mirror repositories (aptly, Pulp, Artifactory) so every server installs exactly the same tested versions. Configuration management (Ansible, Puppet, Salt) states which packages must be present. Container images and image-based systems such as Fedora Silverblue or Ubuntu Core replace package by package upgrades with whole images that are swapped and can be rolled back.</p>',
    '<p>Reproducible builds aim for identical binary packages from identical source, so anyone can check that a package matches its code. Debian, Arch and others track this at reproducible-builds.org. Nix and Guix install every package under a path made from a hash of all its inputs, which allows many versions side by side and atomic rollbacks. The 2024 xz-utils backdoor showed why supply chain checks matter.</p>')}
{scene('the upgrade that broke production', '<p>An admin ran <code>sudo apt full-upgrade -y</code> on a database server on a Friday evening. A new major version of the database package was pulled in, and the service did not start because its data needed a migration. Since then, the team holds the database package with <code>apt-mark hold</code>, lets unattended-upgrades install only security updates, tests every upgrade on a staging copy first, and reads <code>/var/log/apt/history.log</code> after each change.</p>')}
{talk('Here is how software management grows up. At home, keeping a system updated is the single most important security habit. On servers, security updates are usually installed automatically with unattended upgrades, while bigger changes go through a test server first, and important packages are held at a fixed version. Larger companies keep their own copies of the repositories so that every machine gets exactly the same tested packages, and tools such as Ansible describe which packages each server must have. Newer systems go further and update the whole system as one image that can be rolled back. Researchers work on reproducible builds, which let anyone check that a binary package really comes from its published source code. And systems such as Nix give every package a unique path from a hash of its inputs, so many versions can live side by side.')}
''', kw=['unattended-upgrades', 'dnf-automatic', 'reboot-required', 'apt history.log', 'repository mirror', 'Ansible packages', 'image based OS', 'reproducible builds', 'Nix', 'Guix', 'supply chain', 'xz backdoor'])

K.quiz('e', 'Which command downloads fresh package lists on Ubuntu?', ['sudo apt upgrade', 'sudo apt update', 'sudo apt refresh', 'sudo apt list'], 1, 'Update the lists.', 'update only refreshes the lists.')
K.quiz('e', 'Which package file type does Fedora use?', ['.deb', '.rpm', '.apk', '.exe'], 1, 'Red Hat.', 'RPM packages.')
K.quiz('e', 'Which command installs a package on Debian?', ['sudo apt install PKG', 'sudo dnf install PKG', 'sudo pacman -S PKG', 'sudo get PKG'], 0, 'apt.', 'apt install.')
K.quiz('e', 'What is a dependency?', ['A virus', 'Another package that a package needs', 'A backup', 'A user group'], 1, 'Needs.', 'apt installs dependencies automatically.')
K.quiz('m', 'What is the difference between apt remove and apt purge?', ['None', 'purge also deletes configuration files', 'remove deletes more', 'purge only works on Fedora'], 1, 'Config.', 'remove keeps the configuration files.')
K.quiz('m', 'Which command shows which package owns /usr/bin/ssh?', ['dpkg -L /usr/bin/ssh', 'dpkg -S /usr/bin/ssh', 'apt show /usr/bin/ssh', 'which ssh'], 1, 'Search.', 'dpkg -S searches the file lists.')
K.quiz('m', 'Why should scripts use apt-get rather than apt?', ['apt-get is faster', 'apt’s output may change between versions', 'apt needs a desktop', 'apt cannot install'], 1, 'Stable interface.', 'apt warns about its unstable CLI.')
K.quiz('m', 'What does apt autoremove remove?', ['All packages', 'Automatic dependencies that nothing needs', 'Old kernels only', 'Configuration files'], 1, 'Orphans.', 'Automatic packages no longer required.')
K.quiz('m', 'Which command keeps a package at its current version?', ['apt-mark hold PKG', 'apt freeze PKG', 'dpkg -l PKG', 'apt lock PKG'], 0, 'Hold.', 'apt-mark hold.')
K.quiz('h', 'dpkg -i stopped because a dependency is missing. What fixes it?', ['Reboot', 'sudo apt install -f', 'sudo dpkg --force-all', 'Delete /var/lib/dpkg'], 1, 'Fix broken.', 'apt -f fetches the missing dependencies.')
K.quiz('h', 'Where does software built with ./configure && make install go by default?', ['/usr/bin', '/usr/local', '/opt/apt', '/home'], 1, 'Local.', 'The default prefix is /usr/local.')
K.quiz('h', 'What is the rpm equivalent of dpkg -L PKG?', ['rpm -qf PKG', 'rpm -ql PKG', 'rpm -i PKG', 'rpm -e PKG'], 1, 'Query list.', 'rpm -ql lists the files.')
K.quiz('h', 'Which maintainer script runs after a package’s files are unpacked?', ['prerm', 'postinst', 'preinst', 'postrm'], 1, 'After install.', 'postinst runs after unpacking.')
K.quiz('x', 'What guarantees that apt’s package lists were not changed by an attacker?', ['HTTPS only', 'The Release file signed with the repository key, with hashes of the lists', 'File names', 'dpkg -S'], 1, 'Signed.', 'The signature covers hashes of the lists, which cover each .deb.')

K.calc('e', 'apt says it will install 3 new packages and 0 others change. How many packages appear on the NEW line?', '3', 'Count them.', ['The summary says 3 newly installed.', 'All of them are new.', eq('3')], check=3)
K.calc('e', 'jq needs libjq1, and libjq1 needs libonig5. How many packages does sudo apt install jq add on a fresh system?', '3', 'Follow the chain.', ['jq itself.', 'libjq1 and libonig5.', eq('1 + 2 = 3')], check=3)
K.calc('m', 'cowsay is 91 KiB and libtext-charwidth-perl 41 KiB. How many KiB do both use?', '132', 'Add them.', ['91 + 41.', 'apt shows it as 135 kB, since it multiplies by 1024 and divides by 1000.', eq('132 KiB')], check=132)
K.calc('m', 'Downloads of 18572 and 9358 bytes. What is the total in bytes?', '27930', 'apt shows 27.9 kB.', ['18572 + 9358.', 'Divide by 1000 for kB.', eq('27930 B')], check=27930)
K.calc('h', 'Removing jq frees 113 KiB. How many bytes is that?', '115712', 'Times 1024.', ['1 KiB is 1024 bytes.', '113 × 1024.', eq('115712 B')], check=115712)
K.calc('h', 'A server has 41 upgradable packages and you hold 2 of them. How many will apt upgrade install?', '39', 'Holds are skipped.', ['Held packages stay.', '41 − 2.', eq('39')], check=39)

K.must('apt', 'sudo apt update, then upgrade. install, remove, purge (also config), autoremove, search, show, list --installed.')
K.must('dpkg', 'dpkg -l lists, -L files of a package, -S owner of a file, -i installs a .deb without dependencies.')
K.must('Repositories', 'Listed in /etc/apt/sources.list.d, signed with keys. Add third-party ones only when you trust them.')
K.must('Other families', 'dnf and rpm (Fedora, RHEL), pacman (Arch), zypper (SUSE). snap and Flatpak bundle apps.')
K.must('Safe habits', 'Read the plan before Y, use apt-get in scripts, hold critical packages, automatic security updates, build from source into /usr/local.')

T = K.topic(
    slug='packages', topic='packages',
    step=(1, 'Users and software', 'lx-admin-1', 'Manage accounts, groups and sudo rights, and install, update and remove software with package managers.', 'Intermediate'),
    title='Installing software: apt, dpkg and other package managers', short='Packages', badge='1.2', minutes=50, added='2026-11-23',
    lead='Install, upgrade and remove software with apt, understand repositories, dependencies and .deb files, translate the commands to dnf, pacman and zypper, and know when snap, Flatpak or a source build makes sense.',
    desc='Packages, repositories and signing, apt update, upgrade, full-upgrade, install, remove, purge, autoremove, search, show and list, automatic packages and apt-mark hold, dpkg -l, -L, -S and -i, dpkg-deb and maintainer scripts, dnf and rpm, pacman, zypper, snap, Flatpak, AppImage, building from source into /usr/local, and unattended upgrades.',
    summary='Repositories and dependencies, apt and dpkg, .deb files, other package managers, snap and Flatpak, source builds.',
    keywords=['apt', 'apt-get', 'dpkg', 'deb', 'rpm', 'dnf', 'pacman', 'zypper', 'snap', 'flatpak', 'repository', 'dependency'],
    recap='<p>Package managers install software from signed repositories with all its dependencies. apt update refreshes the lists, apt upgrade installs fixes, and install, remove, purge and autoremove manage packages, while dpkg works with single .deb files and the database of installed files. dnf, pacman and zypper do the same jobs on other distributions.</p>')
