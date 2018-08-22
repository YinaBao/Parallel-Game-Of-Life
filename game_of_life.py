from mpi4py import MPI
import numpy
import time

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
stat = MPI.Status()

prob = 0.7
COLS = 200
ROWS = 200
generations = 100

subROWS = ROWS//size + 2 #how many subrows for each worker

def msgUp(subGrid):
    # Sends and Recvs rows with Rank+1
    comm.send(subGrid[subROWS-2,:],dest=rank+1)
    subGrid[subROWS-1,:]=comm.recv(source=rank+1)
    return 0

def msgDn(subGrid):
    # Sends and Recvs rows with Rank-1
    comm.send(subGrid[1,:],dest=rank-1)
    subGrid[0,:] = comm.recv(source=rank-1)
    return 0

def computeGridPoints(subGrid): # watch for the indexs
    M = subGrid
    intermediateM = numpy.copy(M)
    for ROWelem in xrange(1,subROWS-1):
        for COLelem in xrange(1,COLS-1):
            sum = (M[ROWelem - 1, COLelem - 1] + M[ROWelem - 1, COLelem] + M[ROWelem - 1, COLelem + 1]
                   + M[ROWelem, COLelem - 1] + M[ROWelem, COLelem + 1]
                   + M[ROWelem + 1, COLelem - 1] + M[ROWelem + 1, COLelem] + M[ROWelem + 1, COLelem + 1])
            #               print(ROWelem," ",COLelem," ",sum)
            if M[ROWelem, COLelem] == 1:
                if sum < 2:
                    intermediateM[ROWelem, COLelem] = 0
                elif sum > 3:
                    intermediateM[ROWelem, COLelem] = 0
                else:
                    intermediateM[ROWelem, COLelem] = 1
            if M[ROWelem, COLelem] == 0:
                if sum == 3:
                    intermediateM[ROWelem, COLelem] = 1
                else:
                    intermediateM[ROWelem, COLelem] = 0
        M = numpy.copy(intermediateM)
        return M

subGrid = numpy.random.binomial(1,prob,size=subROWS*COLS)
subGrid = numpy.reshape(subGrid,(subROWS,COLS))
# print subGrid

for i in xrange(1,100):
    # i = 1
    print rank, i
    subGrid = computeGridPoints(subGrid)
    #time.sleep(2)
    if rank == 0:
    #    print rank,"up!"
        msgUp(subGrid)
    elif rank == size - 1:
    #    print rank,"down!"
        msgDn(subGrid)
    else:
    #    print rank,"up/down!"
        msgUp(subGrid)
        msgDn(subGrid)
    #print rank,"mid"
    temp_grid = comm.gather(subGrid[1:subROWS - 1, :],root = 0)
    if 0==rank:
        #time.sleep(2)
        print "rank0",rank
    #    temp_grid = comm.gather(subGrid[1:subROWS - 1, :],root = 0)
        #tg_sum = numpy.sum(temp_grid)
        print "iter:", i, "sum:", numpy.sum(temp_grid)
        result = numpy.vstack(temp_grid)
        print result
    #print rank,"ddone"
    #newGrid=comm.gather(subGrid[1:subROWS - 1, :], root=0)
    #print newGrid
