import numpy as np
from copy import deepcopy

DEBUGMODE = False


class Make10:
    def __init__(self):
        self.digits = ''
        self.vec = []
        self.clear()

    def clear(self):
        self.solutions = []
        self.all_exprs = {}
        self.hash_maps = {}
        self.hash_exprs = set()
        self.found_exprs = set()

    def random(self):
        self.clear()
        while len(self.solutions) == 0:
            self.digits = str(np.random.randint(10000))
            if len(self.digits) < 4:
                self.digits = np.random.choice(['2458', '3458', '1266', '2267', '3479', '1459', '4577', '2477', '1112', '0456'], 1)
            self.vec = [c for c in self.digits]
            self.initialize()
        print('\n\n\nMake 10 using %s' % self.digits)

    def enter(self):
        self.clear()
        while len(self.solutions) == 0:
            self.digits = input('\n\n\nWrite some digits to make 10 : ')
            self.vec = [c for c in self.digits if c.isnumeric()]
            self.initialize()
        print('\n\n\nMake 10 using %s' % self.digits)

    def initialize(self):
        self.clear()
        all_hash_exprs = []
        for numbers in findPartitions(self.vec):
            unique_exprs, all_exprs, hash_map, hash_exprs = uniqueExpressions(numbers)
            self.solutions.extend(unique_exprs)
            self.all_exprs.update(all_exprs)
            self.hash_maps.update(hash_map)
            all_hash_exprs.extend(hash_exprs)
        
        self.hash_exprs = set(tuple(expr) for expr in all_hash_exprs)

        if DEBUGMODE:
            print('\n\n\nsolutions: ', self.solutions)
            print('\n\n\nall_exprs: ', self.all_exprs)
            print('\n\n\nhash_maps: ', self.hash_maps)
            print('\n\n\nhash_exprs:', self.hash_exprs, '\n\n\n\n\n')

    def findSolution(self):
        while True:
            if len(self.found_exprs) == len(self.hash_exprs):
                print('\n\n\nFound all %d expressions. You win!' % len(self.hash_exprs))
                break

            try:
                expr = input('\n\n\nWrite an expression eval to 10 using any permutation of %s (1 or 2 digit numbers) and opterators + - * / ** without brackets : ' % self.digits)
                hash_expr = expr2hash(expr)

                if hash_expr in self.hash_exprs and hash_expr not in self.found_exprs:
                    self.found_exprs.add(hash_expr)
                    print('\n\n\nCorrect! Found %d expressions. %d more to go.' % \
                            (len(self.found_exprs), len(self.hash_exprs) - len(self.found_exprs)))

                elif hash_expr in self.hash_exprs and hash_expr in self.found_exprs:
                    print('\n\n\nCorrect, but you already found some expressions of the same category :')
                    combos = findCombinations([self.hash_maps[key] for key in hash_expr])
                    print([''.join(combo).replace(' ', '') for combo in combos])

                elif self.validateExpr(expr):
                    print('\n\n\nBonus! You found an extra solution %s' % expr)

                else:
                    print('\n\n\n%s is not a solution. Try again!' % expr)

            except KeyboardInterrupt:
                print('\n\n\nExit game...')
                break

            except Exception as e:
                print('\n\n\nPlease enter valid expressions only. Re-start game...')
                self.random()

    def solutions(self):
        return self.solutions

    def allExprs(self):
        return self.all_exprs

    def hashMaps(self):
        return self.hash_maps

    def hashExprs(self):
        return self.hash_exprs

    def validateExpr(self, expr):
        return eval(expr) == 10


def uniqueLstOfLst(lstOfLst):
    return [list(uniq) for uniq in set(tuple(lst) for lst in lstOfLst)]


def findPartitions(vec):
    # find all unique unordered partitions of vec
    # input: a list, each vec[i] is a char of a digit
    # output: list of numbers, [numbers1,...],
    #         numbers1 is a list, each numbers1[i] is a string of 1 or 2 digits

    partitions = []

    def recursion(v, curpart):
        if v == []:
            partitions.append(sorted(curpart[:]))
            return

        for i in range(len(v)):
            # choose a number of 1 digit
            curpart.append(v[i])
            vi = v.pop(i)
            recursion(v, curpart)
            v.insert(i, vi)
            curpart.pop()

        for i in range(len(v) - 1):
            for j in range(i + 1, len(v)):
                # choose a number of 2 digits
                for num in set([v[i] + v[j], v[j] + v[i]]):
                    curpart.append(num)
                    vi = v.pop(i)
                    vj = v.pop(j - 1)
                    recursion(v, curpart)
                    v.insert(i, vi)
                    v.insert(j, vj)
                    curpart.pop()
        return

    recursion(vec, [])
    return uniqueLstOfLst(partitions)


