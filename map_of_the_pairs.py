bookkeeping_blocks_length = {}
with open('SourcererCC50/tokenizers/block-level/blocks_tokens/files-tokens-0.tokens','r') as fin:
    for line in fin:
        x = line.split(',')
        x[1] = int(x[1])
        x[2] = int(x[2])
        bookkeeping_blocks_length[x[1]] = x[2]

bookkeeping_pairs_threshold = {}
bookkeeping_pairs_average_length = {}
for i in [75, 73 ,71, 70, 65, 60, 55, 50]:
    print('Commencing on the', i,'threshold')
    with open('SourcererCC'+ str(i) +'/results.pairs','r') as fin:
        for line in fin:
            x = line.split(',')
            if x[0] != x[2]:
                x[3] = int(x[3])
                x[3] = str(x[3])
                if (x[1] + ',' + x[3]) not in bookkeeping_pairs_threshold.keys():
                    bookkeeping_pairs_threshold[x[1] + ',' + x[3]] = i
                    bookkeeping_pairs_average_length[x[1] + ',' + x[3]] = (bookkeeping_blocks_length[int(x[1])] + bookkeeping_blocks_length[int(x[3])])/2
print('Done, writing to file')

different_projects_map = []
for i in bookkeeping_pairs_average_length.keys():
    different_projects_map.append([i,bookkeeping_pairs_threshold[i],bookkeeping_pairs_average_length[i]])

with open('map.txt','w') as fout:
    for i in different_projects_map:
        line = i[0] + ';' + str(i[1]) + ';' + str(i[2]) + '\n'
        fout.write(line)
