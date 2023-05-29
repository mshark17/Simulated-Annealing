import math
import random
import copy
from tkinter import *
import time
import matplotlib
import ujson
import matplotlib.pyplot as plt
import tkcap
import imageio

counter_while=0
guiglobal = []
guigrid = []
counter_screenshots=0

def annealing(fileName):
  st = time.time()
  #Initalize random place for the array using function and return it
  # Retrun [array , no of cells , no of connections ]
  file = open(fileName, "r")
  placement, dict, numberOfCells, numberOfConnections = random_initalize(fileName)
  x_axis1 = [0.75,0.8,0.85,0.9,0.95]
  y_axis1 = []
  temp_x_axis = []
  temp_y_axis = []
  cf= {}
  [nets, cf] = ConnectionsGetter(file, numberOfConnections, numberOfCells)
  for x in x_axis1:
    size = [len(placement), len(placement[0])]
    global guiglobal
    global guigrid
    guiglobal = size
    #Use HPWL and Get inital cose
    HPWL_dict = {}
    cL, HPWL_dict = HPWLL(nets, dict)
    T = 500 * cL  # initial temp
    Tf = pow(5 * 10, -6) * cL / numberOfConnections
    moves = int(10*numberOfCells)
    count = 0
    while T > Tf:
      #pick 2 random number in the range of cells
      index1 = [random.randint(0,len(placement) - 1),random.randint(0,len(placement[0]) - 1)]
      index2 = [random.randint(0,len(placement) - 1),random.randint(0,len(placement[0]) - 1)]
      while index1 == index2:
        index2 = [random.randint(0,len(placement) - 1),random.randint(0,len(placement[0]) - 1)]
      selected = []
      HPWL_newDict = {}
      #swap in the current array and return with new array
      newPlacement, newDict, selected = swap(placement, index1, index2, dict)
      n, HPWL_newDict = HPWL(nets, newDict, cf , selected, cL, HPWL_dict)
      deltaL = n - cL
      if deltaL < 0:
        placement = ujson.loads(ujson.dumps(newPlacement))
        dict = newDict.copy()
        cL = n
        storePlacement = ujson.loads(ujson.dumps(placement))
        HPWL_dict = HPWL_newDict.copy()
        storeL = cL
      else:
        value = -deltaL / T
        e = math.exp(value)
        rand = random.uniform(0, 1)
        if rand < e:
          placement = ujson.loads(ujson.dumps(newPlacement))
          dict = newDict.copy()
          HPWL_dict = HPWL_newDict.copy()
          cL = n
      count = count + 1
      if (count == moves or moves == 0):
        T = x * T
        count = 0
        temp_x_axis.append(T)
        temp_y_axis.append(cL)
    if (storeL < cL):
      placement = copy.ujson.loads(ujson.dumps(storePlacement))
      cL = storeL
    guigrid = placement
    gui()
    root.update()
    sss="--"
    for row in placement:
      temp=""
      for item in row:
        if str(item) =="-1":
          temp=temp + '{:4}'.format(sss)
        else:
          temp=temp + str('{:4}'.format(str(item)))
      print(temp)
    print("\n")
    for row in placement:
      temp=""
      for item in row:
        if str(item) == "-1":
          temp = temp + '{:4}'.format(str(1))
        else:
          temp=temp + str('{:4}'.format(str(0)))
      print(temp)
    print("\n\n The estimated wire length is " + str(cL))
    y_axis1.append(cL)
    reversed_list_x = list(reversed(temp_x_axis))
    reversed_list_y = list(reversed(temp_y_axis))
    end=time.time()
    print("\n\n The run time of the program is " + str(end - st)+ " seconds")
  plot_graphs(x_axis1,y_axis1,reversed_list_x,reversed_list_y,fileName)

def plot_graphs(x_axis1,y_axis1,x_axis2,y_axis2,fileName):
  plt.plot(x_axis1,y_axis1)
  plt.xlabel('Cooling Rate')
  # naming the y axis
  plt.ylabel('Total Wire Length')
  # giving a title to my graph
  plt.title('Total Wire Length vs Cooling Rate \n{}'.format(fileName))
  # function to show the plot
  matplotlib.pyplot.savefig("Screenshots_graphs\TWLvsCR_{}.png".format(fileName[0:2]))
  plt.show()
    
  fig,ax = plt.subplots()
  ax.plot(x_axis2, y_axis2)
  plt.plot()
  ax.set_xscale('log')
  plt.xlabel('Temperature')
  # naming the y axis
  plt.ylabel('Total Wire Length')

  # giving a title to my graph
  plt.title('Total Wire Length vs Temperature \n{}'.format(fileName))

  matplotlib.pyplot.savefig("Screenshots_graphs\TWLvsTemp_{}.png".format(fileName[0:2]))
  # function to show the plot
  plt.show()

