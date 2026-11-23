# Power tools 3.2: archives and compression. tar create, list, extract, -C, --exclude, --strip-components,
# -z -j -J --zstd -a, tar over pipes and ssh, --listed-incremental, gzip gunzip zcat -k -c -d -l -t -r and levels,
# bzip2, xz -T0, zstd, zip and unzip. Sources: GNU tar manual (sections on blocking, compression and incremental
# dumps), tar(1), gzip(1) and the GNU gzip manual, bzip2(1), xz(1), zstd(1), zip(1) and unzip(1) from Info-ZIP,
# RFC 1951 (DEFLATE) and RFC 1952 (gzip format), CVE-2024-3094 (xz-utils 5.6.0 and 5.6.1).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable

K = Kit()

K.lesson('tar', 'tar: many files in, one archive out', f'''
<p>An <b>archive</b> is one file that holds many files and folders, with their names, permissions, owners and times. <code>tar</code> (short for tape archive, from Unix Version 7 in 1979) is the standard archiver on Linux. On its own it only glues files together, it does not make them smaller.</p>
{cmdtable([
    ('tar -cvf NAME.tar FILES', 'Create an archive (c create, v list names, f file name follows)', 'tar -cvf logs.tar logs'),
    ('tar -tvf NAME.tar', 'List what is inside without extracting (t table)', 'tar -tvf logs.tar'),
    ('tar -xvf NAME.tar', 'Extract everything into the current folder (x extract)', 'tar -xvf logs.tar'),
    ('tar -xvf NAME.tar -C DIR', 'Extract into another folder (it must exist)', 'tar -xvf logs.tar -C restore'),
    ('tar -xvf NAME.tar PATH', 'Extract only one member', 'tar -xvf logs.tar logs/app.log'),
    ('tar -rvf NAME.tar FILE', 'Append a file to an uncompressed archive', 'tar -rvf logs.tar notes.txt')])}
{run('Making, reading and unpacking a tar archive', """tar -cvf logs.tar --sort=name logs
ls -l logs.tar
tar -tf logs.tar
mkdir restore
tar -xvf logs.tar -C restore
ls -R restore
tar -tf logs.tar poem.txt""", note='--sort=name makes the order stable, without it tar uses the order the file system returns. The archive is 10240 bytes even though the two logs hold under 400 bytes, the next lesson explains why. Asking for a member that is not inside gives exit status 2.')}
{play('lx-tar')}
{note('The f option takes the next word as the archive name, so keep f last in a bundle: tar -cvf out.tar works, tar -cfv out.tar makes an archive called v. The dash is optional for the first bundle, so tar cvf is the same as tar -cvf.', 'warn')}
{talk('tar takes many files and folders and writes them into a single file called an archive, keeping each name, permission, owner and time. The three main modes are dash c to create, dash t to list the table of contents and dash x to extract. Dash v makes tar print each name as it works, and dash f tells tar which archive file to use. Keep the f last in the bundle of letters, because the word after it is taken as the file name. When you extract, tar writes into the current folder unless you give dash capital C with another folder. A good habit is to list an archive with dash t before extracting it, so you know whether it unpacks into a tidy folder or spills hundreds of files into your current one. The name tar comes from tape archive, because it was first used to write backups to magnetic tape, and its file format still reflects that history.')}
''', kw=['tar', 'tar -c', 'tar -x', 'tar -t', 'tar -v', 'tar -f', 'tar -C', 'archive', 'extract', 'tape archive'])

