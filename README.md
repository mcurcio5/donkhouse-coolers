# donkhouse-coolers

I know some people were skeptical about hands played on the website Donkhouse.com. To check if the site overall changed poker equities, I wrote some javascript code to "play" poker automatically in browser (ie bet/call 100 preflop and check till showdown). I call this code using selenium in play_donk.ipynb. I simulated around 7k hands, while scraping them with donk_scraper.py. 

In hands_stat_analysis.ipynb, I ran some basic tests of how hand equities change from street to street. I confirmed that preflop equity is realized equally on flops, turns and rivers and that the variance of these equities does not change. The site appears fair. However, I've included the simulated hand histories in the folders donk_1 - donk_8.
