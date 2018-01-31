
import numpy as np

def extract_lifetimes(turnover_data, N_neuron):
    '''
    turnover data is assumed to be a numpy.array with 
    lines consisting of the four entries
    
      gen/prune, t, i, j     

    where 
      -- gen/prune :: 1 if synapse became active, 
                      0 if synapse became inactive
      -- t         :: simulation time point in seconds(!)
      -- i         :: pre-synaptic neuron index
      -- j         :: post-synaptic neuron index
      
    returns the collected
     -- lifetimes  :: duration from generation until pruning,
                      i.e. synapse generated but not yet 
                      pruned at simulation end are not included!
     -- deathtimes :: like lifetimes, but from death to generation,
                      i.e. time from begining of simulation until 
                      first generation is not included 
    '''

    # lexsort by pre- and post-synaptic indices
    # Example:
    #
    # array([[  1.,   0.,   2., 347.],
    #        [  1.,   0.,   3., 248.],
    #        [  1.,   0.,   4., 145.],
    #        [  1.,   0.,  14., 210.],
    #        [  1.,   0.,  20., 318.]])
    #
    # becomes
    #
    # array([[1.  , 7.19, 0.  , 1.  ],
    #        [1.  , 1.81, 0.  , 2.  ],
    #        [0.  , 1.86, 0.  , 2.  ],
    #        [1.  , 9.28, 0.  , 2.  ],
    #        [1.  , 1.89, 0.  , 3.  ]])


    ind = np.lexsort((turnover_data[:,3],turnover_data[:,2]))
    df_sorted = turnover_data[ind]

    # create result arrays and temporary storage
    lifetimes, deathtimes, current_synapse = [],[], []
    prev_s_id = 0.
    empty_array_count = 0

    for syn_rec in df_sorted:
        # concept:
        #   1. keep collect syn_records as long as pre-synaptic
        #   and post-synpatic neuron completely match (s_id)
        #
        #   2. if new synapse begins (prev_id != id), process the
        #   current collection by sorting it by time and computing
        #   array of differences.
        #
        #   3. odd entries are the lifetimes, even entries are the
        #   deathtimes
        
        s_id = syn_rec[2] * N_neuron + syn_rec[3]
        
        if not prev_s_id==s_id:

            if current_synapse==[]:
                # this can happen only when synapse 0,0 has no event
                empty_array_count += 1
                assert(empty_array_count < 2)

            else:
                c_array = np.array(current_synapse)
                ind = np.argsort(c_array[:,1])
                c_sort = c_array[ind]

                if len(c_sort) < 2:
                    pass
                else:
                    # first entry must be a synaspe insertion
                    # as we start with zero synapses 
                    assert(c_sort[0,0]==1)
                    life_death = np.diff(c_sort[:,1])

                    # finally add the data
                    lifetimes.extend(life_death[::2])
                    deathtimes.extend(life_death[1::2])

                current_synapse = []
                
        current_synapse.append(list(syn_rec))
        prev_s_id = s_id

    return np.array(lifetimes), np.array(deathtimes)



def extract_active_synapse_count(turnover_data):
    '''
    computes the total number of active synapses at 
    each time step

    turnover data is assumed to be a numpy.array with 
    rows consisting of the four entries
    
      gen/prune, t, i, j     

    where 
      -- gen/prune :: 1 if synapse became active, 
                      0 if synapse became inactive
      -- t         :: simulation time point in seconds(!)
      -- i         :: pre-synaptic neuron index
      -- j         :: post-synaptic neuron index
      
    returns
      -- reduced_t        :: sparse time points at which the 
                             total number of active synapses 
                             changes (in seconds)
      -- reduced_n_active :: total number of active synapses 
                             at time point t
    '''
     
    # method consists of three main steps:
    #
    #   1. replace 0 with -1 in gen/prune data 
    #
    #   2. take cumsum of gen/prune points, this gives already
    #       gives the number of active synapses at each point
    #
    #   3. however,
    #
    #         1 0.2  5 13
    #         1 0.2 45 42
    #         1 0.2  2 55
    #
    #      for example, will result in mutiple values for
    #      time point 0.2 (cn=1,2,3), so "clean up" data to only
    #      take last value (cn=3) for t=0.2.

    y = turnover_data[:,0]
    y[y==0]=-1

    # appending both starting and endpoints such that for loop
    # below fully captures all data
    n_active = np.concatenate(([0],np.cumsum(y),[-1]))
    full_t = np.concatenate(([0.],turnover_data[:,1],[-1]))
    
    reduced_t, reduced_n_active = [], []
    prev_t = 0
    
    for j,t in enumerate(full_t):
        if prev_t != t:
            reduced_t.append(full_t[j-1])
            reduced_n_active.append(n_active[j-1])
        prev_t = t   

    return np.array(reduced_t), np.array(reduced_n_active)

    

if __name__ == "__main__":
    turnover_data = np.genfromtxt('tmp_turnover',delimiter=',')
    lt, dt = process_turnover_data(turnover_data, 400)

    ind = np.lexsort((turnover_data[:,3],turnover_data[:,2]))
    df_sorted = turnover_data[ind]
    print(df_sorted[:6])
    print(lt[:5])