def findMatchings(numbers):
    # find all valid matchings of operator and number, a valid matching must have '+' or '-'
    # input: a list, each numbers[i] is a string of number
    # output: list of matchings, [matching1,...],
    #         matching1 is a list, each matching1[i] is a string of op+' '+num

    matchings = []

    def recursion(nums, curmatch):
        if nums == []:
            if np.any(['+' in m or '-' in m for m in curmatch]):
                matchings.append(curmatch[:])
            return

        for op in ['+', '-', '*', '/', '**']:
            if op == '**' and len(nums[0]) > 1:
                continue # avoid blowing up

            curmatch.append(op + ' ' + nums[0]) # space helps distinguish '* ' and '** '
            recursion(nums[1:], curmatch)
            curmatch.pop()
        return

    recursion(numbers, [])
    return matchings


def findExpressions(matching):
    # find all valid expressions of a matching eval to 10
    # input: a list, matching[i] is a string of op+' '+num
    # output: list of list of items, [ [itemA1, itemA2, ...], [itemB1, itemB2, ...], ...]
    #         where [itemA1,...] is a partition of a matching eval to 10,
    #         itemA1 is a list, each itemA1[i] is a string of op+' '+num,
    #         itemA1 must have only one '+' or '-'

    group1 = [m for m in matching if m[:2] in ['+ ', '- ']]
    group2 = [m for m in matching if m[:2] in ['* ', '/ ']]
    group3 = [m for m in matching if m[:2] == '**']

    items = [[m] for m in group1] # each group1[i] corresponds to an item
    expressions = []

    def recursion2(gr2):
        if gr2 == []: # items = [[m1, group2[i..j]], [m2, group2[k..z]], ...]
            recursion3(group3)
            return

        for item in items:
            # choose an item for gr2[0] to join
            item.append(gr2[0])
            recursion2(gr2[1:])
            item.pop()
        return

    def recursion3(gr3):
        if gr3 == []:
            expr = ' '.join([' '.join(item) for item in items])
            try:
                if eval(expr) == 10:
                    expressions.append(deepcopy(items))
            except:
                pass
            return

        for item in items:
            # choose an item for gr3[0] to join

            if np.any(['**' in x for x in item]):
                continue # avoid blowing up

            for i in range(len(item)):
                # choose item[i] to append gr3[0]
                tmp = item[i]
                item[i] += gr3[0]
                recursion3(gr3[1:])
                item[i] = tmp
        return

    recursion2(group2)
    return expressions


def hashKey(item):
    # generate the hash key of an item: sorted assoc_ops and their corresponding sorted nums and the rest of the item
    # eg, the hash key of ['+ 5', '* 2** 4', '/ 8'] is '*+,2** 4,5,/ 8'

    #item = [m if not m.split()[1] == '0**' else 0 for m in item]
    #item = [m if not m.endswith('** 1') else m.replace('** 1', '') for m in item]
    #item = [m if not m == '/ 1' else m for m in item]
    #item = [m for m in item if m != '']

    assoc_ops = ['+', '-', '*']
    # given itemA and itemB (each with only one '+' or '-' at front, and each itemA[i] or itemB[j] is a string of op+' '+num),
    # rearangements assoc_ops for itemA[i] and itemB[j] are identified as the same category
    # eg, ['+ 4', '* 5'] and ['+ 5', '* 4'] are of the same category
    # eg, ['+ 2** 4', '* 5', '/ 8'] and ['+ 5', '* 2** 4', '/ 8'] are of the same category

    ops = [m[0] for m in item if m[0] in assoc_ops]
    nums = [m[2:] for m in item if m[0] in assoc_ops]
    rest = [m for m in item if m[0] not in assoc_ops]

    ops = ''.join(sorted(ops))
    nums = ','.join(sorted(nums))
    rest = ','.join(sorted(rest))

    key = ','.join([ops, nums, rest])
    return key


def addHash(item, hash_map):
    key = hashKey(item)
    if key not in hash_map:
        hash_map[key] = []
    hash_map[key].append(' '.join(item))
    return key


