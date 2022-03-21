x = " isole di ghiaccio , ciao, ppp, ,, 'adsf, asdfa asdfad,"

map_list = x.split(',')
for element in map_list:
    x = element.lstrip(' ')
    y = x.rstrip(' ')
    if y:
        map_list.remove(element)

print(map_list)