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
dict_o_lists = {}
dict_o_lists[str(df['AWS Region'].iloc[0])] = [ [str(df['NR_Cell_Identity'].iloc[0])[0:8]] ]
print(dict_o_lists)

index_dict = {}
index_dict [str(df['AWS Region'].iloc[0])] = [ [0] ]
for i, row in df.iterrows():
  print("working on row: " + str(i) + ' region: '+row['AWS Region'])
  if i == 0:
    continue

  ci = row['NR_Cell_Identity'][0:8]
  if row['AWS Region'] not in dict_o_lists.keys():
    dict_o_lists[str(row['AWS Region'])] = [ [ci] ]
    index_dict[str(row['AWS Region'])] = [ [i] ]
    print(dict_o_lists)
    continue
    
  didit = False
  for j, o_list in enumerate(dict_o_lists[str(row['AWS Region'])]):
    if ci not in o_list:
      dict_o_lists[str(row['AWS Region'])][j].append(ci)
      index_dict[str(row['AWS Region'])][j].append(i)
      didit = True
      break
      
  if didit == False:
    dict_o_lists[str(row['AWS Region'])].append([ci])
    index_dict[str(row['AWS Region'])].append([i])
     
for region in dict_o_lists.keys():
  for i, i_list in enumerate(index_dict[region]):
    print("writing to file: " + region +" "+ str(i))
    f = open(file_name+'_'+region.replace(" ", "")+'_'+str(i)+ext, "w")
    f.write(header+'\n')
    for idx in i_list:
      line_txt = ''
      for col in col_names:
        line_txt = line_txt+str(df[col].iloc[idx])+","
      f.write(line_txt.strip(',')+'\n')
    f.close()