K.lesson('squeeze', 'Compression: gzip, bzip2, xz and zstd', f'''
<p>A compressor rewrites a file so repeated patterns take less space. It works on one stream of bytes, so to compress a folder you first tar it and then compress the tar. tar can call the compressor for you with one letter.</p>
{table(['Tool', 'Suffix', 'tar letter', 'Speed and size'], [
    ['gzip', '<code>.gz</code>, <code>.tgz</code>', '<code>-z</code>', 'fast, good, available everywhere (DEFLATE, RFC 1951)'],
    ['bzip2', '<code>.bz2</code>', '<code>-j</code>', 'slower, a bit smaller than gzip (Burrows-Wheeler blocks of 900 kB)'],
    ['xz', '<code>.xz</code>', '<code>-J</code>', 'slowest to pack, smallest, quick to unpack (LZMA2)'],
    ['zstd', '<code>.zst</code>', '<code>--zstd</code>', 'very fast at both ends, size close to xz at high levels']])}
{cmdtable([
    ('gzip FILE', 'Replace FILE with FILE.gz', 'gzip access.log'),
    ('gzip -k FILE', 'Keep the original too', 'gzip -k report.csv'),
    ('gunzip FILE.gz', 'Decompress (same as gzip -d)', 'gunzip access.log.gz'),
    ('zcat FILE.gz', 'Print the decompressed text, file untouched', 'zcat access.log.gz | grep ERROR'),
    ('gzip -l FILE.gz', 'Show compressed and original sizes', 'gzip -l backup.tar.gz'),
    ('gzip -t FILE.gz', 'Test that the file is not damaged', 'gzip -t backup.tar.gz'),
    ('gzip -9 FILE', 'Best compression (-1 fastest, -6 default)', 'gzip -9 big.sql'),
    ('xz -T0 FILE', 'xz using every CPU core', 'xz -T0 -k dump.sql'),
    ('tar -czf NAME.tar.gz DIR', 'Create a gzip compressed tarball', 'tar -czf site.tar.gz site'),
    ('tar -xf NAME.tar.xz', 'Extract any of them: GNU tar detects the compression itself', 'tar -xf linux-6.8.tar.xz')])}
{run('Compressing the same file four ways', """seq 1 20000 > numbers.txt
gzip -k numbers.txt
bzip2 -k numbers.txt
xz -k numbers.txt
ls -l numbers.txt*
gzip -l numbers.txt.gz
zcat numbers.txt.gz | tail -n 2
gzip -t numbers.txt.gz && echo "gzip file is fine"
gzip numbers.txt""", note='seq makes 20000 numbered lines, 108894 bytes of very repetitive text. Each tool keeps its own copy with -k. The last line fails because numbers.txt.gz already exists, gzip never overwrites without -f.')}
{run('Compressed tarballs', """tar -czf home.tar.gz --sort=name scripts notes.txt
tar -tzvf home.tar.gz
tar -cJf home.tar.xz --sort=name scripts notes.txt
file home.tar.gz home.tar.xz
tar -czf nologs.tar.gz --exclude='*.log' --sort=name logs scripts
tar -tf nologs.tar.gz""", note='--exclude skips matching names. The logs folder is still stored, just without the .log files inside it.')}
{note('Text, logs and databases compress very well, often to a fifth of their size or less. Photos (JPEG), videos and zip files are already compressed and hardly shrink, so do not waste CPU on them.', 'tip')}
{talk('Compression finds patterns that repeat and stores them only once. The classic tool on Linux is gzip, from nineteen ninety two, which uses the DEFLATE method, the same one inside zip files and PNG images. bzip2 usually gives smaller files but is slower. xz is slower still when packing but gives the smallest files and unpacks quickly, which is why the Linux kernel source is published as tar dot xz. zstd, made at Facebook in twenty sixteen, is very fast in both directions and is now used by many distributions for their packages. Each of these tools works on a single stream of bytes, so to compress a folder you combine them with tar. tar can call the compressor for you: dash z for gzip, dash j for bzip2 and capital J for xz. When extracting, GNU tar looks at the file and picks the right tool on its own, so tar dash x f works for all of them. By default gzip replaces the original file, so add dash k to keep it.')}
''', kw=['gzip', 'gunzip', 'zcat', 'bzip2', 'xz', 'zstd', 'tar -z', 'tar -J', 'tar -j', 'tar.gz', 'tgz', 'compression level', 'DEFLATE', 'LZMA'])