##############################################################
def gui():
  for rows in range(guiglobal[0]):
    for cols in range(guiglobal[1]):
      Grid.rowconfigure(root,rows,weight=1)
      Grid.columnconfigure(root,cols,weight=1)
      if guigrid[rows][cols] == -1:
        Button(root,bg="black",text='',height=1,justify="center",state="disabled",width=1).grid(row=rows,column=cols,sticky="NSEW")
      else:
        Button(root,bg="white",border= True,text='%s' % (guigrid[rows][cols]),fg="black",height=1,justify="center",state="disabled",width=1).grid(row=rows, column=cols,  sticky="NSEW")
  global counter_screenshots
  cap = tkcap.CAP(root)     # master is an instance of tkinter.Tk
  cap.capture("Screenshots_gui\screenshot_{}.png".format(counter_screenshots),overwrite=True)
  counter_screenshots=counter_screenshots+1

##############################################################
def random_initalize(filename):
  infile = open(filename, "r")
  lines = infile.readlines()
  first_line = lines[0].split()
  components = int(first_line[0])
  nets = int(first_line[1])
  ny = int(first_line[2])
  nx = int(first_line[3])
  # initialize grid with -ve ones indicate empty cells
  grid = [[-1] * nx for _ in range(ny)]
  # create a dictionary of nets
  sites_dict = {}
  # randomize the grid by giving different ids
  site_id = 0
  while site_id < components:
    x = random.randint(0, ny - 1)
    y = random.randint(0, nx - 1)
    if grid[x][y] == -1:
      grid[x][y] = site_id
      sites_dict[site_id] = [x, y]
      site_id += 1
  infile.close()
  return grid, sites_dict, components, nets
##############################################################
def ConnectionsGetter(file, connections, cells):
  # initialize variables
  total_nets = []
  All_connections = {i: {} for i in range(cells)}
  # read connections from file and build All_connections and total_nets
  for i in range(connections):
    connection = list(map(int, file.readline().split()[1:]))
    for j in connection:
      All_connections[j][i] = i
    total_nets.append(connection)
  return total_nets, All_connections

##############################################################


def HPWLL(nets, dict):
  HPWL_dict = {}
  hpwl = 0

  for i, net in enumerate(nets):
    x_coords = [dict[cell][0] for cell in net]
    y_coords = [dict[cell][1] for cell in net]
    width = max(x_coords) - min(x_coords)
    height = max(y_coords) - min(y_coords)
    temp = width + height
    HPWL_dict[i] = temp
    hpwl += temp

  return hpwl, HPWL_dict


##############################################################
def HPWL( nets, dict, cf, selected, cL, HPWL_dict):
  finished = set()
  HPWL_dict_new = HPWL_dict.copy()
  hpwl = cL

  for cell in selected:
    for net_idx in cf[cell]:
      if net_idx not in finished:
        finished.add(net_idx)
        hpwl -= HPWL_dict_new[net_idx]

        x_coords, y_coords = zip(*[dict[pin] for pin in nets[net_idx]])
        width, height = max(x_coords) - min(x_coords), max(y_coords) - min(y_coords)
        HPWL_dict_new[net_idx] = width + height
        hpwl += HPWL_dict_new[net_idx]

  return hpwl, HPWL_dict_new

##############################################################
def swap(placement, i1, i2, d):
  new_placement = [row[:] for row in placement]  # create a copy of the placement array
  cell1, cell2 = placement[i1[0]][i1[1]], placement[i2[0]][i2[1]]
  selected = [cell for cell in [cell1, cell2] if cell != -1]  # add non-empty cells to selected list
  new_dict = d.copy()
  if cell1 != -1 and cell2 != -1:
    new_dict[cell1], new_dict[cell2] = i2, i1  # swap cell positions in dictionary
  elif cell1 != -1:
    new_dict[cell1] = i2
  else:
    new_dict[cell2] = i1
  new_placement[i1[0]][i1[1]], new_placement[i2[0]][i2[1]] = cell2, cell1  # swap cell positions in placement array
  return new_placement, new_dict, selected

##############################################################
#####   MAIN  ######
fileName = ""
print("Please specify the file name that you to use as a testing file e.g d1.txt: ")
fileName = input()
root = Tk()
root.geometry("750x750")
annealing(str(fileName))
images = []
for i in range(counter_screenshots):
  images.append(imageio.imread("Screenshots_gui\screenshot_{}.png".format(i)))
imageio.mimwrite('Gifs\{}.gif'.format(fileName[0:2]), images,format="gif")
root.mainloop()