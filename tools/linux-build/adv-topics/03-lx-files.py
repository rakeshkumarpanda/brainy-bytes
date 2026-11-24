# Internals and advanced 2.1: files inside. Directory entries and inodes, what an inode holds, inode numbers and
# df -i, running out of inodes, the seven file types, hard links and symbolic links (link counts, dangling links,
# cross-device links, protected_hardlinks), rename and unlink, file descriptors and open file descriptions, files
# that are deleted but still open (lsof +L1, /proc/PID/fd), the VFS, the page cache, write-back and fsync.
# Sources: inode(7), stat(2), stat(1), link(2), symlink(7), unlink(2), rename(2), open(2), close(2), dup(2), fsync(2),
# sync(1), proc(5) (/proc/PID/fd and fdinfo), lsof(8), find(1) (-inum, -samefile, -xtype), mkfifo(1), debugfs(8),
# mke2fs(8) (-N), df(1), the kernel documentation (filesystems/vfs.rst, admin-guide/sysctl/fs.rst protected_hardlinks,
# admin-guide/sysctl/vm.rst dirty_ratio and dirty_expire_centisecs).
# Real boxes run in the build container: file types and links as the user learner, inode exhaustion on a 64 MiB
# ext4 image with only 64 inodes mounted from a loop device, and a deleted file that a Python process still holds.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('inode', 'Names, inodes and data', f'''
<p>A file on Linux has three parts. Its <b>name</b> is an entry in a folder. The entry points to an <b>inode</b>, a numbered record with everything else about the file. The inode points to the <b>data blocks</b> with the content.</p>
{table(['An inode holds', 'An inode does not hold'], [
    ['the type and the permission bits', 'the name, which lives in the folder'],
    ['the owner and group (as numbers)', 'the path, a file can have several'],
    ['the size and the block or extent list', ''],
    ['the times: access, modify, change, birth', ''],
    ['the link count: how many names point to it', '']])}
{play('lx-inode')}
{run('The seven file types and their inodes', """echo 'Buy milk' > notes.txt
mkdir box
ln -s notes.txt link
mkfifo pipe
ls -lid notes.txt box link pipe
stat -c '%n: inode %i, %h links, %F' notes.txt box link pipe /dev/null
ls -id / /home .""", note='The first column of ls -i is the inode number, and the first letter of the mode is the type: - regular file, d directory, l symbolic link, p named pipe (FIFO), c character device such as /dev/null, b block device such as /dev/sda, s socket. A new folder starts with 2 links, its name in the parent and its own . entry, and every subfolder adds one more for its .. entry. The root folder of an ext4 file system is always inode 2, which is what / shows. Inode numbers are only unique inside one file system, and /home shows a low number too because it is a separate file system in the build container.')}
{run('Run out of inodes while the disk is nearly empty', """mkdir -p /mnt/tiny
cd "$(mktemp -d)"
truncate -s 64M disk.img
mkfs.ext4 -q -N 64 disk.img
mount -o loop disk.img /mnt/tiny
for i in $(seq 1 70); do touch /mnt/tiny/f$i || break; done
df -i /mnt/tiny
df -h /mnt/tiny
umount /mnt/tiny
debugfs -R 'ls -l /' disk.img 2> /dev/null | head -n 5""", note='mkfs.ext4 -N 64 makes a file system with only 64 inodes. The first 11 are reserved (2 is the root folder, 11 is lost+found), so touch fails at the 54th file with “No space left on device”, although df -h shows 56M free. df -i shows 100 % of inodes used. Real servers hit this with millions of tiny files, such as session files or a mail queue. debugfs reads the image directly and shows the inode number, the mode in octal (40755 is a folder, 100644 a regular file) and the link count of each entry.', root=True)}
{talk('A file on Linux is more than its name. The name is only an entry in a folder, and it points to an inode, a numbered record that holds everything else: the type, the owner, the permissions, the size, the times, and where the data is stored. The inode also counts how many names point to it. You can see inode numbers with ls dash i and stat. Every file system has a fixed number of inodes, set when it is made. In the demo, a tiny file system runs out of inodes after fifty three files, while the disk is still almost empty, and touch reports no space left on device. Df dash i shows the inode usage, and it is the first thing to check when that error appears on a disk with free space.')}
''', kw=['inode', 'inode number', 'ls -i', 'stat', 'directory entry', 'dentry', 'link count', 'data blocks', 'extents', 'file types', 'regular file', 'named pipe', 'FIFO', 'mkfifo', 'character device', 'block device', 'socket file', 'df -i', 'inode exhaustion', 'No space left on device', 'mkfs.ext4 -N', 'debugfs'])

K.lesson('links', 'Hard links and symbolic links', f'''
{table(['', 'Hard link (ln)', 'Symbolic link (ln -s)'], [
    ['What it is', 'a second name for the same inode', 'a small file that holds a path'],
    ['Inode', 'the same number', 'its own inode, type l'],
    ['Link count', 'goes up by one', 'does not change'],
    ['Target removed', 'the data stays while any name is left', 'the link dangles and opening it fails'],
    ['Across file systems', 'no (Invalid cross-device link)', 'yes'],
    ['To folders', 'no', 'yes'],
    ['Typical use', 'snapshots that share unchanged files (rsync --link-dest), package tools', 'versions (python3 → python3.12), /etc/alternatives, config in a repo']])}
{run('Make, change, delete and break links', """echo 'Call grandma' > notes.txt
ln notes.txt copy
ln -s notes.txt link
ls -li notes.txt copy link
echo 'Water plants' >> copy
cat notes.txt
rm notes.txt
cat copy
cat link
find . -xtype l
ln copy /dev/shm/copy
ln /etc/hostname myhost""", note='notes.txt and copy share one inode with link count 2, so text added through copy appears in notes.txt. After rm notes.txt the data is still there under the name copy. The symbolic link stores only the path notes.txt, so it now dangles and cat fails. find -xtype l finds such broken links. A hard link to /dev/shm fails, because it is another file system (tmpfs). The last line fails for a different reason: Ubuntu sets fs.protected_hardlinks = 1, so you may only hard link files you own or can read and write, which stops tricks with links to root’s files in shared folders.')}
{cmdtable([
    ('ln TARGET NAME', 'Hard link: another name for the same inode', 'ln report.pdf report-2026.pdf'),
    ('ln -s TARGET NAME', 'Symbolic link (the target path is stored as text)', 'ln -s /srv/app/releases/v42 /srv/app/current'),
    ('ln -sfn TARGET NAME', 'Replace an existing link, also one that points to a folder', 'ln -sfn releases/v43 current'),
    ('readlink LINK, readlink -f PATH', 'The stored path, or the final real path after all links', 'readlink -f /usr/bin/python3'),
    ('find -samefile F, find -inum N', 'All names of one inode', 'find / -xdev -samefile notes.txt'),
    ('find -xtype l', 'Dangling symbolic links', 'find /etc -xtype l')])}
{note('A relative symbolic link is resolved from the folder the link is in, not from your current folder. ln -s ../shared/config.yml app/config.yml works, ln -s shared/config.yml app/config.yml from the parent folder makes a link that points to app/shared/config.yml.', 'warn')}
{talk('There are two kinds of links. A hard link is a second name for the same inode. Both names are equal, a change through one is visible through the other, and the data stays until the last name is gone. Hard links only work inside one file system and not for folders. A symbolic link is a tiny file of its own that stores a path. The kernel follows that path whenever a program opens the link, so symbolic links can point to folders and to other disks. But if the target is deleted or moved, the link dangles. In the demo you see the shared inode number, the link count of two, a dangling link, and two refused hard links: one to another file system, and one to a file that belongs to root.')}
''', kw=['hard link', 'symbolic link', 'symlink', 'soft link', 'ln', 'ln -s', 'ln -sfn', 'link count', 'dangling link', 'broken symlink', 'find -xtype l', 'find -samefile', 'find -inum', 'readlink -f', 'Invalid cross-device link', 'protected_hardlinks', 'relative symlink'])

K.lesson('fds', 'Open files: descriptors and deleted files', f'''
{steps('Three tables behind every open file', [
    'Each process has a <b>file descriptor table</b>: small numbers 0, 1, 2, 3 and so on. You see it in <code>/proc/PID/fd</code>.',
    'Each descriptor points to an <b>open file description</b> in the kernel, which holds the current offset and the open flags (read, write, append). After fork, or after dup2, two descriptors share one description, and therefore one offset. That is why the lines of a parent and a child do not overwrite each other in a shared log.',
    'The description points to the <b>inode</b>. The kernel counts open descriptions as well as names, and frees the data only when both reach zero.'])}
{run('A file deleted while a program still writes it', """python3 -c 'import time; f = open("big.log", "w"); f.write("x" * 5000000); f.flush(); time.sleep(20)' &
sleep 1
ls -l big.log
rm big.log
ls -l /proc/$!/fd | grep big
lsof -p $! 2> /dev/null | grep deleted
cp /proc/$!/fd/3 rescued.log
ls -l rescued.log
kill $!""", note='After rm the name is gone, but the Python process still has the file open on descriptor 3, so the 5 MB stay on the disk and df does not go down. /proc/PID/fd shows the link with “(deleted)”, and lsof shows the same with the size and the inode number. Copying from /proc/PID/fd/3 rescues the content, which has saved many deleted databases and logs. On a server, <code>sudo lsof +L1</code> lists every open file whose link count is 0.')}
{cmdtable([
    ('lsof -p PID', 'Every file, socket and pipe a process has open', 'sudo lsof -p 905'),
    ('lsof FILE, fuser -v FILE', 'Who has this file open (why umount says busy)', 'sudo lsof /var/log/syslog'),
    ('lsof +L1', 'Open files that were deleted (link count 0)', 'sudo lsof +L1'),
    ('lsof -i :PORT', 'Who uses a network port', 'sudo lsof -i :80'),
    (': > FILE', 'Empty a file in place, without deleting it, so writers keep working', 'sudo sh -c ": > /var/log/huge.log"'),
    ('ulimit -n', 'The most descriptors one process may open', 'ulimit -n')])}
{note('“Too many open files” (EMFILE) means a process hit its descriptor limit, often 1024. Check <code>ls /proc/PID/fd | wc -l</code> to see whether it leaks descriptors, and raise the limit in the service with LimitNOFILE= only if the program really needs that many.', 'tip')}
{talk('When a program opens a file, the kernel gives it a small number called a file descriptor. Zero, one and two are standard input, output and error, and new files get three, four and so on. Slash proc slash P I D slash f d shows every descriptor of a process. The kernel keeps a file’s data as long as any name points to it or any process has it open. That is why deleting a huge log that a service still writes does not free any space. In the demo, the deleted file still shows up in slash proc with the word deleted, lsof finds it, and copying from slash proc rescues the content. To free the space safely, empty the file in place instead of deleting it, or restart the service.')}
''', kw=['file descriptor', 'fd', 'file descriptor table', 'open file description', 'offset', '/proc/PID/fd', 'lsof', 'lsof +L1', 'lsof -i', 'fuser', 'deleted but open', '(deleted)', 'recover deleted file', 'disk full after rm', 'truncate file', 'ulimit -n', 'Too many open files', 'EMFILE', 'LimitNOFILE'])

K.lesson('cache', 'The VFS, the page cache and fsync', f'''
{steps('What happens to a write()', [
    'The <b>VFS</b> (virtual file system) is the common layer that turns open, read and write into calls of the right file system driver: ext4, xfs, vfat, tmpfs, NFS, procfs and so on.',
    'write() copies your data into the <b>page cache</b> in RAM and returns at once. The pages are now <b>dirty</b>: newer in memory than on disk.',
    'Kernel flusher threads write dirty pages to the disk later, after about 30 seconds (vm.dirty_expire_centisecs = 3000) or sooner when too much memory is dirty (vm.dirty_background_ratio and vm.dirty_ratio).',
    '<b>fsync(fd)</b> makes the kernel write a file’s dirty data and metadata to the disk now and waits until the disk confirms it. <code>sync</code> does that for everything. Databases call fsync before they tell you a transaction is saved.',
    'Reads go through the same cache. A file read twice comes from RAM the second time, which is why the buff/cache column of free is large on a healthy server. That memory is given back as soon as programs need it.'])}
{table(['Situation', 'What it means for you'], [
    ['power loss right after cp', 'the copy may be incomplete unless you ran sync. Pull a USB stick only after umount or eject'],
    ['a program says “saved”', 'only true after fsync. Editors and databases do it, simple scripts usually do not'],
    ['free shows little free memory', 'normal: look at the available column, which counts cache that can be dropped'],
    ['benchmarking a disk', 'the cache makes reads look too fast. Use fio with --direct=1, or drop the cache first with <code>echo 3 | sudo tee /proc/sys/vm/drop_caches</code> on a test machine only'],
    ['rename to replace a file', 'write a temp file, fsync it, then rename it over the old name. Readers see the old or the new file, never half of one']])}
{shape('Writing a file safely', """write new content to  config.yml.tmp
fsync(config.yml.tmp)          the data is on the disk
rename(config.yml.tmp, config.yml)   atomic switch
fsync(the folder)              the new name is on the disk""", note='This is how editors, package managers and databases avoid half written files after a crash. In shell scripts, mv on one file system is the rename step, and the sync command can do the fsync steps.')}
{talk('Under every file system sits the V F S, the virtual file system, which gives all of them the same open, read and write calls. When a program writes, the data first lands in the page cache in memory, and write returns at once. The kernel writes these dirty pages to the disk a little later, usually within thirty seconds. This makes Linux fast, but it means a power cut can lose the last seconds of writes. Fsync tells the kernel to write one file to the disk now and to wait until it is safe, and sync does it for everything. Reads use the same cache, which is why Linux seems to use a lot of memory for buff slash cache. That memory is handed back the moment programs need it.')}
''', kw=['VFS', 'virtual file system', 'page cache', 'buffer cache', 'dirty pages', 'write-back', 'fsync', 'fdatasync', 'sync', 'dirty_ratio', 'dirty_background_ratio', 'dirty_expire_centisecs', 'drop_caches', 'O_DIRECT', 'atomic rename', 'safe file write', 'buff/cache'])

K.lesson('practice', 'Practice: inodes and links on the practice server', f'''
<p>Explore inodes and links in your home folder on the practice server.</p>
{lab('Inodes and links', [
    ('Show the inode number of notes.txt.', 'ls -i notes.txt', [{'out': r'^\d+ notes\.txt'}]),
    ('Make a hard link called notes-copy.txt.', 'ln notes.txt notes-copy.txt', [{'cmd': r'^ln\s+(?!-s)'}, {'exists': 'notes-copy.txt'}]),
    ('List both with ls -li to see the shared inode and the link count 2.', 'ls -li notes.txt notes-copy.txt', [{'out': r' 2 learner'}]),
    ('Print inode, link count and type of notes.txt with stat -c.', 'stat -c "%i %h %F" notes.txt', [{'out': r'^\d+ 2 regular file$'}]),
    ('Find every name of the same inode in your home folder.', 'find . -samefile notes.txt', [{'out': 'notes-copy.txt'}]),
    ('Make a symbolic link todo that points to notes.txt.', 'ln -s notes.txt todo', [{'cmd': r'ln\s+-s'}]),
    ('Show where todo finally leads.', 'readlink -f todo', [{'out': '/home/learner/notes.txt'}]),
    ('Delete notes.txt.', 'rm notes.txt', [{'cmd': r'^rm\s+notes\.txt'}]),
    ('Read notes-copy.txt, which still has the data.', 'cat notes-copy.txt', [{'out': 'Buy milk'}]),
    ('Try to read todo, which now dangles.', 'cat todo', [{'code': 1}]),
    ('Try a hard link to /etc/hostname, which belongs to root.', 'ln /etc/hostname myhost', [{'out': 'Operation not permitted'}]),
    ('Make a named pipe called jobs.', 'mkfifo jobs', [{'cmd': r'mkfifo\s+jobs'}]),
    ('Show its type letter with ls -l.', 'ls -l jobs', [{'out': r'^p'}])])}
{talk('Now try inodes and links yourself. Show the inode number of notes, make a hard link, and see the same number and a link count of two. Use stat to print the inode, the link count and the type, and find every name of the inode with find dash samefile. Then make a symbolic link and follow it with readlink dash f. Delete notes and see that the hard link still has the data while the symbolic link dangles. Try a hard link to a file of root, which Ubuntu refuses, and finally make a named pipe and look at its type letter.')}
''', kw=['inode lab', 'hard link practice', 'symlink practice', 'mkfifo practice'])

K.lesson('levels', 'Files from school to research', f'''
{ladder(
    '<p>A file’s name is like a label on a box. The box (the inode) holds the details and points to the contents. You can stick several labels on one box (hard links) or write down where another box is (symbolic links).</p>',
    '<p>Read inode numbers and link counts, use hard and symbolic links on purpose, check df -i when “No space left” appears on a disk with space, find deleted but open files with lsof +L1, empty logs with : &gt; instead of rm, and write files safely with a temp file, fsync and rename.</p>',
    '<p>Storage engineers plan inode counts (mkfs -N or -i) for millions of small files, use reflinks on XFS and Btrfs (cp --reflink) that share data blocks until one copy changes, deduplicate backups with hard links (rsync --link-dest), tune the dirty page settings for write heavy servers, and debug with debugfs, xfs_db and filefrag.</p>',
    '<p>Research covers crash consistency (studies such as “All File Systems Are Not Created Equal”, OSDI 2014, found many applications that lose data because they rename without fsync), copy on write file systems (Btrfs, ZFS, bcachefs), file systems for persistent memory, and user space file systems with FUSE and io_uring.</p>')}
{scene('the disk that was full with space left', '<p>A PHP web shop suddenly showed errors, and logs said “No space left on device”. df -h showed 40 % free. A colleague ran df -i: 100 % of inodes were used. A broken cleanup job had left 6 million session files in /var/lib/php/sessions. Deleting the old files with <code>find /var/lib/php/sessions -type f -mmin +1440 -delete</code> freed the inodes, and the team fixed the cleanup timer and added an inode alert to the monitoring.</p>')}
{talk('Here is how understanding files grows. At school you learn that a name is a label on a box, and that one box can have several labels. Professionals read inode numbers and link counts, check d f dash i when a disk with free space says it is full, find deleted files that are still open, and write important files safely with fsync and rename. Storage engineers plan inode counts, share data between copies with reflinks, and build backups from hard links. Researchers study how programs lose data after crashes and design new copy on write file systems.')}
''', kw=['reflink', 'cp --reflink', 'rsync --link-dest', 'deduplication', 'crash consistency', 'copy on write file system', 'Btrfs', 'ZFS', 'bcachefs', 'FUSE', 'filefrag', 'xfs_db', 'mkfs -i'])

K.quiz('e', 'Where is a file’s name stored?', ['In the inode', 'In the folder that contains it', 'In the data blocks', 'In /etc/files'], 1, 'Folder entries.', 'The inode has everything else.')
K.quiz('e', 'Which command shows inode numbers?', ['ls -i', 'ls -n', 'df -h', 'du'], 0, 'i for inode.', 'stat shows it too.')
K.quiz('e', 'What does ln -s make?', ['A hard link', 'A symbolic link', 'A copy', 'A folder'], 1, 's for symbolic.', 'It stores a path.')
K.quiz('e', 'What does the first letter p in ls -l mean?', ['A program', 'A named pipe (FIFO)', 'Protected', 'A partition'], 1, 'Pipe.', 'Made with mkfifo.')
K.quiz('m', 'You delete one of two hard links to a file. What happens to the data?', ['It is deleted', 'It stays, because one name still points to the inode', 'It is moved to the trash', 'It becomes read only'], 1, 'Link count.', 'Freed only at 0.')
K.quiz('m', 'The target of a symbolic link is deleted. What happens?', ['The link is deleted too', 'The link dangles and opening it fails', 'The link keeps the data', 'The target comes back'], 1, 'It stores a path.', 'find -xtype l finds them.')
K.quiz('m', 'touch says “No space left on device” but df -h shows free space. What do you check next?', ['free -h', 'df -i', 'top', 'lsblk'], 1, 'Inodes.', 'Too many small files.')
K.quiz('m', 'Why does ln fail with “Invalid cross-device link”?', ['No permission', 'Hard links cannot span file systems', 'The file is open', 'The disk is full'], 1, 'Inodes are per file system.', 'Use ln -s instead.')
K.quiz('m', 'Why does deleting a big log not free space?', ['rm is slow', 'A process still has the file open', 'The trash keeps it', 'df is cached'], 1, 'Open descriptors.', 'lsof +L1 shows it.')
K.quiz('h', 'How do you empty a log that a service still writes, without restarting it?', ['rm the file', ': > file', 'mv file /tmp', 'chmod 000 file'], 1, 'Truncate in place.', 'Same inode, size 0.')
K.quiz('h', 'What do two descriptors share after dup2 or fork?', ['Nothing', 'One open file description, including the offset', 'Only the name', 'Only the inode number'], 1, 'Shared offset.', 'Appends do not overwrite each other.')
K.quiz('h', 'A program writes a file and the power fails 5 seconds later. Why may the file be missing?', ['Disks are slow', 'The data was still dirty in the page cache, and the program did not call fsync', 'The VFS lost it', 'The inode table is full'], 1, 'Write-back.', 'fsync forces it to disk.')
K.quiz('h', 'Why do editors write to a temp file and then rename it?', ['To save memory', 'rename is atomic, so readers never see a half written file', 'To keep a backup', 'rename is faster than write'], 1, 'Atomic switch.', 'fsync before rename.')
K.quiz('x', 'Why can a new folder have link count 2?', ['A bug', 'Its name in the parent and its own . entry both point to its inode', 'It has two files', 'ext4 counts twice'], 1, '. and the name.', 'Each subfolder adds one for ..')

K.calc('e', 'A file has 3 hard links. You delete 2 of them. What is the link count now?', '1', 'Subtract.', ['3 names.', '3 − 2.', eq('1 link')], check=1)
K.calc('e', 'A folder contains 4 subfolders. What is its link count?', '6', '2 plus one per subfolder.', ['2 for its name and .', '4 subfolders add one .. each.', eq('2 + 4 = 6')], check=6)
K.calc('m', 'mke2fs makes one inode per 16 KiB. How many inodes does a 64 GiB file system get?', '4194304', 'Divide the sizes.', ['64 GiB = 67108864 KiB.', '67108864 ÷ 16.', eq('4194304 inodes')], check=4194304)
K.calc('m', 'Each inode on ext4 is 256 bytes. How many KiB does a table of 4096 inodes use?', '1024', 'Multiply, then divide by 1024.', ['4096 × 256 = 1048576 bytes.', '÷ 1024.', eq('1024 KiB')], check=1024)
K.calc('h', 'A mail server stores 2 million messages, one file each. The file system has 1310720 inodes. How many messages are too many?', '689280', 'Subtract.', ['2000000 messages.', '1310720 inodes, ignoring the reserved ones.', eq('2000000 − 1310720 = 689280')], check=689280)
K.calc('h', 'A deleted log is still open and grows by 30 MB per minute. How many GB does it fill in 10 hours (1 GB = 1000 MB)?', '18', 'Minutes in 10 hours.', ['600 minutes.', '600 × 30 MB = 18000 MB.', eq('18 GB')], check=18)
K.calc('x', 'Dirty pages are written after 30 s at the latest. A program writes 20 MB per second and never calls fsync. At most how many MB can a power cut lose?', '600', 'Rate times delay.', ['Up to 30 s of writes.', '20 MB × 30.', eq('600 MB')], check=600)

K.must('Inodes', 'Name in the folder, everything else in the inode (type, owner, mode, size, times, link count, blocks). ls -i, stat, df -i. Running out of inodes gives No space left on device.')
K.must('File types', '- regular, d folder, l symlink, p FIFO, c and b devices, s socket.')
K.must('Links', 'ln: same inode, count +1, one file system, no folders. ln -s: own inode with a path, can dangle. readlink -f, find -samefile, find -xtype l.')
K.must('Open files', 'Descriptors in /proc/PID/fd, data freed only when no name and no open descriptor are left. lsof +L1, : > file to empty in place.')
K.must('Page cache', 'write lands in RAM as dirty pages, written back within about 30 s. fsync and sync force it. Safe write: temp file, fsync, rename.')

T = K.topic(
    slug='files-inside', topic='files-inside',
    step=(2, 'Files and memory inside', 'lx-adv-2', 'See what files and memory really are to the kernel: inodes, links and open descriptors, the page cache, virtual memory, swapping and the OOM killer.', 'Expert'),
    title='Files inside: inodes, links, open descriptors and the page cache', short='Files inside', badge='2.1', minutes=55, added='2026-11-24',
    lead='Learn what a file really is to the kernel: a name in a folder that points to an inode, hard and symbolic links, descriptors that keep deleted files alive, and the page cache that makes writes fast but needs fsync to be safe.',
    desc='Folder entries and inodes, file types, inode numbers and inode exhaustion on a real ext4 image, hard and symbolic links with cross-device and protected_hardlinks errors, file descriptors and open file descriptions, deleted but open files with lsof and /proc/PID/fd, the VFS, the page cache, write-back, fsync and atomic rename.',
    summary='Inodes, file types, hard and symbolic links, descriptors, deleted open files, page cache.',
    keywords=['inode', 'hard link', 'symbolic link', 'ln', 'link count', 'df -i', 'file descriptor', 'lsof', 'deleted open file', 'VFS', 'page cache', 'fsync', 'dirty pages', 'mkfifo'],
    recap='<p>A folder maps names to inode numbers, and the inode holds the rest of the file. Hard links add names to one inode, symbolic links store a path and can dangle. The kernel frees data only when no name and no open descriptor remain, so lsof +L1 finds space held by deleted files. Writes go to the page cache first, and fsync plus rename makes them safe.</p>')
