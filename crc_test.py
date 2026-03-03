from crc import CRC
from os.path import join
from dataclasses import dataclass

@dataclass
class Entry:
    width   : int
    poly    : int
    init    : int
    refin   : bool
    refout  : bool
    xorout  : int
    check   : int
    residue : int # ignored
    name    : str

def main(path: str) -> None:
    entries = parse_catalogue(path)
    cnt = len(entries)
    for i in range(1, cnt + 1, 1):
        e = entries[i - 1]
        print(f"[({i}/{cnt}) {e.name}] ...")
        _ = CRC(
            e.width,
            e.poly,
            e.init,
            e.refin,
            e.refout,
            e.xorout,
            e.check
        )
        print(f"[({i}/{cnt}) {e.name}] Passed!")
        print()

def parse_catalogue(path: str) -> tuple[Entry, ...]:
    entries: list[Entry] = []
    with open(path, "r") as catalogue:
        while line := catalogue.readline(500):
            line = line.removesuffix("\n")
            line = line.split(" ")
            e = Entry(
                int(line[0].split("=")[1]),
                int(line[1].split("=")[1], 16),
                int(line[2].split("=")[1], 16),
                line[3].split("=")[1] == "true",
                line[4].split("=")[1] == "true",
                int(line[5].split("=")[1], 16),
                int(line[6].split("=")[1], 16),
                int(line[7].split("=")[1], 16),
                line[8].split("=")[1]
            )
            entries.append(e)
    return tuple(entries)

if __name__ == "__main__":
    path = join("third_party", "catalogue", "allcrcs.txt")
    main(path)
