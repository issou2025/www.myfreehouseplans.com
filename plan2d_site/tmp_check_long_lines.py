path = 'tmp_homepage.html'
long = []
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, start=1):
        if len(line) > 800:
            long.append((i, len(line), line[:200].strip()))
print('Long lines found:', len(long))
for ln, l, sample in long[:20]:
    print(f'Line {ln}: {l} chars; sample start: {sample}')
