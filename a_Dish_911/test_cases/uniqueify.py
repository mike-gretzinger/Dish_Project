def parseArgs():
    parser = argparse.ArgumentParser(description='Parse input CSV file and create files that guarantee unique GNB IDs')
    parser.add_argument('-i','--input', type=str, default='C:/Users/mgretzing/Documents/projects/Dish/e911_GNB.csv', help='Input CSV File')
    return(vars(parser.parse_args()))

import argparse
import pandas as pd
import time
import os
args = parseArgs()
df = pd.read_csv(args['input'])
file_name, ext  = os.path.splitext(args['input'])
df = df.dropna()
print(df)

col_names = df.columns.tolist()
header = ""
for i in col_names:
  header = header+str(i)+","

header = header.strip(',')

list_o_lists = [ [str(df['NR_Cell_Identity'].iloc[0])[0:8]] ]
print(list_o_lists)

index_lists = [ [0] ]
for i, row in df.iterrows():
  print("working on row: " + str(i))
  if i == 0:
    i+=1
    continue

  ci = row['NR_Cell_Identity'][0:8]
  didit = False
  for j, o_list in enumerate(list_o_lists):
    if ci not in o_list:
      list_o_lists[j].append(ci)
      index_lists[j].append(i)
      didit = True
      break
      
  if didit == False:
    list_o_lists.append([ci])
    index_lists.append([i])
     
  i+=1

for i, i_list in enumerate(index_lists):
  print("writing to file: " + str(i))
  f = open(file_name+'_'+str(i)+ext, "w")
  f.write(header+'\n')
  for idx in i_list:
    line_txt = ''
    for col in col_names:
      line_txt = line_txt+str(df[col].iloc[idx])+","
    f.write(line_txt.strip(',')+'\n')
  f.close()








