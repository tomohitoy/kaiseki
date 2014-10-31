# coding:utf-8
# 文字列解析スクリプト
# 岩波書店 確率と情報の科学，高速文字列解析の世界に準拠

#
# 基本ファンクション
#

# ライブラリを使う
import collections as cl

# 位置iの文字T[i]を返す
def access(t_string,i_pos):
  return t_string[i_pos]

# T[0,i)中の文字cの出現数を返す
def rank(t_string,i_pos,c_target):
  target_string = t_string[0:i_pos]
  return target_string.count(c_target)

# T中の(i+1)番目のcの出現位置を返す
def select(t_string,i_pos,c_target):
  t_split = t_string.split(c_target)
  if c_target == '0':
    c_decoy = '1'
  else:
    c_decoy = '0'
  t_fixed = c_target.join([c_decoy.join(t_split[:i_pos+1])] + t_split[i_pos+1:])
  return t_fixed.find(c_target)

# T[s,e)中の(r+1)番目に大きい値を返す
def quantile(t_string,s_pos,e_pos,r_pos):
  t_target = t_string[s_pos:e_pos]
  t_target_list = list(set(t_target))
  t_target_list.sort(reverse=True)
  return t_target_list[r_pos+1]

# T[s,e)中で出現回数が多い文字順にその頻度とともにk個返す
def topk(t_string,s_pos,e_pos,k_num):
  return dict(cl.Counter(list(t_string[s_pos:e_pos])).most_common(k_num))

# T[s,e)中に出現するx<=c<yを満たす文字cの合計出現数を返す
def rangefreq(t_string,s_pos,e_pos,x_min,y_max):
  t_target = [t_frag for t_frag in t_string[s_pos:e_pos] if t_frag >= x_min and t_frag < y_max]
  return len(t_target)

# T[s,e)中に出現するx<=c<yの各文字cを頻度と共に列挙する
def rangelist(t_string,s_pos,e_pos,x_min,y_max):
  t_target = [t_frag for t_frag in t_string[s_pos:e_pos] if t_frag >= x_min and t_frag < y_max]
  return dict(cl.Counter(list(t_target)).most_common())

# T[s,e)中に出現する文字を大きい順にその頻度と共にk個返す
def rangemaxk(t_string,s_pos,e_pos,k_num):
  freq_dict = [{k:v} for k,v in sorted(cl.Counter(t_string[s_pos:e_pos]).items())][1:k_num+1]
  return freq_dict

# T[s,e)中に出現する文字を小さい順にその頻度とともにk個返す
def rangemink(t_string,s_pos,e_pos,k_num):
  freq_dict = [{k:v} for k,v in reversed(cl.Counter(t_string[s_pos:e_pos]).items())][1:k_num+1]
  return freq_dict

# T[s,e)中でx<=c<yを満たす最大のcを返す
def prevvalue(t_string,s_pos,e_pos,x_min,y_max):
  t_target = list(t_string[s_pos:e_pos])
  t_target.sort()
  joined_string = "".join(t_target)
  return joined_string.split(y_max)[0][-1]

# T[s,e)中でx<=c<yを満たす最小のcを返す
def nextvalue(t_string,s_pos,e_pos,x_min,y_max):
  t_target = list(t_string[s_pos:e_pos])
  t_target.sort()
  joined_string = "".join(t_target)
  if joined_string.find(x_min) > 0:
    return x_min
  else:
    return joined_string.split(x_min[-1][0])

# T[s1,e1)とT[s2,e2)の間で共通して出現する文字と頻度を返す
def intersect(t_string,s_pos1,e_pos1,s_pos2,e_pos2):
  t_target1 = t_string[s_pos1:e_pos1]
  t_target2 = t_string[s_pos2:e_pos2]
  t_common = set(t_target1).intersection(t_target2)
  sum_target1 = { one_char:list(t_target1).count(one_char) for one_char in list(t_common)}
  sum_target2 = { one_char:list(t_target2).count(one_char) for one_char in list(t_common)}
  return {'common':list(t_common), 'str1':sum_target1, 'str2':sum_target2}
