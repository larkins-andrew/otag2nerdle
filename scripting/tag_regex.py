import re
import readline


def get_tags():
    tag_pattern = re.compile(r'<a href=".*">(?P<tag>.*)<')
    tags = []
    with open("tagger_tags.html") as f:
        in_header = False
        for l in f:
            # if len(tags) > 10:
            #     break
            if 'h2' in l:
                if 'functional' in l:
                    in_header = True
                    # print(l.strip())
                else:
                    in_header = False
            m = re.search(tag_pattern, l)
            if m and in_header:
                # print(l)
                tags.append(m.group(1))
    # print(tags)
    with open("func_tags.txt", "w") as f:
        for t in tags:
            f.write(t+"\n")
    return tags

if __name__ == "__main__":
    get_tags()