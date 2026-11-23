# System administration 3.1: disks, partitions and file systems. Block device names (sd, nvme, vd, mmcblk, loop),
# lsblk and blkid, MBR and GPT partition tables, parted and sfdisk, mkfs for ext4, xfs and vfat, blocks, inodes and
# reserved blocks, mount and umount, the mount tree, busy mounts, /etc/fstab fields and options, UUID and LABEL,
# findmnt --verify, mount -a, fsck and e2fsck, tune2fs, resize2fs, loop devices. Sources: lsblk(8), blkid(8),
# parted(8), sfdisk(8), mkfs.ext4(8) (mke2fs), mke2fs.conf(5), mkfs.xfs(8), mkfs.fat(8), ext4(5), mount(8),
# umount(8), findmnt(8), fstab(5), fsck(8), e2fsck(8), tune2fs(8), resize2fs(8), losetup(8), fuser(1),
# the UEFI specification for the GPT layout, and real runs on loop devices in the build container.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('devices', 'Disks, partitions and their names', f'''
<p>Linux shows every disk as a <b>block device</b>, a file in /dev that programs read and write in blocks. A disk is split into <b>partitions</b>, and each partition usually holds one <b>file system</b>, the structure that turns raw blocks into folders and files.</p>
{table(['Name', 'What it is', 'Partitions'], [
    ['<code>/dev/sda</code>, <code>/dev/sdb</code>', 'SATA, SAS and USB disks, in the order the kernel finds them', '<code>/dev/sda1</code>, <code>/dev/sda2</code>'],
    ['<code>/dev/nvme0n1</code>', 'NVMe drive 0, namespace 1', '<code>/dev/nvme0n1p1</code> (p before the number)'],
    ['<code>/dev/vda</code>, <code>/dev/xvda</code>', 'virtual disks in KVM and older Xen clouds', '<code>/dev/vda1</code>'],
    ['<code>/dev/mmcblk0</code>', 'SD cards and eMMC, as on a Raspberry Pi', '<code>/dev/mmcblk0p1</code>'],
    ['<code>/dev/loop0</code>', 'a loop device: a normal file used as if it were a disk', 'snap packages and disk images use them'],
    ['<code>/dev/mapper/NAME</code>', 'devices made by LVM or disk encryption (chapter 3.2)', '']])}
{cmdtable([
    ('lsblk', 'Tree of disks and partitions with size and mount point', 'lsblk'),
    ('lsblk -f', 'Add file system type, label, UUID and free space', 'lsblk -f'),
    ('sudo blkid', 'Type, LABEL and UUID of every file system', 'sudo blkid /dev/sdb1'),
    ('ls -l /dev/disk/by-uuid/', 'Links from stable names to the current device', 'ls -l /dev/disk/by-id/')])}
{sample('The disks of the practice server', """lsblk
lsblk -f
sudo blkid /dev/sdb1""", out=["""NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0  0   40G  0 disk
└─sda1   8:1  0   40G  0 part /
sdb     8:16  1 29.8G  0 disk
└─sdb1  8:17  1 29.8G  0 part
sdc     8:32  0   20G  0 disk
sdd     8:48  0   10G  0 disk""", """NAME   FSTYPE FSVER LABEL    UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
sda
└─sda1 ext4   1.0            b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71   22.7G    39% /
sdb
└─sdb1 vfat   FAT32 USBSTICK 4A1B-2C3D
sdc
sdd""", '/dev/sdb1: LABEL="USBSTICK" UUID="4A1B-2C3D" BLOCK_SIZE="512" TYPE="vfat" PARTUUID="a1b2c3d4-01"'], note='The practice server has a 40 GB system disk with one ext4 partition mounted on /, a USB stick (RM 1 means removable) with a FAT32 partition that is not mounted, and two new disks of 20 GB and 10 GB with no partitions at all. You will set up sdc in the practice lab and use sdd for LVM in chapter 3.2.')}
{run('A file used as a disk with a loop device', """cd "$(mktemp -d)"
truncate -s 1G disk.img
ls -lh disk.img
du -h disk.img
dev=$(losetup -f --show disk.img)
echo "$dev"
lsblk -o NAME,SIZE,TYPE "$dev"
losetup -d "$dev"
""", note='truncate makes a 1 GB sparse file that uses no space until something is written, which is why du reports 0. losetup -f picks the first free loop device and --show prints its name, which the script keeps in a variable. From then on that device behaves like a 1 GB disk, so you can practise partitioning and formatting without touching a real one. losetup -d detaches it again.', root=True)}
{note('Names like sda and sdb follow the order in which the kernel finds the disks, and that order can change when a disk is added or a USB stick is plugged in. Never rely on them in configuration. Use the UUID or LABEL of the file system, which blkid shows, or the links in /dev/disk/by-uuid and /dev/disk/by-id.', 'warn')}
{talk('Linux treats every disk as a block device, a special file in slash dev. SATA and USB disks are called s d a, s d b and so on. NVMe drives have longer names, such as n v m e zero n one, and their partitions add a p and a number. Virtual machines often show v d a, and SD cards show m m c b l k zero. A disk is divided into partitions, and each partition holds a file system, which organises the raw blocks into folders and files. Lsblk draws the tree of disks and partitions, and lsblk dash f adds the file system type, the label and the U U I D, a unique ID written when the file system was made. Device names can change when you add a disk, so configuration should always use the U U I D or the label instead. A loop device lets a normal file act like a disk, which is perfect for safe practice.')}
''', kw=['block device', '/dev/sda', 'nvme0n1', '/dev/vda', 'mmcblk0', 'partition', 'lsblk', 'lsblk -f', 'blkid', 'UUID', 'LABEL', '/dev/disk/by-uuid', 'loop device', 'losetup', 'truncate sparse file'])

K.lesson('partitions', 'Partition tables: MBR, GPT and parted', f'''
<p>The first sectors of a disk hold a <b>partition table</b>, a list that says where each partition starts and ends. There are two kinds.</p>
{table(['', 'MBR (msdos)', 'GPT'], [
    ['Age', '1983, IBM PC', 'part of the UEFI standard, around 2000'],
    ['Partitions', '4 primary, or 3 plus an extended one that holds logical partitions', '128 by default'],
    ['Largest disk', '2 TiB with 512 byte sectors (sector numbers are 32 bit)', 'far beyond any real disk (64 bit sector numbers)'],
    ['Safety', 'one copy at the start of the disk', 'a backup copy at the end of the disk, with checksums'],
    ['Boots with', 'BIOS', 'UEFI (needs an EFI System Partition), and BIOS through GRUB']])}
{cmdtable([
    ('parted -s DISK mklabel gpt', 'Write a new, empty GPT table (erases the old table)', 'sudo parted -s /dev/sdc mklabel gpt'),
    ('parted -s DISK mkpart NAME TYPE START END', 'Add a partition. START and END in MiB, GiB or percent', 'sudo parted -s /dev/sdc mkpart data ext4 1MiB 100%'),
    ('parted DISK print, unit MiB print', 'Show the table', 'sudo parted /dev/sdc unit MiB print'),
    ('parted DISK rm N', 'Delete partition N', 'sudo parted -s /dev/sdc rm 1'),
    ('sfdisk -l DISK, fdisk -l DISK', 'List the table in sectors', 'sudo sfdisk -l /dev/sda'),
    ('gdisk, cfdisk, fdisk', 'Menu driven editors for the same job', 'sudo cfdisk /dev/sdc')])}
{run('Partition a disk image with parted', """cd "$(mktemp -d)"
truncate -s 1G disk.img
parted -s disk.img mklabel gpt mkpart boot fat32 1MiB 257MiB set 1 esp on mkpart root ext4 257MiB 100% 2>/dev/null
parted -s disk.img unit MiB print
sfdisk -l disk.img | tail -3""", note='The first partition starts at 1 MiB, which keeps partitions aligned to the internal blocks of SSDs and leaves room for the table itself. The esp flag marks an EFI System Partition. The second partition stops at 1023 MiB, because GPT keeps its backup copy in the last sectors of the disk. sfdisk counts in 512 byte sectors: 2048 sectors are exactly 1 MiB. The type name in mkpart only sets a hint in the table and does not format anything. (2>/dev/null hides a harmless warning, because this container has no udev.)', root=True)}
{note('mklabel replaces the whole partition table, and the partitions on the disk are lost with it. Check the device name twice with lsblk before you run it, especially when a USB stick and a data disk have similar sizes.', 'warn')}
{talk('Before a disk can hold files, it needs a partition table, a small list at the start of the disk that says where each partition begins and ends. The old format is called M B R or msdos. It allows only four primary partitions and cannot use more than two tebibytes. The modern format is G P T. It allows one hundred and twenty eight partitions, works with huge disks, and keeps a backup copy at the end of the disk. U E F I computers boot from G P T disks. The tool parted creates the table with mklabel and adds partitions with mkpart, a name, a type hint, a start and an end. Starting the first partition at one mebibyte keeps it aligned for fast S S D access. Be very careful, because mklabel erases the old table. Always check the device name with lsblk first.')}
''', kw=['partition table', 'MBR', 'msdos label', 'GPT', 'GUID partition table', 'EFI System Partition', 'parted', 'mklabel', 'mkpart', 'sfdisk', 'fdisk', 'gdisk', 'cfdisk', 'partition alignment', '2 TiB limit'])

K.lesson('mkfs', 'Making a file system: ext4, xfs and vfat', f'''
<p>A new partition is just empty blocks. <code>mkfs</code> writes a file system onto it: a superblock with the settings, an inode table where each file gets one <b>inode</b> (its owner, mode, size and block list), the blocks for the data, and on ext4 and xfs a <b>journal</b> that keeps the file system consistent after a crash.</p>
{table(['File system', 'Use it for', 'Good to know'], [
    ['ext4', 'the default on Debian and Ubuntu, a safe choice for most disks', 'can grow and shrink (shrink only while unmounted). 5 percent of blocks are reserved for root by default'],
    ['xfs', 'the default on RHEL, Rocky and Fedora Server, large files and big parallel workloads', 'can grow while mounted, but can never shrink'],
    ['vfat (FAT32)', 'USB sticks and the EFI System Partition, readable by every system', 'no Linux owners or permissions, and no single file of 4 GiB or more'],
    ['exfat', 'large USB drives and SD cards shared with Windows and macOS', 'no 4 GiB file limit'],
    ['btrfs', 'snapshots, checksums and compression (default on Fedora Workstation and openSUSE)', 'more features, more to learn'],
    ['swap', 'not a file system: space for memory pages, made with mkswap (chapter 3.2)', '']])}
{cmdtable([
    ('mkfs.ext4 -L LABEL DEV', 'ext4 with a label', 'sudo mkfs.ext4 -L data /dev/sdc1'),
    ('mkfs.xfs -L LABEL DEV', 'xfs (labels up to 12 characters)', 'sudo mkfs.xfs -L logs /dev/sdc2'),
    ('mkfs.vfat -F 32 -n LABEL DEV', 'FAT32 for a USB stick or the EFI partition', 'sudo mkfs.vfat -F 32 -n USB /dev/sdb1'),
    ('tune2fs -l DEV', 'Read the settings of an ext file system', 'sudo tune2fs -l /dev/sdc1 | less'),
    ('tune2fs -L NAME, -m PERCENT', 'Change the label, change the reserved space', 'sudo tune2fs -m 1 /dev/sdc1')])}
{sample('mkfs.ext4 on the practice server’s new 20 GB partition', """sudo mkfs.ext4 -L data /dev/sdc1""", out="""mke2fs 1.47.0 (5-Feb-2023)
Creating filesystem with 5242368 4k blocks and 1310720 inodes
Filesystem UUID: 36cdba49-be45-4fa8-a8bb-106f1ceb90ef
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
	4096000

Allocating group tables: done
Writing inode tables: done
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information: done""", note='These numbers match a real run on a 20 GiB disk image partitioned from 1MiB to 100%. mke2fs makes one inode for every 16 KiB of space, so the number of inodes, and therefore the number of files, is fixed when the file system is made. Copies of the superblock are spread over the disk so e2fsck can repair the file system if the first copy is damaged.')}
{run('Three file systems on real images', """cd "$(mktemp -d)"
truncate -s 512M a.img b.img c.img
mkfs.ext4 -q -L data a.img
mkfs.xfs -q -L logs b.img
mkfs.vfat -F 32 -n USB c.img
blkid a.img b.img c.img
tune2fs -l a.img | grep -E '^(Filesystem volume name|Block count|Block size|Inode count|Reserved block count):'""", note='-q keeps mke2fs and mkfs.xfs quiet, and mkfs.fat only prints its version. blkid reads the type, label and new UUID straight from the images (LABEL_FATBOOT is the copy of the label kept in the FAT boot sector). tune2fs shows that 6553 of the 131072 blocks, 5 percent, are reserved for root, so root can still log in and clean up when users fill the disk. On a big data disk, tune2fs -m 1 gives most of that space back.', root=True)}
{talk('A partition holds nothing until you make a file system on it with mkfs. The file system writes a superblock with its settings, a table of inodes, where every file gets one inode that stores its owner, permissions, size and where its data is, and on modern file systems a journal that keeps everything consistent after a power cut. Ext4 is the default on Ubuntu and a safe choice. X F S is the default on Red Hat systems and is great for large files, but it can never be made smaller. V fat, also called FAT32, works on every computer, which is why USB sticks and the E F I boot partition use it, but it has no Linux permissions and cannot store a file of four gibibytes or more. Give each file system a label with dash capital L, so you can recognise it later. Ext4 reserves five percent of the space for root, which you can change with tune2fs.')}
''', kw=['mkfs', 'mkfs.ext4', 'mke2fs', 'mkfs.xfs', 'mkfs.vfat', 'FAT32', 'exfat', 'btrfs', 'ext4', 'xfs', 'superblock', 'inode', 'inode table', 'journal', 'reserved blocks', 'tune2fs', 'file system label'])

K.lesson('mount', 'Mounting: attaching a file system to the tree', f'''
<p>Linux has one tree of folders that starts at /. A file system becomes visible only when it is <b>mounted</b> on a folder, the <b>mount point</b>. From then on every path under that folder leads into the file system. Whatever the folder held before is hidden until the file system is unmounted.</p>
{play('lx-mount')}
{cmdtable([
    ('mount DEV DIR', 'Mount a file system (the type is detected)', 'sudo mount /dev/sdb1 /mnt/usb'),
    ('mount -o OPTIONS', 'Mount with options: ro, noexec, nosuid, nodev, noatime', 'sudo mount -o ro /dev/sdb1 /mnt/usb'),
    ('mount -o remount,rw /', 'Change the options of a mounted file system', 'sudo mount -o remount,ro /data'),
    ('umount DIR', 'Unmount (the command is umount, with no n)', 'sudo umount /mnt/usb'),
    ('findmnt, findmnt DIR', 'The mount tree, or one mount', 'findmnt /'),
    ('df -hT', 'Size, use and type of every mounted file system', 'df -hT /mnt/usb'),
    ('fuser -vm DIR, lsof DIR', 'Which processes keep a mount busy', 'sudo fuser -vm /mnt/usb')])}
{run('Mount, use and unmount a file system', """cd "$(mktemp -d)"
truncate -s 512M part.img
mkfs.ext4 -q -L data part.img
dev=$(losetup -f --show part.img)
echo "$dev"
mkdir mnt
mount "$dev" mnt
df -hT mnt
findmnt mnt
echo hello > mnt/a.txt
ls mnt
cd mnt && umount "$OLDPWD/mnt"
cd .. && umount mnt
ls mnt
losetup -d "$dev"
""", note='df shows 488M instead of 512M, because the inode tables and the journal take space. lost+found is made by mkfs, and e2fsck puts lost pieces of files there. The first umount fails with target is busy because the shell is still inside the folder. After cd .. it works, and the empty folder is back. The file a.txt is still inside part.img.', root=True)}
{note('Unmount a USB stick before you pull it out. Linux keeps writes in memory for a short while, and umount (or the eject button of a desktop) makes sure they reach the stick.', 'tip')}
{talk('Windows gives each disk a letter, such as D colon. Linux has a single tree that starts at the root, slash, and every other file system is attached to a folder somewhere in it. This is called mounting, and the folder is the mount point. Run sudo mount, the device and the folder, and from then on every path under that folder leads into the device. Anything the folder held before is hidden, not deleted, and comes back after you unmount. Df dash h T shows the size and type of each mounted file system, and findmnt shows the mount tree. To detach a file system, use umount, spelled without the letter n. It fails with target is busy while a program has a file open there or a shell is inside the folder. Fuser dash v m tells you who is using it. Try the animation to watch a folder change when a USB stick is mounted on it.')}
''', kw=['mount', 'mount point', 'umount', 'target is busy', 'findmnt', 'df -hT', 'mount options', 'ro', 'noexec', 'nosuid', 'nodev', 'noatime', 'remount', 'fuser', 'lsof', 'lost+found'])

K.lesson('fstab', 'Mounting at boot with /etc/fstab', f'''
<p>A mount made by hand is gone after a reboot. Lines in <code>/etc/fstab</code> tell the system what to mount at boot. systemd reads the file and makes a mount unit for each line.</p>
{shape('A line of /etc/fstab', """UUID=36cdba49-be45-4fa8-a8bb-106f1ceb90ef  /data  ext4  defaults,noatime  0  2
   (1) what to mount                       (2) where (3) type (4) options (5) dump (6) fsck order""", note='Fields are separated by spaces or tabs, and lines starting with # are comments.')}
{table(['Field', 'Meaning', 'Common values'], [
    ['1 fs_spec', 'the file system', '<code>UUID=...</code>, <code>LABEL=data</code>, <code>/dev/sdc1</code> (avoid), <code>server:/export</code> for NFS'],
    ['2 fs_file', 'the mount point', '<code>/data</code>, or <code>none</code> for swap'],
    ['3 fs_vfstype', 'the type', '<code>ext4</code>, <code>xfs</code>, <code>vfat</code>, <code>swap</code>, <code>nfs</code>, <code>auto</code>'],
    ['4 fs_mntops', 'options, separated by commas', '<code>defaults</code> (rw, suid, dev, exec, auto, nouser, async), <code>noatime</code>, <code>ro</code>, <code>nofail</code>, <code>noauto</code>, <code>x-systemd.automount</code>'],
    ['5 fs_freq', 'used by the old dump backup tool', 'almost always <code>0</code>'],
    ['6 fs_passno', 'order for fsck at boot', '<code>1</code> for /, <code>2</code> for other local file systems, <code>0</code> to skip']])}
{steps('Add a disk to /etc/fstab safely', [
    'Find the UUID with <code>sudo blkid /dev/sdc1</code> and create the mount point with <code>sudo mkdir /data</code>.',
    'Add the line with an editor, or append it with <code>echo "UUID=... /data ext4 defaults 0 2" | sudo tee -a /etc/fstab</code>.',
    'Check the file with <code>sudo findmnt --verify</code>.',
    'Run <code>sudo systemctl daemon-reload</code> so systemd reads the new file, then <code>sudo mount -a</code> to mount everything that is not mounted yet.',
    'Confirm with <code>findmnt /data</code>. Only reboot after these checks pass.'])}
{run('findmnt --verify finds mistakes before a reboot does', """cd "$(mktemp -d)"
truncate -s 64M p.img
mkfs.ext4 -q -U 11111111-2222-3333-4444-555555555555 p.img
dev=$(losetup -f --show p.img)
mkdir -p /srv/data /srv/logs
printf '%s\\n' 'UUID=11111111-2222-3333-4444-555555555555 /srv/data ext4 defaults 0 2' > good.tab
printf '%s\\n' 'UUID=11111111-2222-3333-4444-555555555556 /srv/data ext4 defaults 0 2' "$dev /srv/logs xfs defaults 0 2" > bad.tab
findmnt --verify --tab-file good.tab
findmnt --verify --tab-file bad.tab 2>&1
losetup -d "$dev"
rmdir /srv/data /srv/logs""", note='--tab-file checks a file other than /etc/fstab, which is handy for testing. One wrong character in the UUID is an error, because the system could not find the disk at boot. Writing xfs for an ext4 file system is a warning. Only the summary line goes to standard error, which is why it may print first here.', root=True)}
{note('A broken line in /etc/fstab can stop the boot and drop the machine into emergency mode (chapter 2.1). Add <code>nofail</code> for disks that may be missing, such as USB drives and network shares, and always test with findmnt --verify and mount -a before you reboot a server you cannot reach physically.', 'warn')}
{talk('Mounts you make by hand disappear at the next reboot. To mount a file system every time the machine starts, add a line to slash etc slash f s tab. Each line has six fields. The first says what to mount, and the best choice is U U I D equals and the U U I D from blkid, because device names can change. The second is the mount point, the third the type, such as ext4. The fourth holds options separated by commas, and defaults is a good start. Noatime saves writes, and nofail lets the boot go on if the disk is missing. The fifth field is almost always zero, and the sixth sets the order of the file system check at boot: one for the root file system, two for the others, zero to skip. After editing, check the file with findmnt dash dash verify, reload systemd, and run mount dash a. A typo here can stop the next boot, so never skip the check.')}
''', kw=['/etc/fstab', 'fstab fields', 'fs_spec', 'fs_passno', 'UUID in fstab', 'LABEL=', 'defaults', 'noatime', 'nofail', 'noauto', 'x-systemd.automount', 'findmnt --verify', 'mount -a', 'daemon-reload', 'emergency mode'])

K.lesson('check', 'Checking, repairing and growing file systems', f'''
{cmdtable([
    ('fsck DEV, e2fsck -f DEV', 'Check and repair, only while unmounted', 'sudo e2fsck -f /dev/sdc1'),
    ('e2fsck -n DEV', 'Check only, answer no to every repair', 'sudo e2fsck -fn /dev/sdc1'),
    ('xfs_repair DEV', 'Check and repair xfs (unmounted)', 'sudo xfs_repair /dev/sdc2'),
    ('resize2fs DEV [SIZE]', 'Grow ext4 to fill the partition, or shrink it (unmounted)', 'sudo resize2fs /dev/sdc1'),
    ('xfs_growfs DIR', 'Grow a mounted xfs', 'sudo xfs_growfs /data'),
    ('growpart DISK N', 'Grow partition N to the end of the disk (cloud-guest-utils)', 'sudo growpart /dev/vda 1'),
    ('smartctl -a DEV', 'Health data the disk reports about itself (smartmontools)', 'sudo smartctl -a /dev/sda')])}
{run('Check an ext4 image, then make it bigger', """cd "$(mktemp -d)"
truncate -s 512M part.img
mkfs.ext4 -q part.img
e2fsck -f -n part.img
truncate -s 1G part.img
resize2fs part.img
dumpe2fs -h part.img 2>/dev/null | grep '^Block count'""", note='e2fsck checks in five passes: inodes and blocks, folders, folder links, reference counts and the group summaries. The last line reports used and total files and blocks. Making the image file larger is like growing a virtual disk in the cloud. resize2fs then grows the file system into the new space, from 131072 to 262144 blocks.', root=True)}
{steps('Grow the root disk of a cloud server', [
    'Increase the volume size in the cloud console.',
    'Check that the kernel sees the larger disk with <code>lsblk</code>.',
    'Grow the partition with <code>sudo growpart /dev/vda 1</code>.',
    'Grow the file system: <code>sudo resize2fs /dev/vda1</code> for ext4 or <code>sudo xfs_growfs /</code> for xfs. Both work while mounted.',
    'Confirm the new size with <code>df -h /</code>.'])}
{note('Never run fsck on a mounted file system: repairs made under a running system can destroy data. e2fsck refuses, and the root file system is checked at boot instead, when fs_passno in /etc/fstab is 1.', 'warn')}
{talk('File systems can be checked and repaired with fsck, which calls the right tool for each type, such as e2fsck for ext4 or x f s repair for X F S. It must only run on a file system that is not mounted, because repairing files while programs use them can destroy data. Dash n checks without changing anything. The boot runs the check for you on file systems whose last field in f s tab is one or two. Disks fill up over time, and in the cloud you can simply make a disk larger. After that, grow the partition with growpart, and then grow the file system, with resize2fs for ext4 or x f s growfs for X F S. Both work while the system is running. Smartctl reads the health counters a disk keeps about itself, which can warn you before it fails.')}
''', kw=['fsck', 'e2fsck', 'e2fsck -n', 'xfs_repair', 'resize2fs', 'xfs_growfs', 'growpart', 'grow root disk', 'cloud disk resize', 'dumpe2fs', 'smartctl', 'SMART', 'file system check'])

K.lesson('practice', 'Practice: set up a new data disk in the practice shell', f'''
<p>The practice server has a new, empty 20 GB disk, /dev/sdc, and a USB stick. Partition and format the disk, mount it at /mnt/data, and make the mount survive a reboot.</p>
{lab('Bring a new disk into service', [
    ('List the disks with their file systems, labels and UUIDs.', 'lsblk -f', [{'out': 'USBSTICK'}]),
    ('Give /dev/sdc a GPT table and one partition named data that fills the disk.', 'sudo parted -s /dev/sdc mklabel gpt mkpart data ext4 1MiB 100%', [{'cmd': r'parted'}, {'code': 0}]),
    ('Show the partitions of /dev/sdc with lsblk.', 'lsblk /dev/sdc', [{'out': 'sdc1'}]),
    ('Make an ext4 file system with the label data on /dev/sdc1.', 'sudo mkfs.ext4 -L data /dev/sdc1', [{'out': 'Creating filesystem with 5242368 4k blocks'}]),
    ('Create the folder /mnt/data and mount /dev/sdc1 on it.', 'sudo mkdir /mnt/data && sudo mount /dev/sdc1 /mnt/data', [{'exists': '/mnt/data'}, {'code': 0}]),
    ('Show the size and free space of /mnt/data in readable units.', 'df -h /mnt/data', [{'out': r'/dev/sdc1\s+20G'}]),
    ('Add a line to /etc/fstab that mounts LABEL=data on /mnt/data as ext4 with defaults and fsck order 2.', 'echo "LABEL=data /mnt/data ext4 defaults 0 2" | sudo tee -a /etc/fstab', [{'has': ['/etc/fstab', 'LABEL=data /mnt/data ext4']}]),
    ('Check /etc/fstab for mistakes.', 'sudo findmnt --verify', [{'out': 'Success, no errors'}]),
    ('Unmount /mnt/data, then mount everything in /etc/fstab again.', 'sudo umount /mnt/data && sudo mount -a', [{'cmd': r'mount\s+-a'}, {'code': 0}]),
    ('Check that /mnt/data came back from /etc/fstab.', 'findmnt /mnt/data', [{'out': r'/dev/sdc1\s+ext4'}])])}
{talk('Time to do the job an admin does whenever a new disk arrives. First look at the disks with lsblk dash f, and find the empty one, s d c. Give it a G P T table and one partition that fills the disk, using parted. Check the new partition with lsblk, then make an ext4 file system on it with the label data. Create the mount point and mount it, and check the free space with df. To make the mount permanent, add a line to f s tab that uses the label, verify the file with findmnt, then unmount and run mount dash a, which mounts everything listed in f s tab. If findmnt shows the disk again, the next reboot will mount it too.')}
''', kw=['disk lab', 'new disk practice', 'parted practice', 'mkfs practice', 'fstab practice', 'mount -a practice'])

K.lesson('levels', 'Storage from school to research', f'''
{ladder(
    '<p>A disk is split into partitions, each with a file system, and Linux shows them all in one tree starting at /. lsblk shows the disks, df -h shows the free space, and a USB stick must be unmounted before you pull it out.</p>',
    '<p>Partition with GPT, use ext4 or xfs, mount by UUID in /etc/fstab with nofail for optional disks, and test with findmnt --verify. Watch free space and inodes, and grow cloud disks with growpart and resize2fs or xfs_growfs. Put data that grows, such as /var/lib/postgresql or /var/log, on its own file system so it cannot fill /.</p>',
    '<p>LVM and RAID make storage flexible and safe (chapter 3.2). Mount options such as noexec, nosuid and nodev harden /tmp and removable media. Network file systems (NFS, SMB) and systemd automount join storage from other machines. Cloud block storage (EBS, Persistent Disk), object storage (S3) and Kubernetes persistent volumes build on the same ideas.</p>',
    '<p>Research looks at how file systems survive crashes and how fast they run on new hardware: journaling and copy on write designs (ext4, xfs, btrfs, ZFS), log-structured file systems for flash (F2FS), and testing tools that crash file systems on purpose to find bugs. Studies of disk failures in large data centres, such as the drive statistics Backblaze publishes, show why every serious setup has redundancy and backups.</p>')}
{scene('the server that would not boot after a new disk', '<p>An admin added a data disk, wrote <code>/dev/sdb1 /data ext4 defaults 0 2</code> into /etc/fstab and rebooted. A USB stick was also plugged in, the kernel named the data disk sdc instead, and the boot stopped in emergency mode because /dev/sdb1 was the stick, with a vfat file system. The fix was a line with <code>UUID=</code> from blkid and the nofail option, a check with <code>findmnt --verify</code>, and a team rule to test every fstab change with <code>mount -a</code> before a reboot.</p>')}
{talk('Here is how storage work grows with experience. Beginners learn that disks hold partitions with file systems, all joined in one tree, and that lsblk and df show what is there. Professionals partition with G P T, mount by U U I D, add nofail for disks that may be missing, test every change to f s tab, and keep fast growing data on its own file system so the root disk never fills up. Larger systems use L V M and RAID for flexible and safe storage, harden mounts with options like noexec, and use network and cloud storage. Researchers study how file systems survive crashes and run on flash memory, and large studies of failing disks remind everyone that backups are never optional.')}
''', kw=['separate /var', 'mount hardening', 'noexec /tmp', 'NFS', 'SMB', 'automount', 'EBS', 'persistent volume', 'copy on write', 'ZFS', 'F2FS', 'disk failure statistics', 'fstab device name problem'])

K.quiz('e', 'Which command shows disks and partitions as a tree?', ['ls /dev', 'lsblk', 'df', 'mount'], 1, 'List block devices.', 'lsblk.')
K.quiz('e', 'What is the second partition of the first SATA disk called?', ['/dev/sda2', '/dev/sdb2', '/dev/hd2', '/dev/sda-2'], 0, 'Disk letter, then number.', '/dev/sda2.')
K.quiz('e', 'Which command makes a file system?', ['mkdir', 'mkfs', 'fdisk', 'mount'], 1, 'Make file system.', 'mkfs, for example mkfs.ext4.')
K.quiz('e', 'How is the command to unmount spelled?', ['unmount', 'umount', 'dismount', 'mount -u'], 1, 'No n.', 'umount.')
K.quiz('m', 'Why use UUID= instead of /dev/sdb1 in /etc/fstab?', ['It is shorter', 'Device names can change when disks are added, the UUID stays the same', 'UUIDs mount faster', 'fstab needs it'], 1, 'Stable name.', 'The UUID belongs to the file system.')
K.quiz('m', 'umount says target is busy. What is the usual cause?', ['The disk is broken', 'A process has a file open there or a shell is inside the folder', 'The file system is full', 'You forgot -f'], 1, 'Who uses it.', 'Find it with fuser -vm or lsof.')
K.quiz('m', 'A folder had files before a disk was mounted on it. What happens to them?', ['They are deleted', 'They are hidden until umount', 'They move to the disk', 'They move to lost+found'], 1, 'Covered.', 'They come back after umount.')
K.quiz('m', 'What does the sixth field of an fstab line set?', ['The dump backup', 'The order of the file system check at boot', 'The owner', 'The mount options'], 1, 'fs_passno.', '1 for /, 2 for others, 0 to skip.')
K.quiz('m', 'Which file system can grow but never shrink?', ['ext4', 'xfs', 'vfat', 'btrfs'], 1, 'Red Hat default.', 'xfs.')
K.quiz('h', 'What limits an MBR partition table to 2 TiB with 512 byte sectors?', ['The BIOS clock', 'Sector numbers are 32 bit', 'Only 4 partitions', 'The boot code size'], 1, '2 to the 32 sectors.', '2^32 × 512 bytes = 2 TiB.')
K.quiz('h', 'df shows free space but new files fail with No space left on device. What ran out?', ['RAM', 'Inodes, fixed when mkfs ran', 'The journal', 'Swap'], 1, 'One per file.', 'Check with df -i.')
K.quiz('h', 'Which option lets the boot continue when a disk in fstab is missing?', ['noauto', 'nofail', 'defaults', 'noatime'], 1, 'No failure.', 'nofail.')
K.quiz('h', 'Why must e2fsck not repair a mounted file system?', ['It is too slow', 'Changes under a running system can destroy data', 'It needs the network', 'It only reads xfs'], 1, 'Two writers.', 'Unmount first, or check at boot.')
K.quiz('x', 'Why should the first partition start at 1 MiB?', ['GPT needs exactly 1 MiB', 'It keeps partitions aligned to SSD and RAID blocks and leaves room for the table', 'It makes the disk faster to boot', 'parted refuses anything else'], 1, 'Alignment.', '2048 sectors of 512 bytes.')

K.calc('e', 'A disk sold as 1 TB holds 10¹² bytes. How many GiB (2³⁰ bytes) is that, rounded down?', '931', 'Divide by 1073741824.', ['10¹² ÷ 1073741824.', '= 931.3.', eq('931 GiB')], check=931)
K.calc('e', 'A partition starts at sector 2048 and a sector is 512 bytes. At which byte does it start?', '1048576', 'Multiply.', ['2048 × 512.', 'That is 1 MiB.', eq('1048576')], check=1048576)
K.calc('m', 'An MBR table stores sector numbers in 32 bits. With 512 byte sectors, how many TiB can it address?', '2', 'Two to the 32 times 512.', ['2³² = 4294967296 sectors.', '× 512 = 2199023255552 bytes.', eq('2199023255552 ÷ 2⁴⁰ = 2 TiB')], check=2)
K.calc('m', 'An ext4 file system has 131072 blocks and reserves 5 percent for root. How many blocks are reserved, rounded down?', '6553', 'Five percent.', ['131072 × 0.05.', '= 6553.6.', eq('6553 blocks')], check=6553)
K.calc('h', 'mke2fs makes one inode per 16384 bytes. How many inodes does a 20 GiB (21474836480 byte) file system get?', '1310720', 'Divide.', ['21474836480 ÷ 16384.', 'Every file needs one inode.', eq('1310720 inodes')], check=1310720)
K.calc('h', 'tune2fs shows 262144 blocks of 4096 bytes. How many MiB is the file system?', '1024', 'Blocks times size.', ['262144 × 4096 = 1073741824 bytes.', '÷ 1048576.', eq('1024 MiB')], check=1024)
K.calc('x', 'A GPT table has 128 entries of 128 bytes each. How many 512 byte sectors does the entry array use?', '32', 'Bytes, then sectors.', ['128 × 128 = 16384 bytes.', '16384 ÷ 512.', eq('32 sectors')], check=32)

K.must('Names', 'Disks are /dev/sda, /dev/nvme0n1, /dev/vda, with partitions sda1 or nvme0n1p1. lsblk -f and blkid show types, labels and UUIDs.')
K.must('Partitions', 'GPT for new disks (MBR stops at 2 TiB and 4 primaries). parted mklabel gpt, mkpart NAME TYPE 1MiB 100%, print. mklabel erases the table.')
K.must('File systems', 'mkfs.ext4 -L, mkfs.xfs, mkfs.vfat -F 32. Inodes are fixed at mkfs, ext4 reserves 5 percent for root, xfs cannot shrink.')
K.must('Mounting', 'mount DEV DIR hides what DIR held. umount fails while busy (fuser -vm). df -hT and findmnt show mounts.')
K.must('fstab', 'UUID or LABEL, mount point, type, options (defaults, noatime, nofail), 0, fsck order. findmnt --verify, daemon-reload and mount -a before any reboot.')

T = K.topic(
    slug='disks-filesystems', topic='disks-filesystems',
    step=(3, 'Storage', 'lx-admin-3', 'Partition and format disks, mount them by hand and at boot, keep them healthy and growing, and make storage flexible and safe with LVM, RAID, swap and backups.', 'Advanced'),
    title='Disks and file systems: partitions, mkfs, mount and fstab', short='Disks and file systems', badge='3.1', minutes=60, added='2026-11-23',
    lead='Turn an empty disk into usable storage: name disks and partitions, write a GPT table with parted, make ext4, xfs or vfat file systems, mount them, and make them come back after every reboot with /etc/fstab.',
    desc='Block device names, lsblk and blkid, loop devices, MBR and GPT, parted and sfdisk, mkfs.ext4, mkfs.xfs and mkfs.vfat, inodes, journals and reserved blocks, tune2fs, mount and umount, busy mounts, findmnt and df, /etc/fstab fields and options, findmnt --verify and mount -a, e2fsck, resize2fs, growpart and xfs_growfs.',
    summary='Disk names, partition tables, file systems, mounting, /etc/fstab, checking and growing.',
    keywords=['lsblk', 'blkid', 'parted', 'GPT', 'MBR', 'mkfs', 'ext4', 'xfs', 'mount', 'umount', 'fstab', 'fsck', 'resize2fs'],
    recap='<p>Disks appear as block devices, split into partitions by a GPT or MBR table. mkfs writes a file system with a fixed number of inodes, mount attaches it to a folder of the single tree, and /etc/fstab, checked with findmnt --verify, mounts it by UUID or LABEL at every boot. e2fsck checks unmounted file systems, and growpart with resize2fs or xfs_growfs grows them.</p>')
