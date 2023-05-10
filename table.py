import optparse
import yaml
import statistics

def add_space_size(string):
  x = f'{int(string):,d}'.replace(',', '\\,')
  return x

def add_space_time(string):
  y = str(string).split('.')[0]
  z = str(string).split('.')[1]
  y = f'{int(y):,d}'.replace(',', '\\,')
  return y +'.'+ z

def printsize(data, case, tool):
  casedata = data[case]
  if casedata.get(tool, {}).get('reachability') == ' ':
    return "noresults"
  elif casedata.get(tool, {}).get('reachability') != ' ' and casedata.get(tool, {}).get('reachability', {}).get('size', '-') != '-':
    sizes = casedata.get(tool, {}).get('reachability', {}).get('size', {})
    return add_space_size(sizes)
  else:
    sizes = "\\textbf{--}"
    return sizes

def printtime(data, case, tool):
  casedata = data[case]
  if casedata.get(tool, {}).get('reachability') == ' ':
    return "noresults"
  elif casedata.get(tool, {}).get('reachability').get('times', {}) != 'timeout' and casedata.get(tool, {}).get('reachability').get('times', {}) != 'outofmemory':
    times = casedata.get(tool, {}).get('reachability', {}).get('time', {})
    return float('{:.1f}'.format(times))
  elif casedata.get(tool, {}).get('reachability').get('times', {}) == 'timeout':
    return "t-o"
  elif casedata.get(tool, {}).get('reachability').get('times', {}) == 'outofmemory':
    return "o-o-m"
  else:
    times = "\\textbf{--}"
    return times

def getrow(data, D, case, reportsizes, reporttimes, stdev):
  result = ''
  if reportsizes:
    result += ' {0} & {1} & {2} & {3}'.format(printsize(data, case, 'static_only'),
      printsize(data, case, 'default_master'),
      printsize(data, case, 'default_parunfold'),
      printsize(data, case, 'alternative_parunfold'))
    if printsize(data, case, 'static_only') == printsize(data, case, 'default_master') == printsize(data, case, 'default_parunfold') == printsize(data, case, 'alternative_parunfold'):
        result = '\\multicolumn{4}{c|}{' + format(printsize(data, case, 'static_only') + '}')
    elif printsize(data, case, 'static_only') == printsize(data, case, 'default_master') and (printsize(data, case, 'default_parunfold') == printsize(data, case, 'alternative_parunfold'))  :
        result = '\\multicolumn{2}{c|}{' + format(printsize(data, case, 'static_only')) + '}' + ' &\\multicolumn{2}{c|}{' + format(printsize(data, case, 'default_parunfold') + '}')
    elif printsize(data, case, 'static_only') == printsize(data, case, 'default_master') == printsize(data, case, 'default_parunfold'):
        result = '\\multicolumn{3}{c|}{' + format(printsize(data, case, 'static_only')) + '} & \\multicolumn{1}{c|}{' + format(printsize(data, case, 'alternative_parunfold') + '}')
    elif printsize(data, case, 'default_master') == printsize(data, case, 'default_parunfold') == printsize(data, case, 'alternative_parunfold'):
        result = format(printsize(data, case, 'static_only') + ' & \\multicolumn{3}{|c|}{' + format(printsize(data, case, 'default_master')) + '}')

  if reporttimes:
    result += '& {0}{1} & {2}{3} & {4}{5} & {6}{7}'.format(get_mean(data, case, D, 'static_only'), get_stdev(data, case, D, 'static_only', stdev) ,
      get_mean(data, case, D, 'default_master'), get_stdev(data, case, D, 'default_master', stdev),
      get_mean(data, case, D, 'default_parunfold') , get_stdev(data, case, D, 'default_parunfold', stdev),
      get_mean(data, case, D, 'alternative_parunfold') , get_stdev(data, case, D, 'alternative_parunfold', stdev))

  return '{0} \\\\'.format(result)


def get_mean(data, case, D, tool):
  x = []
  casedata = data[case]
  if casedata.get(tool, {}).get('reachability').get('times', {}) != 'timeout' and casedata.get(tool, {}).get(
          'reachability').get('times', {}) != 'outofmemory':
    for d in D:
      x.append(printtime(d, case, tool))
    return add_space_time('{:.1f}'.format(statistics.mean(x)))
  else:
    return printtime(data, case, tool)

def get_stdev(data, case, D, tool, stdev):
  x = []
  casedata = data[case]
  if len(D) > 1 and stdev == True:
    if casedata.get(tool, {}).get('reachability').get('times', {}) != 'timeout' and casedata.get(tool, {}).get(
            'reachability').get('times', {}) != 'outofmemory':
      for d in D:
        x.append(printtime(d, case, tool))
      #print('SD {}'.format((statistics.stdev(x)*100)/statistics.mean(x)))
      return '(' + str(float('{:.1f}'.format(statistics.stdev(x)))) + ')'
    else:
      return ''
  else:
    return ''

def gettable(data, D, outfilename, sizes, times, stdev):
  print('Getting table, sizes: {0}, times: {1}'.format(sizes, str(times)))
  texfile = open(outfilename, 'w')
  y = sorted(data.keys())
  print(y)
  columns = 3
  if sizes:
    columns += 9
  if times:
    columns += 9

  texfile.write('''\\begin{center}
  \\renewcommand{\\arraystretch}{1.7}
    \\scriptsize
    ''')
  texfile.write(
    '\\begin{tabular}{r|c@{\\hspace{6pt}}c@{\\hspace{6pt}}c@{\\hspace{6pt}}c@{\\hspace{6pt}}|r@{\\hspace{6pt}}r@{\\hspace{6pt}}r@{\\hspace{6pt}}r}')
  texfile.write('{0}{1}\\\\'.format('\\multicolumn{1}{c}{Models} &  \\multicolumn{4}{c}{Sizes}' if sizes else '',
                                     ' & \\multicolumn{4}{c}{Times}' if times else ''))
  texfile.write('& {0}{1}\\\\'.format(
    '\\texttt{static} & \\texttt{def.master} & \\texttt{def.par} & \\texttt{alt.par}' if sizes else '',
    ' & \\texttt{static} & \\texttt{def.master} & \\texttt{def.par} & \\texttt{alt.par}' if times else ''))
  texfile.write('''
    \\toprule
    ''')

  for key in y:
    print(key)
    texfile.write('\\emph{' + key + '}&' + getrow(data, D, str(key), sizes, times, stdev))
    texfile.write('\n')

  texfile.write('''
\\bottomrule
\\end{tabular}
\\end{center}
''')
  texfile.close()
  return texfile.name


def runCmdLine():
  D = []
  parser = optparse.OptionParser(usage='usage: %prog [options] infile1 ... infilen outfile')
  parser.add_option('-s', action='store_true', dest='stdev',
                    help='Print standard deviation for the times')
  options, args = parser.parse_args()
  if len(args) < 2:
    parser.error(parser.usage)

  data = yaml.safe_load(open(args[0]).read())
  for i in args[:-1]:
    D.append(yaml.safe_load(open(i).read()))
  outfilename = args[-1]

  gettable(data, D, outfilename, sizes = True, times = True, stdev = options.stdev)

if __name__ == '__main__':
  runCmdLine()
