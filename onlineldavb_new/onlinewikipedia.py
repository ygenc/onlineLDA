#!/usr/bin/python

# onlinewikipedia.py: Demonstrates the use of online VB for LDA to
# analyze a bunch of random Wikipedia articles.
#
# Copyright (C) 2010  Matthew D. Hoffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cPickle, string, numpy, getopt, sys, random, time, re, pprint

import onlineldavb
import wikirandom


def load_documents(filename):
    ids=[]
    docs=[]
    for line in  file(filename).readlines():
        combo=line.split('\t')
        ids.append(combo[0])
        docs.append(combo[1])
    
    return (docs, ids)

def main():
    """
    Downloads and analyzes a bunch of random Wikipedia articles using
    online VB for LDA.
    """
    
    doc_files=sys.argv[1]
    
    (docset, articlenames) = \
        load_documents(doc_files)
        
    D=len(docset) 
    
    # of topics
    K = int(sys.argv[2])
    
    # Our vocabulary
    vocab = file('./dictnostops_test.txt').readlines()
    W = len(vocab)

    # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
    '''kappa set to 0 to eliminate decay'''
    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0)
    # Run until we've seen D documents. (Feel free to interrupt *much*
    # sooner than this.)
    
   
   
    # Give them to online LDA
    (gamma, bound) = olda.update_lambda(docset)
    # Compute an estimate of held-out perplexity
    (wordids, wordcts) = onlineldavb.parse_doc_list(docset, olda._vocab)
    perwordbound = bound * len(docset) / (D * sum(map(sum, wordcts)))
    print '  rho_t = %f,  held-out perplexity estimate = %f' % \
        ( olda._rhot, numpy.exp(-perwordbound))

    # Save lambda, the parameters to the variational distributions
    # over topics, and gamma, the parameters to the variational
    # distributions over topic weights for the articles analyzed in
    # the last iteration.
    print (olda._lambda.shape)
    print (gamma.shape)
    
    numpy.savetxt('lambda.dat',  olda._lambda)
    numpy.savetxt('gamma.dat',   gamma)

if __name__ == '__main__':
    main()
