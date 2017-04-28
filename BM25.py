import metapy


def BM25mining():
	idx = metapy.index.make_inverted_index('config.toml')
	query = metapy.index.Document()
	ranker = metapy.index.OkapiBM25()
	#ranker = metapy.index.DirichletPrior(mu=vari)
	#best = 36
	#ranker = metapy.index.JelinekMercer(vari)
	#best = 0.52
	# ranker = metapy.index.AbsoluteDiscount(0.789)
	#best = 0.789	
	# ranker = metapy.index.PivotedLength(0.42)
	#best = 0.42

	# ranker = metapy.index.OkapiBM25(k1=1.65,b=0.7,k3=50)
	#defalut 1.2 0.75
	#ranker = PL2Ranker(vari)
	with open('scores.txt', 'w') as f:
		num_results = 10
		with open('queries.txt') as query_file:
		    for query_num, line in enumerate(query_file):
		        query.content(line.strip())
		        results = ranker.score(idx, query, num_results)
		        out = query.content() + ": "
		        print out
		        f.write(out + "\n")

		        count = 0
		        
		        results = sorted(results, key = lambda x:x[0])
		        # print results
		        outlist = []
		        while count<len(results):

		        	totalscore = 0
			        while (results[count][0]+1)%3 != 0:
			        	totalscore += results[count][1]
			        	count += 1
			        totalscore += results[count][1]
			        num = (results[count][0]+1) / 3
			        count += 1
		       		
		       		outlist.append((num,totalscore))
		       		outlist = sorted(outlist, key=lambda x:x[1], reverse=True)
		       	for item in outlist:
			       	print str(item[0]) + " " + str(item[1])
		    	   	f.write(str(item[0]) + " " + str(item[1]) + "\n")
	   	query_file.close()
	f.close()
