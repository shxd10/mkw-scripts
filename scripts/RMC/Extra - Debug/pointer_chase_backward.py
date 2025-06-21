from dolphin import memory
import time
from Modules import agc_lib as lib



# Knuth-Morris-Pratt string matching
# David Eppstein, UC Irvine, 1 Mar 2002

def KnuthMorrisPratt(text, pattern):

    '''Yields all starting positions of copies of the pattern in the text.
Calling conventions are similar to string.find, but its arguments can be
lists or iterators, not just strings, it returns all matches, not just
the first one, and it does not need the whole text in memory at once.
Whenever it yields, it will have read the text exactly up to and including
the match that caused the yield.'''

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos


def list_of_possible_list(l):
    """Takes a list of list as an argmument.
        Return a list containing each possible list you can form from those list
        Ex : [  [a, b]
                [a]
                [c, e] ]
        Return : [ [a,a,c] , [a,a,e], [b,a,c] etc]"""
    res = []
    if l :
        tmp = list_of_possible_list(l[1:])
        for val in l[0]:
            for list_ in tmp:
                res.append([val]+list_)
    else:
        return [[]]
            
        

def scan_memory_array(addrStart, addrEnd, byte_array):
    t1 = time.time()
    memory_read = memory.read_bytes(addrStart, addrEnd-addrStart)
    t2 = time.time()
    res = [addrStart+offset for offset in KnuthMorrisPratt(memory_read, byte_array)]
    t3 = time.time()
    print(t2-t1, t3-t2)
    return res

def find_address_in_memory(addrStart, addrEnd, addrToFind, offsetmax):
    res = []
    for addr in range(addrStart, addrEnd, 4):
        if addrToFind - offsetmax <= memory.read_u32(addr) <= addrToFind:
            res.append(addr)
    return res

def find_address_in_memory_fast(inv_graph, addr, offsetmax):
    res = []
    for curaddr in range(addr, addr-offsetmax, -4):
        if curaddr in inv_graph.keys():
            #res = res+inv_graph[curaddr]
            res.append(min(inv_graph[curaddr]))
    return res

def is_addr(addr):
    return (0x80000000 <= addr <= 0x9FFFFFFF)

def create_graph():
    """Return a list where if addr is an address containing a pointer, list[addr] is the address pointed"""
    graph = {}
    for addr in range(0x80000000, 0x9FFFFFFF, 4):
        val = memory.read_u32(addr)
        if is_addr(val):
            graph[addr] = val
    return graph

def invert_graph(graph):
    """Return inv_graph so if graph[addr] is an address, inv_graph[graph[addr]] contain addr."""
    inv_graph = {}
    for addr in graph.keys():
        if graph[addr] not in inv_graph.keys():
            inv_graph[graph[addr]] = []
        inv_graph[graph[addr]].append(addr)
    return inv_graph

def graphtofile(filename, graph, address):
    """takes a graph (dic type), an address, and store to file"""
    f = open(filename, 'w')
    f.write(str(address)+"\n")
    for addr in graph.keys():
        f.write(str(addr)+','+str(graph[addr])+'\n')
    f.close()


def chase_backward(graph, inv_graph, startAddr, offsetmax, depth_max):
    """Return a list of ptr chain, starting from anywhere, leading to startAddr"""
    prev_addr_list = find_address_in_memory_fast(inv_graph, startAddr, offsetmax)
    res = [[startAddr]]
    if depth_max == 0:
        1+1
    else:
        for prev_addr in prev_addr_list:
            prev_res = chase_backward(graph, inv_graph, prev_addr, offsetmax, depth_max -1)
            for ptr_chain in prev_res:
                res.append(ptr_chain + [startAddr - graph[prev_addr]])
    return res


def chase_backward_multi_graph(graph_list, inv_graph_list, startAddr_list, offsetmax, depth_max):
    res = []
    if depth_max:
        for offset in range(0, offsetmax, 4):
            b = True
            for i in range(len(graph_list)):
                b = b and startAddr_list[i]-offset in inv_graph_list[i].keys()
            if b:
                addr_list_list = []
                for i in range(len(graph_list)):
                    addr_list_list.append(inv_graph_list[i][startAddr_list[i]-offset])
                possible_prev_addr_list = list_of_possible_list(addr_list_list)
                for prev_addr_list in possible_prev_addr_list:
                    prev_res = chase_backward_multi_graph(graph_list, inv_graph_list, prev_addr_list, offsetmax, depth_max-1)
                    for ptr_chain in prev_res:
                        res.append(ptr_chain + [offset])
    return res

                    
def main():
    
    s = lib.Split.from_rkg(lib.rkg_addr(), 1)
    l = scan_memory_array(0x80F00000, 0x81FFFFFF, s.time_format_bytes())
    print(len(l))
    print(hex(l[0]))
    t1 = time.time()
    g = create_graph()
    t2 = time.time()
    i = invert_graph(g)
    t3 = time.time()
    print('create: ', t2-t1)
    print('invert: ', t3-t2)
    if l:
        graphtofile('3.graph', g, l[0])
    
            

if __name__ == '__main__':
    main()




