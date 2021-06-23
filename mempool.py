class Mempool:
    def __init__(self):
        #we're going to use a priority queue since this will
        #let us add all our transactions in O(n log n) while letting us access
        #the smallest fee in O(n) time
        self.priority = []
        #we're going to use a dictionary for TXHash so we can retrieve our line
        #and make sure that duplicate values don't get overwritten
        self.hash_dict = {}


    #This will add our transaction to our mempool if it passes all tests
    def add_transaction(self, transaction):
        #parse our transaction line
        try:
            newval, newhash = self.parse_tran(transaction)
        except Exception as e:
            raise e
            
        #size check
        if len(self.priority) == 5000:
#             print('its over 5000')
            #will actually be max value ('closest to 0') since priority queue is a min heap
            min_val = float('-inf')
            min_ind = None
            
            #finds smallest value
            for i in range(len(self.priority)):
                if self.priority[i][0] > min_val:
                    min_val = self.priority[i][0]
                    min_hash = self.priority[i][1]
                    min_ind = i
            
#             print(min_val, newval)
            #replace min value and add newval, then reorder priority queue
            self.priority[min_ind] = self.priority[-1]
            self.priority[-1] = (newval, newhash)
            heapq.heapify(self.priority)
            
            #update dictionary
            del self.hash_dict[min_hash]
            self.hash_dict[newhash] = transaction

        else:
#             print('adding to mempool')
            heapq.heappush(self.priority, (newval, newhash))
            self.hash_dict[newhash] = transaction

                

    def parse_tran(self, transaction):
        #make sure that this function returns the gas fee * gas * -1
        #and our txtHash. We should also make sure that transactions
        #are properly formatted
        line = transaction.split(' ')

        #check if four lines
        if len(line) != 4:
            raise ValueError('transactions should only have 4 elements')
        
        #check if Txhash is correct
        try:
            hash_parse = line[0].split('=')
            if hash_parse[0] != 'TxHash':
                raise ValueError('Line is not properly in order')
            newhash = hash_parse[1]
            
            #type and length testing
            assert len(newhash)== 64, 'hash length is invalid'
#             assert type(newhash) is str, 'hash type is invalid'
            assert newhash not in self.hash_dict, 'somethings gone wrong, we should never see the same hash'
                
        except Exception as e:
            print(e)
            raise ValueError('TxHash is not properly formatted')
            
        #calculate newval 
        try:
            gas_parse = line[1].split('=')
            fee_parse = line[2].split('=')

            if gas_parse[0] != 'Gas' or fee_parse[0] != 'FeePerGas':
                raise ValueError('Line is not properly in order')

                
            #I'm choosing to convert our gas to an int because our transactions file only
            #has it in that format.
            gas, fees = int(gas_parse[1]), float(fee_parse[1])
            #multiplying by negative one so our min heap priority queue will rank by highest
            newval = gas * fees * -1
            assert newval <= 0, 'newval should never be positive'
            
                
        except Exception as e:
            print(e)
            raise ValueError('Gas and Fees are not properly formatted')
        
        return newval, newhash
    
    def output_mempool(self):
        #if we wanted to just get a txt file and no longer use the mempool at all,
        #we could just iteratively heappop our priority queue until it's empty and then
        #return that (n log n runtime). Provided that we want the text document and want 
        #to retain a mempool of our transactions though, we sort our mempool, iterate through, 
        #then heapify it again (n log n runtime * 2, which becomes n log n runtime)
        
        self.priority.sort()
        
        with open('prioritized-transactions.txt', 'w') as f:       
            for fees, txhash in self.priority:
#                 print(fees)
                f.write(self.hash_dict[txhash])
                
        f.close()
        heapq.heapify(self.priority)


#running file       
test = Mempool()
with open('transactions.txt', 'r') as reader:
    count = 0
    for line in reader:
        try:
            test.add_transaction(line)
        except Exception as e:
            print(line)
            print(e)
            pass
test.output_mempool()     
    