K.lesson('zip', 'zip and unzip: the format everyone can open', f'''
<p>A zip file is an archive and a compressor in one. Each file inside is compressed on its own, and a table at the end of the file lists every member, so one file can be extracted without reading the rest. Windows and macOS open zip files with no extra software, which makes zip the right choice when you send files to people who do not use Linux.</p>
{cmdtable([
    ('zip NAME.zip FILES', 'Make or update a zip with files', 'zip notes.zip notes.txt poem.txt'),
    ('zip -r NAME.zip DIR', 'Include folders and everything inside (-r recursive)', 'zip -r site.zip site'),
    ('unzip -l NAME.zip', 'List the contents', 'unzip -l site.zip'),
    ('unzip NAME.zip', 'Extract into the current folder', 'unzip site.zip'),
    ('unzip NAME.zip -d DIR', 'Extract into DIR (created if needed)', 'unzip site.zip -d /tmp/site'),
    ('unzip -o NAME.zip', 'Overwrite existing files without asking', 'unzip -o site.zip'),
    ('zip -e NAME.zip FILES', 'Ask for a password (weak ZipCrypto, do not trust it for secrets)', 'zip -e tax.zip tax.pdf')])}
{run('Working with zip files', """zip notes.zip notes.txt poem.txt
zip -r notes.zip scripts
unzip -l notes.zip
unzip notes.zip -d copy
ls -R copy""", note='zip adds new members to an existing zip file. Small files are stored without compression because deflating them would not save space.')}
{note('unzip asks before replacing an existing file. In a script, use -o to overwrite or -n to never overwrite, so it does not stop and wait for an answer.', 'warn')}
{talk('Zip is both an archive and a compressor in one format. It was created by Phil Katz in nineteen eighty nine, and today every operating system opens zip files without extra software. That makes zip the polite choice when you send files to Windows or Mac users. Inside a zip file each member is compressed on its own, and a central directory at the end of the file lists all of them, so a program can pull out a single file quickly. tar dot gz compresses everything as one stream, which usually gives a smaller result but means reading from the start to reach the last file. Use zip dash r to include folders, unzip dash l to look inside and unzip dash d to choose where the files go. The password option of zip uses an old method that can be broken easily, so do not rely on it for real secrets.')}
''', kw=['zip', 'unzip', 'zip -r', 'unzip -l', 'unzip -d', 'unzip -o', 'central directory', 'zip vs tar'])

K.lesson('backup', 'Real backups: pipes, ssh, increments and safety', f'''
<p>Because tar can read and write standard input and output with <code>-f -</code>, it fits into pipelines. That is how administrators copy whole folder trees between machines, or stream a backup without a temporary file.</p>
{cmdtable([
    ('tar -czf - DIR | ssh HOST "cat > DIR.tgz"', 'Stream a backup to another machine', "tar -czf - site | ssh backup@vault 'cat > site.tgz'"),
    ('ssh HOST "tar -czf - DIR" | tar -xzf -', 'Pull a folder from a server and unpack it here', "ssh web1 'tar -czf - /etc/nginx' | tar -xzf -"),
    ('tar -cf - DIR | tar -xf - -C DEST', 'Copy a tree and keep every permission and time', 'tar -cf - project | tar -xf - -C /mnt/usb'),
    ('tar -xf NAME.tar --strip-components=1', 'Drop the top folder of each member when extracting', 'tar -xf app-2.1.tar.gz --strip-components=1'),
    ('tar -g snap.file -czf FULL.tgz DIR', 'Incremental: the next run with the same snap file stores only changes', 'tar -g home.snar -czf mon.tgz /home'),
    ('sha256sum NAME.tar.gz', 'Fingerprint the archive to check it later', 'sha256sum backup.tar.gz > backup.sha256')])}
{run('Streaming and checking archives', """tar -czf - --sort=name logs | tar -tzf -
mkdir mirror
tar -cf - scripts | tar -xf - -C mirror
ls -l mirror/scripts
tar -czf app.tar.gz --sort=name logs
mkdir flat
tar -xzf app.tar.gz -C flat --strip-components=1
ls flat
sha256sum app.tar.gz > app.sha256
sha256sum -c app.sha256""", note='The first tar writes a compressed stream to its standard output and the second reads it from standard input. --strip-components=1 removed the logs/ prefix, so the files landed straight inside flat.')}
{steps('A backup you can trust', [
    'Archive with paths relative to a known folder, for example tar -czf home.tgz -C / home, so restores land where you expect.',
    'Run tar -tzf on the result (or gzip -t) to prove the file is readable.',
    'Store a sha256sum next to it and check it after every copy.',
    'Keep at least one copy on another machine or disk. A backup on the same disk dies with it.',
    'Practise a restore into an empty folder. A backup that was never restored is only a hope.'])}
{lab('Pack and unpack', [
    ('Create a tar archive <code>logs.tar</code> of the <code>logs</code> folder.', 'tar -cvf logs.tar logs', [{'cmd': r'^tar\s'}, {'exists': 'logs.tar', 'type': 'f'}]),
    ('List what is inside <code>logs.tar</code> without extracting it.', 'tar -tvf logs.tar', [{'cmd': r'-\w*t'}, {'out': 'logs/app\\.log'}]),
    ('Create a gzip compressed tarball <code>home.tar.gz</code> of <code>scripts</code> and <code>notes.txt</code>.', 'tar -czvf home.tar.gz scripts notes.txt', [{'cmd': r'-\w*z'}, {'exists': 'home.tar.gz', 'type': 'f'}]),
    ('Extract <code>home.tar.gz</code> into the <code>projects</code> folder using -C.', 'tar -xzvf home.tar.gz -C projects', [{'cmd': r'-C\s+projects'}, {'exists': 'projects/scripts/hello.sh', 'type': 'f'}]),
    ('Compress <code>poem.txt</code> with gzip but keep the original file.', 'gzip -k poem.txt', [{'exists': 'poem.txt.gz', 'type': 'f'}, {'exists': 'poem.txt', 'type': 'f'}]),
    ('Read the compressed poem without unpacking it to a file.', 'zcat poem.txt.gz', [{'cmd': r'zcat|gzip\s+-\w*c|gunzip\s+-\w*c'}, {'out': 'Twinkle'}]),
    ('Make <code>photos.zip</code> with the whole <code>photos</code> folder inside.', 'zip -r photos.zip photos', [{'cmd': r'zip\s+-r'}, {'exists': 'photos.zip', 'type': 'f'}])])}
{talk('Real backups use a few extra tricks. Writing dash f dash, a single dash as the file name, makes tar write to standard output or read from standard input, so you can pipe an archive straight into ssh and store it on another machine without a temporary file. The same trick copies a folder tree with every permission and time kept, by piping one tar into another. Dash dash strip components drops the top folder of each path while extracting, which is handy for downloads that unpack into a folder named after the version. GNU tar can also make incremental backups with dash g and a snapshot file, so each new run stores only what changed since the last one. Whatever you do, check your archives. List them with dash t, keep a sha two five six checksum beside them, keep a copy on another disk, and practise restoring, because a backup that was never restored is only a hope.')}
''', kw=['tar -f -', 'tar ssh', 'backup', 'strip-components', 'incremental backup', 'listed-incremental', 'snapshot', 'sha256sum', 'restore test', '3-2-1'])

