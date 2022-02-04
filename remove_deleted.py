def remove_deleted(fn):
    with open(fn, "rt") as fin:
        data = fin.read()

    data = data.replace(".py\n+++ /dev/nul", "")

    with open(fn, "wt") as fin:
        fin.write(data)


if __name__ == '__main__':
    remove_deleted("github_diff.txt")
