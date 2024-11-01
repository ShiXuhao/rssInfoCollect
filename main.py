TOTAL = 0


infoDownloader = 'infoDownloader.py'
sentimentAnalysis = 'sentimentAnalysisUnit.py'

if __name__ == '__main__':
    exec(open(infoDownloader).read())
    exec(open(sentimentAnalysis).read())