K.lesson('levels', 'Archives and compression from school to research', f'''
{ladder(
    '<p>tar puts many files into one. gzip, xz and zip make files smaller by storing repeated parts only once. Always look inside an archive before unpacking it.</p>',
    '<p>A tar file is a sequence of 512 byte blocks: a header block per member (name, mode, owner, size, time, checksum) followed by its data padded to whole blocks, then two zero blocks. GNU tar writes in records of 20 blocks, 10240 bytes. DEFLATE combines LZ77 back references (a 32 KiB window) with Huffman codes. xz uses LZMA2 with windows of many megabytes, which is why it compresses better and needs more memory.</p>',
    '<p>The POSIX pax format (ustar plus extended headers) removes the old 100 character name and 8 GiB size limits, and GNU tar can write it with --format=pax. Compressed tarballs are not seekable, so extracting the last member reads the whole stream, while zip seeks through its central directory. zstd adds long range matching and trained dictionaries that compress many tiny similar files (such as JSON records) far better than any general method. Reproducible builds need stable archives: --sort=name, --mtime and --owner=0 --group=0 --numeric-owner give byte identical tarballs.</p>',
    '<p>Compression research balances ratio, speed and memory. Asymmetric numeral systems (ANS, Jarek Duda, 2009) give entropy coding as tight as arithmetic coding at the speed of Huffman, and power zstd and Apple LZFSE. Neural compressors using learned probability models now beat classic tools on text and images but are far too slow for daily use. Supply chain security joined the field in 2024 when CVE-2024-3094 showed a backdoor hidden in the build scripts of xz-utils 5.6.0 and 5.6.1, caught by Andres Freund through a half second slowdown in ssh logins.</p>')}
{scene('the 4 a.m. restore', '<p>A developer deletes a customer table by mistake. The nightly job has run <code>pg_dump shop | zstd -T0 &gt; /backup/shop-2026-11-22.sql.zst</code> and copied it to another region, with a sha256 file beside it. The on-call engineer checks the checksum, runs <code>zstd -dc shop-2026-11-22.sql.zst | psql shop_restore</code> into a fresh database, copies the missing rows back, and the shop is fixed before customers wake up.</p>')}
{talk('Inside, a tar file is simple. Each member gets a five hundred and twelve byte header block holding its name, size, permissions, owner and time, followed by its data rounded up to whole blocks, and two empty blocks mark the end. GNU tar writes whole records of ten thousand two hundred and forty bytes, which is why a tiny archive is still ten kilobytes before compression. gzip uses DEFLATE, which replaces repeated text with short references back to an earlier copy, then codes the result with Huffman codes, giving short codes to common symbols. xz looks much further back, many megabytes, so it finds more repeats and makes smaller files. Modern tools such as zstd use a newer coding method called asymmetric numeral systems, which is both tight and fast. Compression even became a security story in twenty twenty four, when an engineer at Microsoft noticed ssh logins were half a second slower and uncovered a backdoor hidden in the xz library. That event changed how open source projects review their build scripts.')}
''', kw=['tar format', '512 byte block', 'record size', 'ustar', 'pax', 'LZ77', 'Huffman', 'LZMA2', 'ANS', 'reproducible builds', 'CVE-2024-3094', 'xz backdoor'])

