# -*- coding:utf-8 -*-
# Multiprocessingするスクリプト

import sd_scraper as ss
import pymongo as pm
import sys
import time as ti
from selenium import webdriver as wd

# 一段階入れ子になっている配列をフラットな配列にする
# 例： [[1,2,3],[4,5]] => [1,2,3,4,5]
def flatten_list(dirty_list):
    munged_list = []
    for one_list in dirty_list:
        munged_list.extend(one_list)
    return munged_list

# Scriptファイルとして実行される時に，スクレイプが走るようにする
if __name__ == '__main__':
    argvs = sys.argv
    # ジャーナルID（文字列番号）
    journal_id = argvs[1]
    # ジャーナル名（保存用）
    journal_name = argvs[2]
    # 保存するMongoDBのDB名
    dbname = argvs[3]
    # 最小のボリューム数（10の倍数）
    min_vol = int(argvs[4])
    # 最大のボリューム数（10の倍数）
    max_vol = int(argvs[5])
    # ボリューム数を分割する数
    vol_breaks = int(argvs[6])
    
    # スクリプト開始時間をこの時点で記録
    start_time = int(ti.time())
    
    # ログを記録するファイル名を定義
    log_filepath = './log/log_' + journal_name + str(start_time) + '.txt'

    # MongoDBをイニシャライズ
    con = pm.Connection()
    db = con[dbname]
    abstract_collection = db[journal_name+'_abstract' + str(start_time)]
    
    # ブラウザを作る
    browser = wd.PhantomJS()
    browser.set_window_size(1024,768)
    
    # スクレイパークラスからスクレイプツールを作成
    scraper = ss.Scraper(journal_id,log_filepath,abstract_collection,browser)
    
    # 10かたまりのVolume番号からそれぞれのイシューのリンクを取得する
    issue_links = []
    volume_links = ['http://www.sciencedirect.com/science/journal/'+journal_id+'/'+str(volume) for volume in range(min_vol,max_vol+vol_breaks,vol_breaks)]
    for volume_link in volume_links:
        issue_links.append(scraper.get_issue_links(volume_link))
    munged_issue_links = flatten_list(issue_links)
    # ログファイルに記録
    scraper.logging('Finish to get ' + str(len(munged_issue_links))+ ' issue links in ' + journal_name + ' at ' + scraper.get_now())
    
    # Issueのリンクから一つ一つの論文のリンクを取得する
    article_links = []
    for issue_link in munged_issue_links:
        article_links.append(scraper.get_article_links(issue_link))
    
    # ログファイルに記録
    munged_article_links = flatten_list(article_links)
    scraper.logging('Finish to get '+str(len(munged_article_links))+' article links in ' + journal_name + ' at ' + scraper.get_now())
    
    # 論文のリンク一つ一つからアブストラクトをスクレイプして保存する
    abstract_results = []
    for article_link in munged_article_links:
        abstract_results.append(scraper.get_abstract(article_link))
    
    # ログファイルに記録
    scraper.logging('Finish to get ' + str(len(abstract_results)) + ' abstracts in ' + journal_name + ' at ' + scraper.get_now())
    
    browser.quit()
