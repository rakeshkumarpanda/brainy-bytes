# System administration 3.2: LVM, RAID, swap and backups. LVM physical volumes, volume groups, logical volumes and
# 4 MiB extents (pvcreate, vgcreate, vgextend, lvcreate, lvextend -r, pvs, vgs, lvs, pvmove, snapshots), software RAID
# with mdadm and /proc/mdstat (levels 0, 1, 5, 6, 10, replacing a failed disk), swap partitions and swap files
# (mkswap, swapon, swapoff, fstab, vm.swappiness), and backups (3-2-1 rule, tar full and incremental archives with
# --listed-incremental, rsync -a --delete --dry-run, --link-dest snapshots, restore tests, restic and borg).
# Sources: lvm(8), pvcreate(8), vgcreate(8), lvcreate(8), lvextend(8), lvmthin(7), lvs(8), mdadm(8), md(4),
# mkswap(8), swapon(8), fallocate(1), proc(5) for /proc/sys/vm/swappiness, the kernel admin guide on sysctl/vm,
# tar(1) and the GNU tar manual on incremental dumps, rsync(1), restic and BorgBackup documentation, and real runs
# on loop devices in the build container (lvcreate and mdadm need kernel modules the container lacks, so their output
# comes from the practice shell or is marked as typical).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('lvm', 'LVM: storage pools made of disks', f'''
<p>A partition is fixed in size and stuck on one disk. The <b>Logical Volume Manager</b> (LVM) adds a layer in between, so volumes can grow, span several disks and move between them while they are in use.</p>
{table(['Layer', 'What it is', 'Made with', 'Listed with'], [
    ['Physical volume (PV)', 'a disk or partition with an LVM label, cut into extents of 4 MiB', '<code>pvcreate /dev/sdc</code>', '<code>pvs</code>, <code>pvdisplay</code>'],
    ['Volume group (VG)', 'a pool of extents from one or more PVs', '<code>vgcreate vgdata /dev/sdc</code>', '<code>vgs</code>, <code>vgdisplay</code>'],
    ['Logical volume (LV)', 'a block device cut from the pool, used like a partition', '<code>lvcreate -n web -L 10G vgdata</code>', '<code>lvs</code>, <code>lvdisplay</code>']])}
{play('lx-lvm')}
{run('Physical volumes and a volume group on two loop devices', """cd "$(mktemp -d)"
truncate -s 1G d1.img d2.img
a=$(losetup -f --show d1.img)
b=$(losetup -f --show d2.img)
pvcreate "$a" "$b"
vgcreate vgdata "$a" "$b"
pvs
vgs
vgdisplay vgdata | grep -E 'VG Size|PE Size|Total PE|Free  PE'
vgremove -q vgdata
pvremove -q "$a" "$b"
losetup -d "$a" "$b\"""", note='Each 1 GiB PV gives 1020 MiB, because LVM keeps 1 MiB for its own metadata and counts only whole 4 MiB extents. The pool holds 510 extents. The Attr column a-- means the PV is allocatable. Creating logical volumes needs the device-mapper driver of the kernel, which this build container lacks, so the next box comes from the practice shell.', root=True)}
{sample('Cut a logical volume from the pool, format it and mount it', """sudo lvcreate -n web -L 12G vgdata
sudo lvs
sudo mkfs.ext4 -q -L web /dev/vgdata/web
sudo mkdir /srv/web
sudo mount /dev/vgdata/web /srv/web
df -h /srv/web
lsblk /dev/sdc""", out=['  Logical volume "web" created.', """  LV  VG     Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  web vgdata -wi-a----- 12.00g""", '', '', '', """Filesystem             Size Used Avail Use% Mounted on
/dev/mapper/vgdata-web  12G  24K   12G   1% /srv/web""", """NAME         MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sdc           8:32  0   20G  0 disk
└─vgdata-web 253:0  0   12G  0 lvm  /srv/web"""], note='The same volume has three names: /dev/vgdata/web and /dev/mapper/vgdata-web are links to the device-mapper device /dev/dm-0, which has the major number 253. In the Attr column, w means writable, i means inherited allocation, a means active, and an o appears once the volume is open, for example mounted.')}
{talk('With plain partitions, every file system is stuck inside one fixed piece of one disk. L V M, the logical volume manager, adds a flexible layer. First you turn disks or partitions into physical volumes with p v create. L V M cuts each one into small extents of four mebibytes. Then you collect physical volumes into a volume group, a pool of extents, with v g create. Finally you cut logical volumes out of the pool with l v create, giving a name and a size. A logical volume behaves like a partition: you make a file system on it and mount it. The commands p v s, v g s and l v s list each layer. Try the animation to see a volume take blocks from a disk, and grow onto a second disk when the first one is full.')}
''', kw=['LVM', 'logical volume manager', 'physical volume', 'PV', 'volume group', 'VG', 'logical volume', 'LV', 'extent', 'PE size', 'pvcreate', 'vgcreate', 'lvcreate', 'pvs', 'vgs', 'lvs', '/dev/mapper', 'device-mapper'])

K.lesson('lvmgrow', 'Growing, moving and snapshotting volumes', f'''
{cmdtable([
    ('lvextend -r -L +5G LV', 'Grow by 5 GiB and grow the file system too (-r)', 'sudo lvextend -r -L +5G /dev/vgdata/web'),
    ('lvextend -r -l +100%FREE LV', 'Grow into all free space of the pool', 'sudo lvextend -r -l +100%FREE /dev/vgdata/web'),
    ('vgextend VG PV', 'Add a new disk to the pool', 'sudo vgextend vgdata /dev/sdd'),
    ('pvmove PV', 'Move all extents off a disk, online', 'sudo pvmove /dev/sdc'),
    ('vgreduce VG PV', 'Take an empty disk out of the pool', 'sudo vgreduce vgdata /dev/sdc'),
    ('lvcreate -s -L 2G -n NAME LV', 'A snapshot: a frozen view of a volume', 'sudo lvcreate -s -L 2G -n web-snap vgdata/web'),
    ('lvremove VG/LV', 'Delete a volume (unmount it first)', 'sudo lvremove vgdata/web-snap')])}
{sample('The pool is full, so add a disk and grow the mounted volume', """sudo lvextend -r -L +10G /dev/vgdata/web
sudo vgextend vgdata /dev/sdd
sudo lvextend -r -L +10G /dev/vgdata/web
sudo pvs""", out=['  Insufficient free space: 2560 extents needed, but only 2047 available', """  Physical volume "/dev/sdd" successfully created.
  Volume group "vgdata" successfully extended""", """  Size of logical volume vgdata/web changed from 12.00 GiB (3072 extents) to 22.00 GiB (5632 extents).
  Logical volume vgdata/web successfully resized.
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/mapper/vgdata-web is mounted on /srv/web; on-line resizing required
old_desc_blocks = 2, new_desc_blocks = 3
The filesystem on /dev/mapper/vgdata-web is now 5767168 (4k) blocks long.""", """  PV       VG     Fmt  Attr PSize   PFree
  /dev/sdc vgdata lvm2 a--  <20.00g    0
  /dev/sdd vgdata lvm2 a--  <10.00g 7.99g"""], note='This comes from the practice shell, whose messages follow lvm2 2.03 and e2fsprogs 1.47 on Ubuntu 24.04. vgextend runs pvcreate for a disk that is not a PV yet. The -r option calls resize2fs (through fsadm) after the volume has grown, and ext4 grows while mounted. Without -r you must run resize2fs, or xfs_growfs for xfs, yourself.')}
{steps('Replace an old disk without downtime', [
    'Add the new disk to the pool: <code>sudo vgextend vgdata /dev/sde</code>.',
    'Move every extent off the old disk while the volumes stay mounted: <code>sudo pvmove /dev/sdc</code>.',
    'Take the empty disk out of the pool: <code>sudo vgreduce vgdata /dev/sdc</code>.',
    'Remove its LVM label with <code>sudo pvremove /dev/sdc</code>, then take it out of the machine.'])}
{note('A snapshot made with lvcreate -s freezes a volume at one moment, so a backup can copy a consistent state while the original keeps changing. Only changed blocks use space in the snapshot, and a classic snapshot becomes invalid when that space (-L) fills up, so remove it after the backup. Thin pools (lvmthin) allow cheaper snapshots and overcommitted volumes.', 'tip')}
{talk('The big win of L V M is growing storage without downtime. When a volume is almost full and the pool still has free extents, one command does it all: l v extend dash r dash capital L plus five G grows the volume by five gibibytes, and dash r grows the file system on it too, while it stays mounted. When the pool itself is full, add a new disk with v g extend, and grow again. To replace an old disk, add the new one, move all data off the old one with p v move while everything keeps running, then remove the empty disk from the group. Snapshots freeze a volume at one moment, which lets a backup copy a consistent state. Remember one danger: a volume spread over two disks without RAID is lost if either disk dies.')}
''', kw=['lvextend', 'lvextend -r', '100%FREE', 'vgextend', 'pvmove', 'vgreduce', 'pvremove', 'LVM snapshot', 'lvcreate -s', 'thin pool', 'lvmthin', 'online resize', 'grow logical volume'])

K.lesson('raid', 'RAID: surviving a broken disk', f'''
<p><b>RAID</b> (redundant array of independent disks) combines several disks so the data survives when one fails, or so it is faster. On Linux, <code>mdadm</code> builds software RAID arrays such as /dev/md0, and the kernel reports their state in <code>/proc/mdstat</code>.</p>
{table(['Level', 'How it works', 'Usable space with n disks of size s', 'Disks that may fail'], [
    ['RAID 0', 'stripes data across the disks for speed', 'n × s', 'none: one failure loses everything'],
    ['RAID 1', 'mirrors: every disk holds the same data', 's', 'all but one'],
    ['RAID 5', 'stripes with one parity block per stripe (at least 3 disks)', '(n − 1) × s', 'one'],
    ['RAID 6', 'stripes with two parity blocks (at least 4 disks)', '(n − 2) × s', 'two'],
    ['RAID 10', 'stripes over mirrored pairs (at least 4 disks)', 'n × s ÷ 2', 'one in each pair']])}
{eq('RAID 5 usable = (n − 1) × s,   RAID 6 usable = (n − 2) × s')}
{sample('Build a mirror and read its state (typical output, the build container has no md driver)', """sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdc1 /dev/sdd1
cat /proc/mdstat""", out=["""mdadm: Note: this array has metadata at the start and
    may not be suitable as a boot device.  If you plan to
    store '/boot' on this device please ensure that
    your boot-loader understands md/v1.x metadata, or use
    --metadata=0.90
Continue creating array? y
mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md0 started.""", """Personalities : [raid1]
md0 : active raid1 sdd1[1] sdc1[0]
      10476544 blocks super 1.2 [2/2] [UU]
      [=====>...............]  resync = 28.5% (2987776/10476544) finish=1.2min speed=103027K/sec

unused devices: <none>"""], note='The mdadm messages up to the question were printed by mdadm 4.3 in the build container before it stopped for lack of the md kernel module. [2/2] [UU] means two of two disks are up. A degraded mirror shows [2/1] [U_], and a failed member is marked (F). The first resync copies one disk onto the other in the background, and the array can be used meanwhile.')}
{steps('Replace a failed disk in /dev/md0', [
    'Find the failed member in <code>cat /proc/mdstat</code> or <code>sudo mdadm --detail /dev/md0</code>.',
    'Mark it failed if the kernel has not, and remove it: <code>sudo mdadm /dev/md0 --fail /dev/sdd1 --remove /dev/sdd1</code>.',
    'Fit the new disk and copy the partition table from the good disk, for example <code>sudo sfdisk -d /dev/sdc | sudo sfdisk /dev/sdd</code>.',
    'Add the new partition: <code>sudo mdadm /dev/md0 --add /dev/sdd1</code>, and watch the rebuild in /proc/mdstat.',
    'Save the array in the config with <code>sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf</code> and run <code>sudo update-initramfs -u</code> once, after creating an array.'])}
{note('RAID is not a backup. A mirror copies a deleted file, a ransomware encryption or a broken update to every disk at once. RAID keeps a server running when a disk dies, and backups bring back data that is gone.', 'warn')}
{talk('Disks fail, and RAID keeps the data alive when one of them does. RAID zero only stripes data over disks for speed, so one broken disk loses everything. RAID one mirrors, every disk holds the same data, so you keep the space of one disk and can lose all but one. RAID five spreads one parity block over each stripe and survives one failed disk, and RAID six keeps two parity blocks and survives two. RAID ten mirrors pairs and stripes across them, fast and safe but using half the space. On Linux, m d a d m builds software arrays, and slash proc slash m d stat shows their state: U for a working disk, an underscore for a missing one. When a disk fails, remove it, add the new one, and the array rebuilds. But RAID is never a backup, because a deleted file is deleted on every disk.')}
''', kw=['RAID', 'RAID 0', 'RAID 1', 'RAID 5', 'RAID 6', 'RAID 10', 'mirror', 'parity', 'striping', 'mdadm', '/proc/mdstat', 'degraded array', 'rebuild', 'resync', 'mdadm.conf', 'RAID is not a backup'])

K.lesson('swap', 'Swap: room for memory pages on disk', f'''
<p>When RAM runs short, the kernel can move memory pages that have not been used for a while to <b>swap</b> space on disk, and bring them back when they are needed. Swap can be a partition or a file. It is far slower than RAM, so it is a safety net, not extra memory. Hibernation also writes RAM into swap.</p>
{cmdtable([
    ('swapon --show', 'Active swap areas', 'swapon --show'),
    ('fallocate -l 2G /swapfile', 'Make a 2 GiB file', 'sudo fallocate -l 2G /swapfile'),
    ('chmod 600 /swapfile', 'Only root may read swap, it holds memory contents', 'sudo chmod 600 /swapfile'),
    ('mkswap FILE or DEV', 'Write a swap signature', 'sudo mkswap /swapfile'),
    ('swapon FILE, swapoff FILE', 'Start and stop using it', 'sudo swapon /swapfile'),
    ('/swapfile none swap sw 0 0', 'The /etc/fstab line that turns it on at boot', 'echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab'),
    ('sysctl vm.swappiness=10', 'How eagerly the kernel swaps (0 to 200, default 60)', 'cat /proc/sys/vm/swappiness')])}
{run('Add a swap file, use it, remove it', """cd "$(mktemp -d)"
fallocate -l 256M swapfile
chmod 600 swapfile
mkswap swapfile
swapon swapfile
swapon --show
free -h | grep -E 'total|Swap'
swapoff swapfile
cat /proc/sys/vm/swappiness""", note='mkswap keeps the first 4 KiB page for its header, so 256 MiB of file gives 268431360 bytes of swap. The priority -2 was chosen by the kernel, because the swap area had none set. swapoff moves any swapped pages back into RAM before it lets go. A swappiness of 60 is the kernel default.', root=True)}
{note('Without chmod 600, mkswap warns about insecure permissions, because any user could read memory contents of other programs from the file. A file with holes (made by truncate) can be rejected by swapon, so use fallocate or dd.', 'warn')}
{talk('Swap is disk space the kernel uses when memory runs short. Pages of memory that have not been used for a while move out to swap, which frees RAM for programs that need it now. Swap is far slower than RAM, so a machine that swaps all the time is too small for its work, but a bit of swap keeps it from crashing when memory is tight. You can use a partition or a simple file. For a file, create it with f allocate, make it readable only by root with chmod six hundred, write the swap signature with m k swap, and switch it on with swap on. Swap on dash dash show lists the active areas, and free shows how much is used. Add a line to f s tab to keep it after a reboot. The setting swappiness, sixty by default, controls how eagerly the kernel swaps.')}
''', kw=['swap', 'swap file', 'swap partition', 'mkswap', 'swapon', 'swapoff', 'swapon --show', 'fallocate', 'swappiness', 'vm.swappiness', 'fstab swap line', 'hibernation', 'free -h swap'])

K.lesson('backup', 'Backups with tar and rsync', f'''
<p>A backup is a copy you can restore after a mistake, a broken disk, ransomware or a fire. The <b>3-2-1 rule</b>: keep 3 copies of the data, on 2 different kinds of storage, with 1 copy in another place. A backup you have never restored is only a hope, so test restores.</p>
{table(['Kind', 'What it copies', 'Restore needs'], [
    ['Full', 'everything, every time', 'the one full backup'],
    ['Incremental', 'what changed since the last backup of any kind', 'the full backup and every incremental after it, in order'],
    ['Differential', 'what changed since the last full backup', 'the full backup and the newest differential'],
    ['Snapshot (rsync --link-dest)', 'a complete folder tree each day, unchanged files are hard links', 'just copy the folder of that day back']])}
{run('A full and an incremental tar backup', """mkdir -p site/img
echo '<h1>Home</h1>' > site/index.html
echo 'body{}' > site/style.css
echo PNG > site/img/logo.png
tar --sort=name -czf full.tar.gz --listed-incremental=site.snar site
tar -tzf full.tar.gz
echo '<p>new</p>' > site/news.html
tar --sort=name -czf incr1.tar.gz --listed-incremental=site.snar site
tar -tzf incr1.tar.gz
mkdir restore
tar -xzf full.tar.gz -C restore --listed-incremental=/dev/null
tar -xzf incr1.tar.gz -C restore --listed-incremental=/dev/null
ls restore/site""", note='The snapshot file site.snar remembers what was saved. The second run stores only news.html, plus the folder entries tar needs to restore deletions. A restore unpacks the full archive and then each incremental one in order. --listed-incremental=/dev/null while extracting tells tar to apply the incremental information.')}
{run('rsync: mirror a folder, then keep daily snapshots', """mkdir -p site/img
echo '<h1>Home</h1>' > site/index.html
echo 'body{}' > site/style.css
echo PNG > site/img/logo.png
rsync -a site/ mirror/
rm site/style.css
rsync -a --delete --dry-run -v site/ mirror/ | grep -v bytes
rsync -a --delete site/ mirror/
ls mirror
mkdir snaps
rsync -a site/ snaps/day1/
echo new > site/img/banner.png
rsync -a --link-dest=../day1 site/ snaps/day2/
ls -i snaps/day1/index.html snaps/day2/index.html
du -sh snaps/day1 snaps/day2""", note='-a keeps permissions, owners, times and links. The trailing slash on site/ means the contents of site. --delete removes files from the copy that are gone from the source, so try it with --dry-run first. With --link-dest, unchanged files in day2 are hard links to day1, so the inode numbers are equal and day2 needs almost no extra space, yet each day is a complete tree. rsync creates only the last folder of the target path, which is why snaps is made first.')}
{cmdtable([
    ('rsync -a SRC/ user@host:DEST/', 'Copy to another machine over ssh', 'rsync -a --delete /srv/web/ backup@nas:/backups/web/'),
    ('restic -r REPO backup PATH', 'Encrypted, deduplicated snapshots to disk, sftp or S3', 'restic -r /mnt/usb/restic backup /home'),
    ('borg create REPO::NAME PATH', 'Deduplicated, compressed, optionally encrypted archives', 'borg create /mnt/usb/borg::{now} /home'),
    ('pg_dump, mysqldump', 'Consistent dumps of a running database, instead of copying its files', 'pg_dump shop > shop.sql')])}
{talk('Backups protect you from deleted files, broken disks, ransomware and even fire. Follow the three two one rule: three copies of your data, on two kinds of storage, and one copy somewhere else. A full backup copies everything. An incremental backup copies only what changed since the last backup, which saves space but needs every piece in order to restore. Tar with dash dash listed incremental makes both kinds, using a small snapshot file to remember what it saved. Rsync copies only the differences between two folders, locally or over s s h, and dash dash delete makes the copy an exact mirror, so test it with dash dash dry run first. With dash dash link dest, each day becomes a complete folder, but unchanged files are hard links that use no extra space. Tools such as restic and borg add encryption and deduplication. Most important of all, practise restoring, because an untested backup may not work when you need it.')}
''', kw=['backup', '3-2-1 rule', 'full backup', 'incremental backup', 'differential backup', 'tar --listed-incremental', 'snapshot file', 'restore test', 'rsync', 'rsync -a', 'rsync --delete', 'rsync --dry-run', 'rsync --link-dest', 'hard link snapshots', 'restic', 'borg', 'pg_dump'])

K.lesson('practice', 'Practice: grow storage with LVM and add swap', f'''
<p>The web server needs a volume that can grow, and more swap. The practice server has two empty disks, /dev/sdc (20 GB) and /dev/sdd (10 GB).</p>
{lab('LVM and swap on the practice server', [
    ('Make /dev/sdc an LVM physical volume.', 'sudo pvcreate /dev/sdc', [{'out': 'Physical volume "/dev/sdc" successfully created'}]),
    ('Create the volume group vgdata from /dev/sdc.', 'sudo vgcreate vgdata /dev/sdc', [{'out': 'Volume group "vgdata" successfully created'}]),
    ('Create a 15 GiB logical volume named web in vgdata.', 'sudo lvcreate -n web -L 15G vgdata', [{'out': 'Logical volume "web" created'}]),
    ('Make an ext4 file system with the label web on it.', 'sudo mkfs.ext4 -L web /dev/vgdata/web', [{'out': 'Creating filesystem with 3932160 4k blocks'}]),
    ('Create /srv/web and mount the volume there.', 'sudo mkdir /srv/web && sudo mount /dev/vgdata/web /srv/web', [{'exists': '/srv/web'}, {'code': 0}]),
    ('Add /dev/sdd to the volume group.', 'sudo vgextend vgdata /dev/sdd', [{'out': 'successfully extended'}]),
    ('Grow web by 8 GiB together with its file system.', 'sudo lvextend -r -L +8G /dev/vgdata/web', [{'out': 'is now 6029312 \\(4k\\) blocks long'}]),
    ('Show the size of /srv/web in readable units.', 'df -h /srv/web', [{'out': r'vgdata-web\s+23G'}]),
    ('Create a 1 GiB file /swapfile that only root can read and write.', 'sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile', [{'mode': ['/swapfile', '600']}]),
    ('Turn /swapfile into swap and switch it on.', 'sudo mkswap /swapfile && sudo swapon /swapfile', [{'cmd': r'swapon'}, {'code': 0}]),
    ('Check the swap total with free in readable units.', 'free -h', [{'out': r'Swap:\s+3\.0Gi'}])])}
{talk('Now build flexible storage yourself. Turn the twenty gigabyte disk into a physical volume, make a volume group called v g data from it, and cut a fifteen gibibyte logical volume called web. Format it with ext4, create the folder slash s r v slash web, and mount it. Then the web site grows, so add the second disk to the group with v g extend, and grow the volume by eight gibibytes with l v extend dash r, which grows the file system too. Df shows the new size. Finally, add a one gibibyte swap file: create it with f allocate, protect it with chmod six hundred, write the swap signature and switch it on. Free shows three gibibytes of swap, the two the server already had plus your new file.')}
''', kw=['LVM lab', 'lvextend practice', 'swap file practice', 'vgextend practice'])

K.lesson('levels', 'Storage safety from school to research', f'''
{ladder(
    '<p>Keep important files in more than one place, for example on a laptop and on a USB disk or a cloud drive, and check now and then that you can open the copies.</p>',
    '<p>Use LVM for volumes that will grow, RAID 1 or RAID 10 on servers that must survive a disk failure, a swap file sized to the workload, and automatic backups with rsync, restic or borg on a timer. Watch /proc/mdstat and SMART health, and test a restore every few months.</p>',
    '<p>Snapshots (LVM, btrfs, ZFS) give consistent backups of running systems. ZFS and btrfs join volume management, RAID and checksums in one file system, so they detect silent corruption. Cloud setups use replicated block storage, object storage with versioning and object lock against ransomware, and off-site copies in another region. Recovery time objective (RTO) and recovery point objective (RPO) set how fast and how recent a restore must be.</p>',
    '<p>Research on large disk fleets studies failure rates, latent sector errors and silent data corruption, and erasure codes such as Reed-Solomon, used in big storage systems, keep data safe with far less extra space than mirroring. Deduplication research shapes tools like borg and restic, which split data into content-defined chunks so a small change only stores a small new piece.</p>')}
{scene('the RAID that was mistaken for a backup', '<p>A small company kept its files on a RAID 1 server and saw no need for backups. Ransomware encrypted the shared folder, and the mirror copied every encrypted block to the second disk within seconds. Both disks were healthy and the data was gone. The new setup kept RAID 1 for uptime, added nightly restic snapshots to a disk that is only mounted during the backup, and a weekly copy to object storage with object lock, following the 3-2-1 rule. The first restore test found that the database needed pg_dump instead of a file copy.</p>')}
{talk('Here is how storage safety grows with experience. At school, keep important files in two places and check that the copies open. Professionals use L V M so volumes can grow, RAID so a server survives a broken disk, and automatic backups on a timer, and they test restores regularly. Larger systems use snapshots for consistent backups, file systems like Z F S and B T R F S that check every block for silent corruption, and off-site copies with object lock that ransomware cannot delete. They plan how fast and how recent a restore must be. Researchers study how disks fail across huge fleets, and use erasure codes and deduplication to keep data safe with less space.')}
''', kw=['3-2-1 backups', 'ZFS', 'btrfs', 'silent corruption', 'object lock', 'ransomware backup', 'RTO', 'RPO', 'erasure coding', 'Reed-Solomon', 'deduplication', 'restore testing'])

K.quiz('e', 'Which LVM layer is a pool made of one or more disks?', ['Physical volume', 'Volume group', 'Logical volume', 'Extent'], 1, 'The group.', 'A volume group.')
K.quiz('e', 'Which command lists logical volumes?', ['pvs', 'vgs', 'lvs', 'lsblk -l'], 2, 'LV.', 'lvs.')
K.quiz('e', 'Which RAID level only mirrors the data?', ['RAID 0', 'RAID 1', 'RAID 5', 'RAID 6'], 1, 'Two copies.', 'RAID 1.')
K.quiz('e', 'Which command switches on a swap file?', ['mount', 'swapon', 'mkswap', 'free'], 1, 'Swap on.', 'swapon, after mkswap.')
K.quiz('m', 'What does lvextend -r add to a plain lvextend?', ['It reboots', 'It also resizes the file system on the volume', 'It removes the old size', 'It makes a snapshot'], 1, 'Resize fs.', 'It calls resize2fs or xfs_growfs.')
K.quiz('m', 'The volume group is full. How do you get more space for a volume?', ['vgextend with a new disk, then lvextend', 'mkfs again', 'pvmove', 'lvremove'], 0, 'Grow the pool.', 'Add a PV to the VG.')
K.quiz('m', 'Why must a swap file have mode 600?', ['Speed', 'It holds memory contents that other users must not read', 'swapon requires 600', 'To save space'], 1, 'Secrets in RAM.', 'mkswap warns about insecure permissions.')
K.quiz('m', 'What does rsync --delete do?', ['Deletes the source', 'Removes files from the copy that no longer exist in the source', 'Deletes old backups', 'Deletes temporary files'], 1, 'Exact mirror.', 'Try it with --dry-run first.')
K.quiz('m', 'What does /proc/mdstat show with [2/1] [U_]?', ['A healthy mirror', 'A mirror with one of two disks missing', 'A RAID 0', 'A rebuild finished'], 1, 'One up.', 'The array is degraded.')
K.quiz('h', 'Why is RAID 1 not a backup?', ['It is too slow', 'Deletions and encryption are copied to every disk at once', 'It needs more disks', 'It cannot be restored'], 1, 'Mirror copies mistakes.', 'Backups keep older versions.')
K.quiz('h', 'An incremental tar backup chain is full, incr1, incr2. What do you need to restore the latest state?', ['incr2 only', 'full and incr2', 'full, incr1 and incr2 in order', 'full only'], 2, 'Every link.', 'Incrementals build on each other.')
K.quiz('h', 'How does rsync --link-dest save space?', ['It compresses files', 'Unchanged files become hard links to the previous snapshot', 'It skips folders', 'It deletes old days'], 1, 'Same inode.', 'Each day still looks complete.')
K.quiz('h', 'Two 10 GB disks are in one volume group without RAID, holding one big volume. One disk dies. What happens?', ['Nothing', 'Half the files survive for sure', 'The volume is lost and must be restored from backup', 'LVM rebuilds it'], 2, 'No redundancy.', 'LVM alone has no copies.')
K.quiz('x', 'Why should a database be backed up with pg_dump instead of copying its data folder while it runs?', ['pg_dump is faster', 'A file copy of a running database can catch files in an inconsistent state', 'The folder is hidden', 'rsync cannot read it'], 1, 'Consistency.', 'Or copy a snapshot taken with the database in a safe state.')

K.calc('e', 'An LVM extent is 4 MiB. How many extents does a 12 GiB volume need?', '3072', 'GiB to MiB, then divide.', ['12 GiB = 12288 MiB.', '12288 ÷ 4.', eq('3072 extents')], check=3072)
K.calc('e', 'RAID 1 with two 4 TB disks. How many TB can you use?', '4', 'A mirror.', ['Both disks hold the same data.', 'Usable is one disk.', eq('4 TB')], check=4)
K.calc('m', 'RAID 5 with 4 disks of 8 TB. How many TB are usable?', '24', 'One disk for parity.', ['(n − 1) × s.', '(4 − 1) × 8.', eq('24 TB')], check=24)
K.calc('m', 'RAID 6 with 6 disks of 4 TB. How many TB are usable?', '16', 'Two disks for parity.', ['(n − 2) × s.', '(6 − 2) × 4.', eq('16 TB')], check=16)
K.calc('h', 'A 20 GiB disk loses 1 MiB to LVM metadata and keeps only whole 4 MiB extents. How many extents does it give?', '5119', 'Subtract, divide, round down.', ['20 GiB = 20480 MiB.', '20480 − 1 = 20479 MiB.', eq('⌊20479 ÷ 4⌋ = 5119')], check=5119)
K.calc('h', 'mkswap keeps a 4096 byte header. How many bytes of swap does a 1 GiB (1073741824 byte) file give?', '1073737728', 'Subtract the header.', ['1073741824 − 4096.', 'The header holds the signature and UUID.', eq('1073737728 bytes')], check=1073737728)
K.calc('x', 'Daily rsync snapshots with --link-dest: 50 GB of data, 1 GB of files change each day. About how many GB do 30 days use?', '79', 'One full copy plus changes.', ['The first day stores 50 GB.', 'Each of the next 29 days stores about 1 GB of new files.', eq('50 + 29 × 1 = 79 GB')], check=79)

K.must('LVM layers', 'pvcreate makes PVs, vgcreate pools them into a VG, lvcreate cuts LVs. pvs, vgs, lvs list them. Extents are 4 MiB.')
K.must('Growing', 'lvextend -r -L +SIZE grows the volume and its file system online. vgextend adds a disk, pvmove empties one, snapshots freeze a moment.')
K.must('RAID', '0 stripes, 1 mirrors, 5 survives one failure with (n − 1) × s, 6 survives two with (n − 2) × s, 10 mirrors pairs. mdadm and /proc/mdstat. RAID is not a backup.')
K.must('Swap', 'fallocate, chmod 600, mkswap, swapon, a line in /etc/fstab. swapon --show and free -h. vm.swappiness sets how eagerly the kernel swaps.')
K.must('Backups', '3-2-1 rule. tar --listed-incremental for full and incremental archives, rsync -a --delete (with --dry-run first), --link-dest snapshots, restic or borg. Test restores.')

T = K.topic(
    slug='lvm-raid-backup', topic='lvm-raid-backup',
    step=(3, 'Storage', 'lx-admin-3', 'Partition and format disks, mount them by hand and at boot, keep them healthy and growing, and make storage flexible and safe with LVM, RAID, swap and backups.', 'Advanced'),
    title='LVM, RAID, swap and backups', short='LVM, RAID and backups', badge='3.2', minutes=60, added='2026-11-23',
    lead='Make storage flexible with LVM volumes that grow while mounted, survive a broken disk with RAID, give the kernel swap space, and keep data safe with tar and rsync backups that you have actually restored.',
    desc='LVM physical volumes, volume groups, logical volumes and extents, pvcreate, vgcreate, lvcreate, lvextend -r, vgextend, pvmove and snapshots, RAID levels 0, 1, 5, 6 and 10 with mdadm and /proc/mdstat, replacing a failed disk, swap files with fallocate, mkswap and swapon, swappiness, the 3-2-1 backup rule, tar full and incremental archives, rsync mirrors and --link-dest snapshots, restic and borg.',
    summary='LVM volumes, software RAID, swap files, and backups with tar and rsync.',
    keywords=['LVM', 'pvcreate', 'vgcreate', 'lvcreate', 'lvextend', 'RAID', 'mdadm', 'swap', 'mkswap', 'swapon', 'backup', 'tar', 'rsync'],
    recap='<p>LVM pools disks into volume groups and cuts logical volumes that grow online with lvextend -r. RAID keeps data available when disks fail, but only backups bring back deleted or encrypted data. Swap files give the kernel room for idle memory pages. Backups follow the 3-2-1 rule with tar, rsync, restic or borg, and restores are tested.</p>')