K.quiz('e', 'Which command creates an archive called site.tar from the folder site?', ['tar -xvf site.tar site', 'tar -cvf site.tar site', 'tar -tvf site site.tar', 'gzip site'], 1, 'c for create.', 'c creates, v lists names, f names the archive.')
K.quiz('e', 'How do you look inside backup.tar.gz without extracting it?', ['tar -xzf backup.tar.gz', 'tar -tzf backup.tar.gz', 'cat backup.tar.gz', 'gunzip backup.tar.gz'], 1, 't for table.', 'tar -t lists the members.')
K.quiz('e', 'What happens to notes.txt after gzip notes.txt?', ['Nothing, a copy is made', 'It is replaced by notes.txt.gz', 'It is deleted with no copy', 'It is renamed to notes.zip'], 1, 'gzip replaces by default.', 'Use -k to keep the original.')
K.quiz('e', 'Which format opens on Windows without extra software?', ['.tar.xz', '.zip', '.bz2', '.zst'], 1, 'The common one.', 'Windows and macOS open zip files natively.')
K.quiz('m', 'Which tar letter selects xz compression?', ['-z', '-j', '-J', '-x'], 2, 'Capital letter.', '-z gzip, -j bzip2, -J xz.')
K.quiz('m', 'Where does tar -xf app.tar -C /opt put the files?', ['In the current folder', 'Inside /opt', 'In /tmp', 'It fails'], 1, 'C changes folder.', '-C makes tar work inside that folder.')
K.quiz('m', 'Why does tar -cfv out.tar notes.txt go wrong?', ['v is not an option', 'f takes the next word as the name, so the archive is called v', 'tar needs -z', 'notes.txt is too small'], 1, 'f takes a value.', 'Keep f last in the bundle.')
K.quiz('m', 'Which reads a compressed log without creating any new file?', ['gunzip app.log.gz', 'zcat app.log.gz', 'gzip -k app.log.gz', 'tar -xf app.log.gz'], 1, 'cat for gz.', 'zcat prints the decompressed data to standard output.')
K.quiz('m', 'Why do JPEG photos hardly shrink in a tar.gz?', ['tar skips images', 'They are already compressed', 'gzip only reads text', 'They are too big'], 1, 'Little repetition left.', 'Compressed data has almost no patterns left to remove.')
K.quiz('h', 'What does tar -cf - project | tar -xf - -C /backup do?', ['Deletes project', 'Copies the tree to /backup keeping modes and times', 'Makes a file called -', 'Compresses project'], 1, 'Dash means a stream.', '-f - writes to stdout and reads from stdin.')
K.quiz('h', 'What does --strip-components=1 do when extracting app-2.1/bin/run?', ['Skips the file', 'Writes it as bin/run', 'Writes it as run', 'Strips the permission bits'], 1, 'Drop one leading folder.', 'One path element is removed from the front.')
K.quiz('h', 'A tar holds one 100 byte file. Why is it 10240 bytes?', ['tar adds a picture', 'Blocks of 512 bytes are written in records of 20 blocks', 'The file is copied 100 times', 'It is compressed backwards'], 1, 'Blocking.', 'GNU tar pads the archive to a whole 10240 byte record.')
K.quiz('x', 'Why can zip extract its last member faster than tar.gz can?', ['zip files are smaller', 'zip has a central directory and compresses each member on its own', 'tar.gz has no names', 'zip uses xz'], 1, 'Seeking.', 'A gzip stream must be read from the start, zip jumps to the member.')