def findCombinations(lstOfLst):
    # input: list of list of various lengths
    # output: list of different combinations of an item from each inner list

    if len(lstOfLst) == 0:
       return [[]]

    lastLst = lstOfLst[-1]
    prevCombos = findCombinations(lstOfLst[:-1])
    ret = []

    for innerLst in prevCombos:
        for item in lastLst:
            innerLst.append(item)
            ret.append(innerLst[:])
            innerLst.pop()
    
    return ret


def uniqueExpressions(numbers):
    # use hash map for grouping expressions of the same category

    # find all possible expressions, may contain duplicate expressions of the same category
    dup_exprs = []

    for matching in findMatchings(numbers):
        expressions = findExpressions(matching)
        if expressions:
            dup_exprs.extend(expressions)

    if not dup_exprs:
        return [], {}, {}, []


    # convert each expression into a list of hashKeys
<<<<<<< HEAD
    hash_exprs = [] # list of list of sorted hashKeys
=======
    hash_exprs = [] # list of tuple of sorted hashKeys
>>>>>>> 7b96acb061929d2decaaa1fa6f04b50fa59feae2
    hash_map = {} # {hashKey : list of item_expr}, each item_expr=' '.join(item)

    for expr in dup_exprs: # each expr is a list of items eval to 10
        hash_exprs.append(sorted([addHash(item, hash_map) for item in expr]))
    hash_exprs = uniqueLstOfLst(hash_exprs)


    # clean up hash_map to have a map of unique expressions
    for key, lst in hash_map.items():
        hash_map[key] = sorted(set(lst))
    
    if DEBUGMODE:
        print('*'*200)
        print('numbers:         ', numbers)
        print('hash_map:        ', hash_map)
        print('uniq hash_exprs: ', hash_exprs)


    # find unique expressions
    unique_exprs = []
    all_exprs = {}
    
<<<<<<< HEAD
    for hash_expr in hash_exprs: # each hash_expr is a sorted list of hashKeys, eval to 10
=======
    for hash_expr in hash_exprs: # each hash_expr is a sorted tuple of hashKeys, eval to 10
>>>>>>> 7b96acb061929d2decaaa1fa6f04b50fa59feae2
        first_normal_expr = [hash_map[key][0] for key in hash_expr]
        first_normal_expr = ' '.join(first_normal_expr).replace(' ', '')
        unique_exprs.append(first_normal_expr)

        if first_normal_expr not in all_exprs:
            all_exprs[first_normal_expr] = []

        lstOfLst = [hash_map[key] for key in hash_expr]
        combos = findCombinations(lstOfLst)
        all_exprs[first_normal_expr] = [' '.join(lst).replace(' ', '') for lst in combos]

        if DEBUGMODE:
            print('#'*100)
            print('hash_expr:           ', hash_expr)
            print('first_normal_expr:   ', first_normal_expr)
            print('combos:              ', combos)

    return unique_exprs, all_exprs, hash_map, hash_exprs


def expr2hash(expr):
    # convert expr to hash_expr

    expr = expr.replace(' ', '')
    if expr[0] not in '+-':
        expr = '+' + expr
    print('Entered expression : %s' % expr)

    items = []
    item = []
    mat = ''
    i = 0

    while i < len(expr):
        if expr[i] in '+-':
            if mat:
                item.append(mat)
            if item:
                items.append(item[:])
            item = []
            mat = expr[i] + ' '
            i += 1

        elif expr[i].isnumeric():
            while i < len(expr) and expr[i].isnumeric():
                mat += expr[i]
                i += 1

            if i + 1 >= len(expr) or expr[i:(i+2)] != '**':
                item.append(mat)
                mat = ''

        elif i + 1 < len(expr) and expr[i:(i+2)] == '**':
            mat += expr[i:(i+2)] + ' '
            i += 2

        elif expr[i] in '*/':
            mat += expr[i] + ' '
            i += 1
    
        else:
            raise ValueError('unrecognised ' + expr[i])

    if item:
        items.append(item[:])

    return tuple(sorted([hashKey(item) for item in items]))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='count', default=0)
    parser.add_argument('-e', '--enter', action='count', default=0)
    args = parser.parse_args()

    if args.debug:
        DEBUGMODE = True

    game = Make10()

    if args.enter:
        game.enter()
    else:
        game.random()

    game.findSolution()

