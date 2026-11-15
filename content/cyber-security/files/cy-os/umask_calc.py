# 2.1 Operating systems: users, permissions, processes and logs
# Example "umask_calc" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# New files start from 666 (rw for all) and new folders from 777, then the umask REMOVES bits
def apply_umask(start, umask):
    return start & ~umask          # keep only the bits that the umask does not block

for umask in [0o022, 0o027, 0o077]:
    file_mode = apply_umask(0o666, umask)
    dir_mode = apply_umask(0o777, umask)
    print("umask", format(umask, "03o"), "-> new file", format(file_mode, "03o"), " new folder", format(dir_mode, "03o"))