K.calc('e', 'A 400 MB log compresses to 40 MB. What percent of the space is saved?', '90', 'Saved over original.', ['Saved: 400 − 40 = 360 MB.', '360 ÷ 400 = 0.9.', eq('90%')], check=90)
K.calc('e', 'How many 512 byte data blocks does tar use for a 1300 byte file?', '3', 'Round up.', ['1300 ÷ 512 ≈ 2.54.', 'Partial blocks are padded to a whole block.', eq('3 blocks')], check=3)
K.calc('m', 'Total blocks for one 1300 byte file in a tar, counting its header and the two end blocks?', '6', 'Header plus data plus end.', ['Header: 1 block.', 'Data: 3 blocks.', 'End marker: 2 blocks.', eq('1 + 3 + 2 = 6 blocks')], check=6)
K.calc('m', 'An archive needs 25 blocks of 512 bytes. GNU tar writes 10240 byte records. How many bytes is the file?', '20480', 'Records of 20 blocks.', ['25 blocks need 2 records of 20 blocks.', 'Each record is 10240 bytes.', eq('2 × 10240 = 20480 bytes')], check=20480)
K.calc('m', 'gzip -l shows compressed 2500 and uncompressed 10000. What is the ratio column (percent saved)?', '75', 'One minus the fraction.', ['2500 ÷ 10000 = 0.25.', '1 − 0.25 = 0.75.', eq('75.0%')], check=75)
K.calc('h', 'xz takes 120 s on one core. With xz -T0 on 8 cores and perfect scaling, how many seconds?', '15', 'Divide by cores.', ['Cores: 8.', '120 ÷ 8 = 15.', eq('15 seconds (real runs scale a little worse)')], check=15)

K.must('tar', 'tar -cvf make, -tvf list, -xvf extract, -C DIR to choose the folder. Keep f last, the next word is the archive name.')
K.must('Compress', 'tar -z gzip, -j bzip2, -J xz, --zstd. GNU tar detects the method when extracting. gzip replaces the file, -k keeps it.')
K.must('Read packed files', 'zcat, xzcat and bzcat print without unpacking. gzip -l shows sizes, gzip -t tests the file.')
K.must('zip', 'zip -r out.zip dir, unzip -l to look, unzip -d DIR to place, -o to overwrite. Best for sharing with Windows and Mac users.')
K.must('Backups', 'Stream with -f - over ssh, strip a top folder with --strip-components, check with tar -t and sha256sum, test a restore.')

T = K.topic(
    slug='archives', topic='archives',
    step=(3, 'Finding and packing files', 'lx-power-3', 'Search the file tree with find and xargs, and bundle and compress files with tar, gzip, xz and zip.', 'Intermediate'),
    title='Archives and compression: tar, gzip, xz and zip', short='tar, gzip and zip', badge='3.2', minutes=45, added='2026-11-23',
    lead='Bundle files and folders with tar, shrink them with gzip, bzip2, xz and zstd, share them as zip files, and build backups that stream over ssh and can be trusted.',
    desc='tar create, list and extract with -C, --exclude and --strip-components, compressed tarballs with -z -j -J and --zstd, gzip gunzip zcat with -k -l -t and levels, bzip2, xz -T0, zip and unzip, tar over pipes and ssh, incremental backups, checksums, and how the tar format and DEFLATE work.',
    summary='tar -c -t -x, gzip and xz, zip and unzip, streaming backups and checking them.',
    keywords=['tar', 'gzip', 'gunzip', 'zcat', 'xz', 'bzip2', 'zstd', 'zip', 'unzip', 'tar.gz', 'archive', 'compress', 'backup'],
    recap='<p>tar bundles, compressors shrink one stream, so a folder becomes a .tar.gz or .tar.xz. zip does both per file and opens everywhere. Stream archives with -f -, and check every backup by listing it and restoring it.</p>')
