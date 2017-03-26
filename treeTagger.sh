mkdir -p tree-tagger
cd tree-tagger/
wget http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/data/tagger-scripts.tar.gz
wget http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/data/install-tagger.sh
wget http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/data/french-par-linux-3.2-utf8.bin.gz
wget http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/data/french-chunker-par-linux-3.2-utf8.bin.gz
source install-tagger.sh 
export LOCALTAGDIR='~/tree-tagger/'
exit
