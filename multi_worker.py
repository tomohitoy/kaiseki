# -*- coding: utf-8 -*-
# inspired from http://d.hatena.ne.jp/halhorn/20100904/1283612722

import multiprocessing as mp

class MultiWorker:
    def __init__(self, core_num):
        self.core_num = core_num
    
    def map_calc(self, target_func, args):
        def pipefunc(conn,arg):
            conn.send(target_func(arg))
            conn.close()
        results = []
        k = 0
        while(k < len(args)):
            plist = []
            clist = []
            end = min(k + self.core_num, len(args))
            for arg in args[k:end]:
                pconn, cconn = mp.Pipe()
                plist.append(mp.Process(target = pipefunc, args=(cconn,arg,)))
                clist.append(pconn)
            for p in plist:
                p.start()
            for conn in clist:
                results.append(conn.recv())
            for p in plist:
                p.join()
            k += self.core_num
        return results
